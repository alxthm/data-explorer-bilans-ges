from dataclasses import dataclass
from holoviews.plotting.util import process_cmap
from typing import Optional, Any

import panel as pn
import pandas as pd
import plotly.express as px

from src.data.make_dataset import DATA_PATH
from src.visualization.visualize import (
    LABELS,
)

import textwrap

# Setting a max_width to Markdown components seems necessary to avoid stretching to the entire screen width.
# For the plots in this page, don't bother with responsive=True, simply set the frame size.

MAX_TEXT_WIDTH = 700
SIZE = dict(frame_height=350, frame_width=600)

# For our plotly treemaps, fix the height, but set the width to be responsive.
#
# When using autosize=True in plotly layout, the pn.Plotly component does not seem to have its height set properly.
# As a workaround we specify it again when creating the pn.Plotly component

PLOTLY_HEIGHT = 700
PLOTLY_OPTS = dict(
    autosize=True,
    height=PLOTLY_HEIGHT,
)

_LABELS_NUNIQUE = {
    "Id": LABELS.n_bilans,
    "SIREN principal": LABELS.n_entites,
}


def df_nunique(df, groupby: str, sort=True):
    x = df.groupby([groupby], as_index=False).nunique().rename(columns=_LABELS_NUNIQUE)
    if sort:
        x = x.sort_values(LABELS.n_bilans, ascending=False)
    return x


def plot_nunique(
    df,
    groupby: str,
    *,
    y=(LABELS.n_bilans, LABELS.n_entites),
    sort=True,
    opts=None,
    rot=90,
):
    x = df_nunique(df, groupby, sort)
    if opts is None:
        opts = dict(multi_level=False)
    x = x.plot(
        x=groupby,
        y=y,
        kind="bar",
        rot=rot,
        **SIZE,
    )
    return x.opts(**opts, shared_axes=False)


def custom_wrap(s, width=20):
    return "<br>".join(textwrap.wrap(s, width=width))


@pn.cache
def get_df():
    df = pd.read_csv(
        DATA_PATH / "processed/bilans-ges-all.csv",
        dtype={"naf2_code": str, "naf3_code": str, "naf4_code": str},
    )
    # remove unnecessary columns for performance and readability
    df = df[[c for c in df.columns if "Emissions" not in c]]

    df.month_publication = pd.to_datetime(df.month_publication)
    df[LABELS.annee_publication] = df.month_publication.dt.year
    return df


@pn.cache
def get_df_ademe():
    x = pd.read_csv(
        DATA_PATH / "raw/rapport-beges-ademe-2022-annexe-1.csv", dtype={"Code NAF": str}
    )
    x["Taux de conformité"] = x["Taux de conformité"].str.rstrip("%").astype(float)
    x = x[["Code NAF", "Nombre d'obligés", "Nombre conforme", "Taux de conformité"]]
    x = x.rename(
        columns={
            "Code NAF": "naf2_code",
            "Taux de conformité": "Taux de conformité (%)",
        }
    )
    return x


@dataclass
class Plot:
    title: str
    widget: Any  # hvplot plot or Panel widget
    description: Optional[str] = None

    @property
    def styles(self):
        # Most widgets have a fixed size and should be put on the same row if there is space -> use fit-content.
        # But plotly widgets have responsive width and are better displayed full-width -> use auto so that they always
        # take the entire row.
        flex_basis = (
            "auto" if isinstance(self.widget, pn.pane.Plotly) else "fit-content"
        )
        return dict(
            styles={
                "flex": f"1 1 {flex_basis}",
                "border": "1px solid WhiteSmoke",
            },
            margin=5,
        )


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
            **SIZE,
        )
        return x.opts(multi_level=False, shared_axes=False)

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
    x = df.rename(columns=_LABELS_NUNIQUE)

    # Compute the reporting year relative to publication year
    x[LABELS.annee_reporting_rel] = (
        x["Année de reporting"] - x[LABELS.annee_publication]
    )

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

    df[LABELS.annee_reporting_rel] = (
        df["Année de reporting"] - df[LABELS.annee_publication]
    )
    x[LABELS.annee_reporting_rel_label] = x[LABELS.annee_reporting_rel].map(label_n)

    # build a custom colormap: the last value is red on purpose, to indicate
    # that '> N' is not a normal value
    n_labels = x[LABELS.annee_reporting_rel_label].nunique()
    cmap = process_cmap("blues", ncolors=n_labels - 1) + ["darkred"]

    def hook(plot, element):
        # fix the legend title, using the underlying bokeh API
        # https://discourse.holoviz.org/t/removing-legend-title/1317/2
        plot.state.legend.title = "Année de reporting"

    x = x.sort_values([LABELS.annee_publication, LABELS.annee_reporting_rel])
    x = x.groupby(
        [LABELS.annee_publication, LABELS.annee_reporting_rel_label], sort=False
    )
    x = x[LABELS.n_bilans].nunique()
    return x.plot(kind="bar", stacked=True, cmap=cmap, **SIZE).opts(hooks=[hook])


def plot_annee_bilan(df):
    x = df.rename(columns=_LABELS_NUNIQUE)
    x = x.rename(
        columns={
            LABELS.annee_publication: "publication",
            "Année de reporting": "reporting",
        }
    )
    x = x.melt(
        id_vars=[LABELS.n_bilans],
        value_vars=["publication", "reporting"],
        var_name="Année de",
        value_name="Année",
    )
    x = x.groupby(["Année", "Année de"])[LABELS.n_bilans].nunique()
    return x.plot(kind="bar", rot=90, **SIZE).opts(multi_level=False)


def plot_mois_publication(df):
    x = df.rename(columns=_LABELS_NUNIQUE)
    x.month_publication = pd.to_datetime(x.month_publication)
    x["month_publication_digit"] = x.month_publication.dt.month
    x["Mois de la publication"] = x.month_publication.dt.month_name("fr_FR.UTF-8")
    x = x.groupby(["month_publication_digit", "Mois de la publication"])
    x = x[LABELS.n_bilans].nunique()
    return x.plot(x="Mois de la publication", kind="bar", **SIZE)


def secteur_activite_n_entites_treemap(df):
    cols = ["naf1", "naf2", "naf3", "naf4"]
    x = (
        df.groupby(cols + ["naf5"], dropna=False)
        .nunique()
        .rename(columns={"SIREN principal": LABELS.n_entites})[LABELS.n_entites]
        .reset_index()
        .fillna("undefined")
    )

    # wrap text so that it is more readable
    for c in cols:
        x[c] = x[c].map(custom_wrap)

    fig = px.treemap(
        x,
        path=[px.Constant("all")] + cols,
        values=LABELS.n_entites,
        hover_name=LABELS.n_entites,
    )
    fig.update_traces(hovertemplate=f"{LABELS.n_entites}: %{{value}}<br><br>%{{label}}")
    fig.update_layout(**PLOTLY_OPTS)
    return pn.pane.Plotly(
        fig,
        height=PLOTLY_HEIGHT,
    )


def secteur_activite_ratio_treemap(df):
    x = df.rename(columns=_LABELS_NUNIQUE)
    x = x.groupby(["naf1", "naf2", "naf2_code"]).nunique()[
        [LABELS.n_bilans, LABELS.n_entites]
    ]
    x = x.reset_index()
    x = pd.merge(x, get_df_ademe(), on="naf2_code", how="left")
    x[LABELS.ratio_n_entites_n_obliges] = x[LABELS.n_entites] / x["Nombre d'obligés"]

    # wrap text so that it is more readable
    cols = ["naf1", "naf2"]
    for c in cols:
        x[c] = x[c].map(custom_wrap)

    fig = px.treemap(
        x,
        path=[px.Constant("all")] + cols,
        values="Nombre d'obligés",
        custom_data=LABELS.n_entites,
        color=LABELS.ratio_n_entites_n_obliges,
        color_continuous_scale="BrBg",
        color_continuous_midpoint=1.0,
        range_color=(0, 2),
    )
    fig.update_traces(
        hovertemplate=f"{LABELS.n_entites}: %{{customdata[0]}}<br>"
        f"Nombre d'obligés: %{{value}}<br>"
        f"{LABELS.ratio_n_entites_n_obliges}: %{{color:.2f}}<br><br>"
        f"%{{label}}"
    )
    fig.update_layout(
        **PLOTLY_OPTS,
        coloraxis_colorbar_orientation="h",
        coloraxis_colorbar_y=-0.15,
    )
    return pn.pane.Plotly(
        fig,
        height=PLOTLY_HEIGHT,
    )


def _get_plots(df):
    return [
        # Qui dépose des bilans GES sur le site de l'ADEME ?
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
        # Quand les bilans sont-ils publiés ?
        Plot(
            title="Répartition des bilans par année",
            widget=plot_annee_bilan(df),
            description="La date de publication correspond à la date à laquelle un bilan GES "
            "est mis en ligne sur le site de l'ADEME.\n"
            "L'année de reporting correspond à l'année pour laquelle les émissions ont été calculées.",
        ),
        Plot(
            title="Répartition des bilans par année",
            widget=plot_annee_publication(df),
            description="Note: pour un tout petit nombre de bilans, l'année de reporting est plus grande "
            "que l'année de publication (`> N`). Peut-être une erreur dans les données sources ?",
        ),
        Plot(
            title="Mois de publication",
            widget=plot_mois_publication(df),
        ),
        # Quels secteurs d'activités ?
        Plot(
            title="Secteur d'activité",
            widget=secteur_activite_n_entites_treemap(df),
            description="Nombre d'entités ayant publié au moins un bilan, par secteur d'activité "
            "([NAF](https://www.insee.fr/fr/information/2120875)).\n"
            "Note: un petit nombre d'entités ont indiqué différents codes NAF d'un bilan à l'autre, dans ce cas là"
            " uniquement le dernier code NAF en date est pris en compte",
        ),
        Plot(
            title="Secteur d'activité",
            widget=secteur_activite_ratio_treemap(df),
            description="""
Ratio du nombre d'entités ayant publié au moins un bilan sur le nombre d'entités "obligées", par secteur.

Notes:

* Le nombre d'entités obligées (c'est à dire, soumises à la réglementation BEGES) est tiré du rapport de l'ADEME: [Evaluation 2021 de la Réglementation des Bilans d'Emissions de Gaz à Effet de Serre](https://librairie.ademe.fr/changement-climatique-et-energie/5919-evaluation-2021-de-la-reglementation-des-bilans-d-emissions-de-gaz-a-effet-de-serre.html), Annexe 1. Ces données sont en principe valables uniquement pour l'année 2021, mais le rapport indique relativement peu de changements d'une année à l'autre.
* La taille des blocs est déterminée par le *nombre d'entités obligées* (et non pas par l'importance du secteur en termes d'émissions par exemple).
""",
        ),
        #     # Quel périmètre pour le bilan GES ?
        #     Plot(
        #         title="Mode de consolidation (opérationnel / financier)",
        #         widget=plot_nunique(df, "Mode de consolidation"),
        #     ),
        #     Plot(
        #         title="Seuil d'importance retenu (%)",
        #         widget=plot_nunique(df, "Seuil d'importance retenu (%)"),
        #         description="Todo: harmoniser ces données (seuil inversé dans certains cas)",
        #     ),
        #     Plot(
        #         title="Méthode BEGES (V4,V5)",
        #         widget=yearly_evolution(df, "Méthode BEGES (V4,V5)"),
        #         description="Parmi les entités ayant publié au moins un bilan, quelle méthode a été utilisée ?",
        #     ),
        #     # Contraintes réglementaires et aides publiques
        #     Plot(
        #         title="Assujetti DPEF/PCAET ?",
        #         widget=yearly_evolution(df, "Assujetti DPEF/PCAET ?"),
        #         description="Parmi les entités ayant publié au moins un bilan, combien sont assujetties au DPEF ou PCAET ?",
        #     ),
        #     Plot(
        #         title="Bilan obligatoire ?",
        #         widget=yearly_evolution(df, "Structure obligée"),
        #         description="Parmi les entités ayant publié au moins un bilan, combien y étaient obligées ?",
        #     ),
        #     Plot(
        #         title="Aide diag décarbon'action",
        #         widget=plot_nunique(df, "Aide diag décarbon'action"),
        #         description="""
        # Pourquoi est-ce vide? car les données s'arrêtent le 28-09-2023 (https://data.ademe.fr/datasets/bilan-ges)
        #
        # Il serait potentiellement faisable de contacter l'ademe et/ou de scrapper le site pour des données plus a jour.
        #
        # En attendant, au 31/03/2024, le site a jour recense 171 bilans utilisant le diag decarbon'action
        #         """,
        #     ),
    ]


def get_profiles_dashboard():
    df = get_df()

    def _get_md(p: Plot):
        txt = f"## {p.title}"
        if p.description:
            txt += f"\n{p.description}"
        return pn.pane.Markdown(
            txt,
            max_width=MAX_TEXT_WIDTH,
        )

    plots = [
        pn.Column(
            _get_md(p),
            p.widget,
            **p.styles
        )
        for p in _get_plots(df)
    ]
    return pn.FlexBox(*plots)
