from src.pages.internal import base as b
from src.visualization.panel_figures.benchmark import get_benchmark_dashboard

template = b.get_template(main=get_benchmark_dashboard(), page='benchmark')
template.servable()
