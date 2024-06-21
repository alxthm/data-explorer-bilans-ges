from src.pages.internal import base as b
from src.visualization.utils import section

template = b.get_template(main=section("about", "sources"), page="about")
template.servable()
