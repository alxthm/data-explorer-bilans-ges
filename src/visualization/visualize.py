import numpy as np
import pandas as pd
import panel as pn
import holoviews as hv

import hvplot.pandas  # noqa

# make df.plot return a hvPlot
pd.options.plotting.backend = "holoviews"


def disable_logo(plot, element):
    plot.state.toolbar.logo = None


# Remove bokeh logo https://stackoverflow.com/a/47586547/12662410
hv.plotting.bokeh.ElementPlot.hooks.append(disable_logo)

# Disable mouse wheel zoom by default
hv.plotting.bokeh.element.ElementPlot.active_tools = ["box_zoom"]


def _patched_get_data(*args, **kwargs):
    data, mapping, style = _original_get_data(*args, **kwargs)
    mapping["circle_1"]["radius"] = 0.01
    return data, mapping, style


# apply https://github.com/holoviz/holoviews/pull/6169/files temporarily
_original_get_data = hv.plotting.bokeh.stats.BoxWhiskerPlot.get_data
hv.plotting.bokeh.stats.BoxWhiskerPlot.get_data = _patched_get_data


def select_widget(
    df: pd.DataFrame, col: str, name=None, sort=False, widget=pn.widgets.Select
):
    """Construct a panel_figures widget from the df[col] unique values"""
    options = df[col].unique().tolist()
    if None in options:
        options.remove(None)
    if sort:
        options = sorted(options)
    return widget(
        name=name or col,
        options=["all"] + options,
    )


def _get_upper_bar(vals: np.ndarray):
    # compute the upper bar of the whisker plot (above which outliers are drawn as points)
    # https://github.com/holoviz/holoviews/blob/0eeb0fc4d6ff977475b23d798262886372db0b87/holoviews/plotting/bokeh/stats.py#L137
    if len(vals) == 0:
        return -1
    q1, q3 = (np.percentile(vals, q=q) for q in (25, 75))
    iqr = q3 - q1
    upper = max(vals[vals <= q3 + 1.5 * iqr].max(), q3)
    return upper


class LABELS:
    n_salaries = "Nb. salariés ou agents"
    n_bilans = "Nb. bilans déposés"
    n_entites = "Nb. entités ayant déposé\nau moins un bilan"
    annee_publication = "Année de publication"
    annee_reporting_rel = "Année de reporting (relative, digit)"
    annee_reporting_rel_label = "Année de reporting (relative)"
    ratio_n_entites_n_obliges = "Ratio nb. entités / nb. obligés"
    type_structure = "Type de structure"
    secteur_activite = "Secteur d'activité (NAF1)"
    category_emissions = "Catégorie d'émissions"
    poste_emissions = "Poste d'émissions"
    emissions_par_salarie = "Émission_par_salarié"
    emissions_total = "Émissions_totales"
