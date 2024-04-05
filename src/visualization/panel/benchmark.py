from src.visualization.visualize import select_widget
import panel as pn

import pandas as pd

from src.data.make_dataset import DATA_PATH
from src.visualization.visualize import _get_hvplot


@pn.cache
def get_df():
    return pd.read_csv(DATA_PATH / "processed/bilans-ges-benchmark.csv")


def get_benchmark_dashboard():
    df = get_df()

    plot_col = pn.widgets.Select(
        name="Indicateur", options=["emissions_par_salarie", "emissions_clipped"]
    )
    mode_consolidation = select_widget(df, "Mode de consolidation")
    annee = select_widget(df, "Année de reporting", sort=True)

    plot_by_secteur_activite = pn.bind(
        lambda **kw: _get_hvplot(df, group_by=["naf1"], secteur_activite="all", **kw),
        annee=annee,
        mode_consolidation=mode_consolidation,
        plot_col=plot_col,
    )

    secteur_activite = select_widget(df, "naf1", "Secteur d'activité")
    plot_by_poste_emission = pn.bind(
        lambda **kw: _get_hvplot(df, group_by=["poste_name", "sub_poste_name"], **kw),
        secteur_activite=secteur_activite,
        annee=annee,
        mode_consolidation=mode_consolidation,
        plot_col=plot_col,
    )

    benchmark = pn.Row(
        pn.WidgetBox(plot_col, mode_consolidation, annee, margin=10),
        pn.Column(
            pn.Column(
                "## Émissions totales, par secteur d'activité",
                plot_by_secteur_activite,
            ),
            pn.Column(
                "## Postes d'émissions", secteur_activite, plot_by_poste_emission
            ),
        ),
    )
    return benchmark
