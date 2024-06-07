from pathlib import Path

import panel as pn
from typing import Literal


_SRC_PATH = Path(__file__).resolve().parent


def section(name: str, extension: Literal["md", "html"] = "md"):
    content = (_SRC_PATH / f"pages/{name}.{extension}").read_text()
    if extension == "md":
        return pn.pane.Markdown(content)
    elif extension == "html":
        return pn.pane.HTML(content)
