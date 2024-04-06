from pathlib import Path

import panel as pn

from src.visualization.panel.benchmark import get_benchmark_dashboard
from src.visualization.panel.profiles import get_profiles_dashboard

_SRC_PATH = Path(__file__).resolve().parent

pn.extension("plotly")

template = pn.Template(
    """
{% extends base %}
{% block postamble %}
    <script defer data-domain="alxthm-data-explorer-bilans-ges-ademe.hf.space" src="https://plausible.io/js/script.js"></script>
{% endblock %}
    """
)


def _markdown(name: str):
    md_file = _SRC_PATH / f"visualization/markdown/{name}.md"
    return pn.pane.Markdown(md_file.read_text())


benchmark = get_benchmark_dashboard()
profiles = get_profiles_dashboard()

main = pn.Column(
    _markdown("header"),
    pn.Tabs(
        ("Benchmark Émissions", benchmark),
        ("Profil des entreprises", profiles),
        ("À propos", _markdown("about")),
    ),
)

template.add_panel("main", main)
template.servable(title="Data Explorer - Bilans GES ADEME")
