import panel as pn

from src.visualization.panel_figures.benchmark import get_benchmark_dashboard
from src.visualization.panel_figures.profiles import get_profiles_dashboard
from src.visualization.utils import section

pn.extension("plotly", defer_load=True, loading_indicator=True)

# Load the custom CSS: increase app font size
pn.config.raw_css.append("""
:host {
    --bokeh-font-size: 1em;
}
""")

template = pn.Template(
    """
{% extends base %}
{% block postamble %}
{% endblock %}
    """
)

benchmark = get_benchmark_dashboard()
profiles = get_profiles_dashboard()

main = pn.Column(
    section("header"),
    pn.Tabs(
        ("Benchmark Émissions", benchmark),
        ("Profil des entreprises et des bilans publiés", profiles),
        ("À propos", section("about")),
    ),
)

template.add_panel("main", main)
template.servable(title="Data Explorer - Bilans GES ADEME")
