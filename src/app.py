import panel as pn

from src.visualization.panel_figures.benchmark import get_benchmark_dashboard
from src.visualization.panel_figures.profiles import get_profiles_dashboard
from src.visualization.utils import section

pn.extension("plotly")

template = pn.Template(
    """
{% extends base %}
{% block postamble %}
    <script defer data-domain="alxthm-data-explorer-bilans-ges-ademe.hf.space" src="https://plausible.io/js/script.js"></script>
{% endblock %}
    """
)

benchmark = get_benchmark_dashboard()
profiles = get_profiles_dashboard()

main = pn.Column(
    section("header"),
    pn.Tabs(
        ("Benchmark Émissions", benchmark),
        ("Profil des entreprises", profiles),
        ("À propos", section("about")),
    ),
)

template.add_panel("main", main)
template.servable(title="Data Explorer - Bilans GES ADEME")
