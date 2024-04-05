from dataclasses import dataclass
from typing import Callable, Optional

import panel as pn
import pandas as pd
import plotly.express as px

from src.data.make_dataset import DATA_PATH
from src.visualization.visualize import PLOT_OPTS, plot_nunique, yearly_evolution


@pn.cache
def get_df():
    df = pd.read_csv(DATA_PATH / "processed/bilans-ges-all.csv")
    # remove unnecessary columns for performance and readability
    df = df[[c for c in df.columns if "Emissions" not in c]]
    return df


@dataclass
class Plot:
    title: str
    plot_fn: Callable
    description: Optional[str] = None


def _taille_entreprises(df):
    x = df.groupby(["nb_salaries_range", "nb_salaries_min"], as_index=False).nunique()
    x = x.sort_values(by="nb_salaries_min")
    x = x.plot(x="nb_salaries_range", y=["Id", "SIREN principal"], kind="bar", rot=90)
    return x.opts(multi_level=False, **PLOT_OPTS, shared_axes=False)


def _date_publication(df):
    x = df.groupby(["month_publication"])[["Id", "SIREN principal"]].nunique().cumsum()
    return x.plot().opts(shared_axes=False)


def _secteur_activite_treemap(df):
    x = (
        df.groupby(["naf1", "naf2", "naf3", "naf4", "naf5"])["SIREN principal"]
        .nunique()
        .reset_index()
    )
    x = x.rename(columns={"SIREN principal": "Nombre_Entites"})
    x["all"] = "all"  # in order to have a single root node
    fig = px.treemap(
        x,
        path=["all", "naf1", "naf2", "naf3", "naf4"],
        values="Nombre_Entites",
        hover_name="Nombre_Entites",
    )
    return pn.pane.Plotly(fig)


_PLOTS = [
    Plot(
        title="Taille des entreprises",
        plot_fn=_taille_entreprises,
        description="Certaines entreprises ont plusieurs bilans, ce qui explique pourquoi Id est plus grand",
    ),
    Plot(
        title="Année de reporting",
        plot_fn=lambda df: plot_nunique(df, "Année de reporting", sort=False),
    ),
    Plot(
        title="Date de publication",
        plot_fn=_date_publication,
    ),
    Plot(
        title="Type de structure",
        plot_fn=lambda df: plot_nunique(df, "Type de structure"),
    ),
    Plot(
        title="Mode de consolidation (opérationnel / financier)",
        plot_fn=lambda df: plot_nunique(df, "Mode de consolidation"),
    ),
    Plot(
        title="Secteur d'activité",
        plot_fn=_secteur_activite_treemap,
        description="Nombre d'entités ayant publié au moins un bilan, par secteur d'activité",
    ),
    Plot(
        title="Seuil d'importance retenu (%)",
        plot_fn=lambda df: plot_nunique(df, "Seuil d'importance retenu (%)"),
        description="Todo: harmoniser ces données (seuil inversé dans certains cas)",
    ),
    Plot(
        title="Aide diag décarbon'action",
        plot_fn=lambda df: plot_nunique(df, "Aide diag décarbon'action"),
        description="""
Pourquoi est-ce vide? car les données s'arrêtent le 28-09-2023 (https://data.ademe.fr/datasets/bilan-ges)

Il serait potentiellement faisable de contacter l'ademe et/ou de scrapper le site pour des données plus a jour.

En attendant, au 31/03/2024, le site a jour recense 171 bilans utilisant le diag decarbon'action
        """,
    ),
    Plot(
        title="Assujetti DPEF/PCAET ?",
        plot_fn=lambda df: yearly_evolution(df, "Assujetti DPEF/PCAET ?"),
        description="Parmi les entités ayant publié au moins un bilan, combien sont assujetties au DPEF ou PCAET ?",
    ),
    Plot(
        title="Bilan obligatoire ?",
        plot_fn=lambda df: yearly_evolution(df, "Structure obligée"),
        description="Parmi les entités ayant publié au moins un bilan, combien y étaient obligées ?",
    ),
    Plot(
        title="Méthode BEGES (V4,V5)",
        plot_fn=lambda df: yearly_evolution(df, "Méthode BEGES (V4,V5)"),
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

    plots = [(_get_md(p), p.plot_fn(df), pn.layout.Divider()) for p in _PLOTS]
    plots = [i for tup in plots for i in tup]  # flatten list

    return pn.Column(
        pn.pane.Markdown("""
        * Id: nombre de submissions
        * SIREN principal: nombre d'entreprises ayant fait au moins une submission
        """),
        *plots,
    )
