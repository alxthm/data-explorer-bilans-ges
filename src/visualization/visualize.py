import numpy as np
import pandas as pd
import panel as pn
from hvplot import hvPlot

_OPTS = dict(frame_height=350, frame_width=600)


def select_widget(
    df: pd.DataFrame, col: str, name=None, sort=False, widget=pn.widgets.Select
):
    """Construct a panel widget from the df[col] unique values"""
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
            **_OPTS,
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
            **_OPTS,
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
