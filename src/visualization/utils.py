from pathlib import Path

import panel as pn
from typing import Literal

_SRC_PATH = Path(__file__).resolve().parent


def section(*names: str, extension: Literal["md", "html"] = "md"):
    content = "\n".join(
        (_SRC_PATH / f"text/{name}.{extension}").read_text() for name in names
    )
    opts = dict(margin=20)
    if extension == "md":
        return pn.pane.Markdown(content, **opts)
    elif extension == "html":
        return pn.pane.HTML(content, **opts)
