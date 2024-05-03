import numpy as np
import pandas as pd
import panel as pn
import holoviews as hv
from hvplot import hvPlot

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

PLOT_OPTS = dict(frame_height=350, frame_width=600)


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


def _get_hvplot(
    df: pd.DataFrame,
    *,
    secteur_activite: str,
    annee: str,
    mode_consolidation: str,
    plot_col: str,
    group_by: list[str],
):
    # filter plot data
    x = df.copy()
    if secteur_activite != "all":
        x = x[x.naf1 == secteur_activite]
    if mode_consolidation != "all":
        x = x[x["Mode de consolidation"] == mode_consolidation]
    if annee != "all":
        x = x[x["Année de reporting"] == annee]

    if plot_col == "emissions_clipped":
        opts = dict(
            ylabel="tCO2 eq.",
            logx=True,
            **PLOT_OPTS,
        )
    elif plot_col == "emissions_par_salarie":
        # compute the upper bound of all whisker plots
        upper = 1.0
        for sub_poste in x[group_by[-1]].unique():
            if sub_poste is None:
                continue
            y = x[(x[group_by[-1]] == sub_poste) & ~pd.isna(x.emissions_par_salarie)]
            upper = max(upper, _get_upper_bar(y.emissions_par_salarie.values))

        opts = dict(
            ylabel="tCO2 eq. / salarié",
            ylim=(-1.0, upper + 1.0),
            **PLOT_OPTS,
        )
    else:
        raise ValueError(f"Invalid {plot_col=}")

    return (
        hvPlot(x)
        .box(
            by=group_by,
            y=plot_col,
            fields={"naf1": {"default": "all"}},
            # Not sure the difference between this and ylim, in both cases it does not seem to reset the axes
            # when replotting (only the last max value is taken into account)
            # ).redim(
            #    emissions_par_salarie=hv.Dimension('emissions_par_salarie', range=(-1., upper + 1.))
        )
        .opts(title=f"n_bilans={x.Id.nunique()}", invert_axes=True, **opts)
    )


class LABELS:
    n_salaries = "Nb. salariés ou agents"
    n_bilans = "Nb. bilans déposés"
    n_entites = "Nb. entités ayant déposé\n au moins un bilan"


_LABELS_NUNIQUE = {
    "Id": LABELS.n_bilans,
    "SIREN principal": LABELS.n_entites,
}


def df_nunique(df, groupby: str, sort=True):
    x = df.groupby([groupby], as_index=False).nunique().rename(columns=_LABELS_NUNIQUE)
    if sort:
        x = x.sort_values(LABELS.n_bilans, ascending=False)
    return x


def plot_nunique(df, groupby: str, sort=True, opts=None, rot=90):
    x = df_nunique(df, groupby, sort)
    if opts is None:
        opts = dict(multi_level=False, **PLOT_OPTS)
    x = x.plot(
        x=groupby,
        y=[LABELS.n_bilans, LABELS.n_entites],
        kind="bar",
        rot=rot,
    )
    return x.opts(**opts, shared_axes=False)


def yearly_evolution(_df, col, opts=None):
    if opts is None:
        opts = dict(multi_level=False, **PLOT_OPTS)

    x = _df.groupby(["Année de reporting", col], as_index=False)
    x = (
        x["SIREN principal"]
        .nunique()
        .rename(columns={"SIREN principal": LABELS.n_entites})
        .pivot(
            columns=col,
            index="Année de reporting",
            values=LABELS.n_entites,
        )
    )
    return x.plot(kind="bar", rot=90).opts(**opts, shared_axes=False)
