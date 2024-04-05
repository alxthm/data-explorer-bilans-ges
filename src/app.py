from pathlib import Path

import pandas as pd
import panel as pn

from src.data.make_dataset import DATA_PATH
from src.visualization.visualize import select_widget, _get_hvplot

_SRC_PATH = Path(__file__).resolve().parent

pn.extension()


@pn.cache
def get_df():
    return pd.read_csv(DATA_PATH / "processed/bilans-ges-benchmark.csv")


def _markdown(name: str):
    md_file = _SRC_PATH / f"visualization/markdown/{name}.md"
    return pn.pane.Markdown(md_file.read_text())


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
        pn.Column("## Postes d'émissions", secteur_activite, plot_by_poste_emission),
    ),
)

pane = pn.Column(
    _markdown("header"),
    pn.Tabs(
        ("Benchmark Émissions", benchmark),
        ("À propos", _markdown("about")),
    ),
)

pane.servable()
