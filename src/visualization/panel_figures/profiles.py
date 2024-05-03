from dataclasses import dataclass
from holoviews.plotting.util import process_cmap
from typing import Optional, Any

import panel as pn
import pandas as pd
import plotly.express as px

from src.data.make_dataset import DATA_PATH
from src.visualization.visualize import (
    PLOT_OPTS,
    plot_nunique,
    yearly_evolution,
    _LABELS_NUNIQUE,
    LABELS,
)


@pn.cache
def get_df():
    df = pd.read_csv(DATA_PATH / "processed/bilans-ges-all.csv")
    # remove unnecessary columns for performance and readability
    df = df[[c for c in df.columns if "Emissions" not in c]]
    return df


@dataclass
class Plot:
    title: str
    widget: Any  # hvplot plot or Panel widget
    description: Optional[str] = None


def plot_type_structure(df):
    return plot_nunique(df, "Type de structure", rot=45)


class TailleEntreprise:
    def __init__(self, df):
        self.df = df

    def _intermediate_df(self, type_structure):
        x = self.df
        if type_structure != "all":
            x = x[x["Type de structure"] == type_structure]
        # We want to keep the rows where nb_salaries_range is nan, rather than drop them !
        # (it's more explicit)
        x = (
            x.groupby(
                ["nb_salaries_range", "nb_salaries_min"], as_index=False, dropna=False
            )
            .nunique()
            .rename(columns=_LABELS_NUNIQUE)
            .rename(columns={"nb_salaries_range": LABELS.n_salaries})
            .sort_values(by="nb_salaries_min")
        )
        return x

    def plot(self, type_structure):
        x = self._intermediate_df(type_structure)
        x = x.plot(
            x=LABELS.n_salaries,
            y=LABELS.n_bilans,
            kind="bar",
            rot=90,
        )
        return x.opts(multi_level=False, **PLOT_OPTS, shared_axes=False)

    def widget(self):
        type_structure_widget = pn.widgets.Select(
            name="Type de structure",
            options=["all"] + self.df["Type de structure"].unique().tolist(),
        )
        return pn.Column(
            type_structure_widget,
            pn.bind(self.plot, type_structure=type_structure_widget),
        )

    def _numbers(self):
        x = self._intermediate_df(type_structure="Entreprise")
        n_total = x[LABELS.n_bilans].sum()
        n_500_or_more = x.loc[x.nb_salaries_min >= 500, LABELS.n_bilans].sum()
        n_less_than_500 = x.loc[x.nb_salaries_min < 500, LABELS.n_bilans].sum()
        n_nan = x.loc[x.nb_salaries_min.isna(), LABELS.n_bilans].sum()
        return n_total, n_500_or_more, n_less_than_500, n_nan

    def description(self):
        n_total, n, _, _ = self._numbers()
        return (
            f"Parmi les {n_total} bilans GES déposés par des entreprises, {n} ont été déposés par des entreprises "
            f"de 500 employés ou plus ({100 * n / n_total:.1f}%).\n"
        )


def plot_annee_publication(df):
    class L:
        annee_publication = "Année de publication"
        annee_reporting_rel = "Année de reporting (relative, digit)"
        annee_reporting_rel_label = "Année de reporting (relative)"

    # Compute the reporting year relative to publication year
    x = df.rename(columns=_LABELS_NUNIQUE)
    x.month_publication = pd.to_datetime(x.month_publication)
    x[L.annee_publication] = x.month_publication.dt.year
    x[L.annee_reporting_rel] = x["Année de reporting"] - x[L.annee_publication]

    # Get a nice label for that
    def label_n(n):
        if n == 0:
            return "N"
        if n > 0:
            # strangely, some publications report data for years in the future
            return "> N"
        if n <= -5:
            # some go far in the past (N-11), regroup everything to be less spammy
            return "< N-5"
        return f"N-{abs(n)}"

    x[L.annee_reporting_rel_label] = x[L.annee_reporting_rel].map(label_n)

    # build a custom colormap: the last value is red on purpose, to indicate
    # that '> N' is not a normal value
    n_labels = x[L.annee_reporting_rel_label].nunique()
    cmap = process_cmap("blues", ncolors=n_labels - 1) + ["darkred"]

    def hook(plot, element):
        # fix the legend title, using the underlying bokeh API
        # https://discourse.holoviz.org/t/removing-legend-title/1317/2
        plot.state.legend.title = "Année de reporting"

    x = x.sort_values([L.annee_publication, L.annee_reporting_rel])
    x = x.groupby([L.annee_publication, L.annee_reporting_rel_label], sort=False)
    x = x[LABELS.n_bilans].nunique()
    return x.plot(kind="bar", stacked=True, cmap=cmap).opts(**PLOT_OPTS, hooks=[hook])


def plot_mois_publication(df):
    x = df.rename(columns=_LABELS_NUNIQUE)
    x.month_publication = pd.to_datetime(x.month_publication)
    x["month_publication_digit"] = x.month_publication.dt.month
    x["Mois de la publication"] = x.month_publication.dt.month_name("fr_FR.UTF-8")
    x = x.groupby(["month_publication_digit", "Mois de la publication"])
    x = x[LABELS.n_bilans].nunique()
    return x.plot(x="Mois de la publication", kind="bar").opts(**PLOT_OPTS)


def _secteur_activite_treemap(df):
    x = (
        df.groupby(["naf1", "naf2", "naf3", "naf4", "naf5"])
        .nunique()
        .rename(columns={"SIREN principal": LABELS.n_entites})[LABELS.n_entites]
        .reset_index()
    )
    x["all"] = "all"  # in order to have a single root node
    fig = px.treemap(
        x,
        path=["all", "naf1", "naf2", "naf3", "naf4"],
        values=LABELS.n_entites,
        hover_name=LABELS.n_entites,
    )
    return pn.pane.Plotly(fig)


def _get_plots(df):
    return [
        Plot(
            title="Type de structure",
            widget=plot_type_structure(df),
            description="Différentes entités peuvent déposer des bilans GES sur le site de l'ADEME: entreprises, mais"
            " également organismes publics ou associations. Chaque entité est identifiée par son"
            " [numéro SIREN](https://www.insee.fr/fr/metadonnees/definition/c2047).",
        ),
        Plot(
            title="Taille des entités",
            widget=TailleEntreprise(df).widget(),
            description=TailleEntreprise(df).description(),
        ),
        Plot(
            title="Année de publication",
            widget=plot_annee_publication(df),
            description="La date de publication correspond à la date à laquelle un bilan GES "
            "est mis en ligne sur le site de l'ADEME.\n"
            "L'année de reporting correspond à l'année pour laquelle les émissions ont été calculées.\n\n"
            "> Note: pour un tout petit nombre de bilans, l'année de reporting est plus grande que l'année de "
            "publication (`> N`), ce qui pourrait être une erreur.",
        ),
        Plot(
            title="Mois de publication",
            widget=plot_mois_publication(df),
        ),
        Plot(
            title="Mode de consolidation (opérationnel / financier)",
            widget=plot_nunique(df, "Mode de consolidation"),
        ),
        Plot(
            title="Secteur d'activité",
            widget=_secteur_activite_treemap(df),
            description="Nombre d'entités ayant publié au moins un bilan, par secteur d'activité",
        ),
        Plot(
            title="Seuil d'importance retenu (%)",
            widget=plot_nunique(df, "Seuil d'importance retenu (%)"),
            description="Todo: harmoniser ces données (seuil inversé dans certains cas)",
        ),
        Plot(
            title="Aide diag décarbon'action",
            widget=plot_nunique(df, "Aide diag décarbon'action"),
            description="""
    Pourquoi est-ce vide? car les données s'arrêtent le 28-09-2023 (https://data.ademe.fr/datasets/bilan-ges)
    
    Il serait potentiellement faisable de contacter l'ademe et/ou de scrapper le site pour des données plus a jour.
    
    En attendant, au 31/03/2024, le site a jour recense 171 bilans utilisant le diag decarbon'action
            """,
        ),
        Plot(
            title="Assujetti DPEF/PCAET ?",
            widget=yearly_evolution(df, "Assujetti DPEF/PCAET ?"),
            description="Parmi les entités ayant publié au moins un bilan, combien sont assujetties au DPEF ou PCAET ?",
        ),
        Plot(
            title="Bilan obligatoire ?",
            widget=yearly_evolution(df, "Structure obligée"),
            description="Parmi les entités ayant publié au moins un bilan, combien y étaient obligées ?",
        ),
        Plot(
            title="Méthode BEGES (V4,V5)",
            widget=yearly_evolution(df, "Méthode BEGES (V4,V5)"),
            description="Parmi les entités ayant publié au moins un bilan, quelle méthode a été utilisée ?",
        ),
    ]


def get_profiles_dashboard():
    df = get_df()

    def _get_md(p: Plot):
        txt = f"## {p.title}"
        if p.description:
            txt += f"\n{p.description}"
        return pn.pane.Markdown(txt)

    plots = [(_get_md(p), p.widget, pn.layout.Divider()) for p in _get_plots(df)]
    plots = [i for tup in plots for i in tup]  # flatten list

    return pn.Column(
        pn.pane.Markdown("""
        """),
        *plots,
    )
