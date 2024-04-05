from pathlib import Path

import panel as pn

from src.visualization.panel.benchmark import get_benchmark_dashboard
from src.visualization.panel.profiles import get_profiles_dashboard

_SRC_PATH = Path(__file__).resolve().parent

pn.extension('plotly')


def _markdown(name: str):
    md_file = _SRC_PATH / f"visualization/markdown/{name}.md"
    return pn.pane.Markdown(md_file.read_text())


benchmark = get_benchmark_dashboard()
profiles = get_profiles_dashboard()

pane = pn.Column(
    _markdown("header"),
    pn.Tabs(
        ("Benchmark Émissions", benchmark),
        ("Profil des entreprises", profiles),
        ("À propos", _markdown("about")),
    ),
)

pane.servable(title='Data Explorer - Bilans GES ADEME')
