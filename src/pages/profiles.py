from src.pages.internal import base as b
from src.visualization.panel_figures.profiles import get_profiles_dashboard

template = b.get_template(main=get_profiles_dashboard(), page='profiles')
template.servable()
