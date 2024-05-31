import holoviews as hv
import pandas as pd
import panel as pn
import param
from bokeh.models import Range1d, LinearAxis
from panel.widgets import MultiChoice

from src.data.make_dataset import DATA_PATH
from src.visualization.visualize import (
    _get_upper_bar,
    PLOT_OPTS,
    LABELS,
)


@pn.cache
def get_df() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH / "processed/bilans-ges-benchmark.csv")
    df = df.rename(
        columns={
            "naf1": LABELS.secteur_activite,
            "poste_name": LABELS.category_emissions,
            "sub_poste_name": LABELS.poste_emissions,
            "emissions_par_salarie": LABELS.emissions_par_salarie,
            "emissions_clipped": LABELS.emissions_total,
        }
    )
    return df


def get_multi_choice(df: pd.DataFrame, col: str, name=None, sort=False):
    options = df[col].unique().tolist()
    if sort:
        options = sorted(options)

    # for each choice of options, a different class is needed (because options are shared class-wise)
    class MultiChoiceWithAll(param.Parameterized):
        select_all = param.Boolean(default=True, label="All")
        selected_options = param.ListSelector(
            default=[], objects=options, precedence=-1, label=""
        )

        @param.depends("select_all", watch=True)
        def _update_options(self):
            if self.select_all:
                self.param.selected_options.precedence = -1
            else:
                self.param.selected_options.precedence = 1

        def widget(self):
            return pn.Param(self, widgets={"selected_options": MultiChoice})

    return MultiChoiceWithAll(name=name or col)


filters = dict(
    type_structure=dict(col="Type de structure"),
    secteur_activite=dict(col=LABELS.secteur_activite),
    categorie_emissions=dict(col=LABELS.category_emissions),
    poste_emissions=dict(col=LABELS.poste_emissions),
    annee=dict(col="Année de reporting", sort=True),
    mode_consolidation=dict(col="Mode de consolidation"),
)


def get_benchmark_dashboard():
    df = get_df()

    plot_col = pn.widgets.Select(
        name="Indicateur",
        options=[LABELS.emissions_par_salarie, LABELS.emissions_total],
    )
    widgets = {key: get_multi_choice(df, **kw) for key, kw in filters.items()}
    # nested parameters don't seem to work well, so we pass all options directly as kwarg
    kwargs = dict(
        **{f"{k}_all": w.param.select_all for k, w in widgets.items()},
        **{f"{k}_options": w.param.selected_options for k, w in widgets.items()},
    )

    data = pn.bind(filter_options, df=df, secteur_activite="all", **kwargs)
    plot_by_secteur_activite = pn.bind(
        plot_emissions_par_secteur,
        df=data,
        plot_col=plot_col,
    )

    return pn.Row(
        pn.WidgetBox(
            plot_col,
            *(w.widget() for w in widgets.values()),
            margin=10,
        ),
        plot_by_secteur_activite,
    )


def filter_options(
    df: pd.DataFrame,
    *,
    secteur_activite: str,
    **kwargs,
):
    x = df.copy()

    if secteur_activite != "all":
        x = x[x[LABELS.secteur_activite] == secteur_activite]

    for key, opts in filters.items():
        select_all: bool = kwargs[f"{key}_all"]
        selected_options: list[str] = kwargs[f"{key}_options"]
        col_name = opts["col"]
        if not select_all:
            x = x[x[col_name].isin(selected_options)]

    # drop nan values and zeros
    x = x.fillna(0)
    x = x[x != 0]

    return x


def plot_emissions_par_secteur(
    df: pd.DataFrame,
    *,
    plot_col: str,
):
    x = df.copy()
    group_by = LABELS.poste_emissions

    box = x.plot(
        kind="box",
        # Note: it would be possible here to pass `by=[LABELS.categorie_emissions, LABELS.poste_emissions]`
        # in order to group postes by category (with a multi-level index). But this does not work when combining
        # with a regular scatter plot.
        by=group_by,
        y=plot_col,
        # fields={"naf1": {"default": "all"}},
        # hover_cols="all",
    )

    match plot_col:
        case LABELS.emissions_par_salarie:
            box_opts = dict(
                ylabel="tCO2 eq. / salarié",
                ylim=(0, _boxwhisker_upper_bound(x) + 1.0),
            )
        case LABELS.emissions_total:
            box_opts = dict(
                ylabel="tCO2 eq.",
                logx=True,
            )
        case _:
            raise ValueError(plot_col)

    y = get_valid_postes_percentage(x, group_by=group_by)
    scatter = y.plot(
        kind="scatter",
        y="Part de bilans incluant le poste d'émissions (%)",
        # display all the data (absolute nb. in addition of the %) in the hover toolbox
        hover_cols="all",
    )

    return (box * scatter).opts(
        hv.opts(
            title=f"n_bilans={x.Id.nunique()}",
            invert_axes=True,
            **PLOT_OPTS,
            multi_y=False,
        ),
        # active_tools=['ywheel_zoom'],
        hv.opts.BoxWhisker(**box_opts, show_legend=False),
        hv.opts.Scatter(
            ylim=(0, None), color="red", marker="x", size=10, hooks=[plot_secondary]
        ),
    )


# Helper functions


def plot_secondary(plot, element):
    """
    Hook to plot data on a secondary (twin) axis on a Holoviews Plot with Bokeh backend.
    More info:
    - http://holoviews.org/user_guide/Customizing_Plots.html#plot-hooks
    - https://docs.bokeh.org/en/latest/docs/user_guide/plotting.html#twin-axes

    Necessary because multi_index does not work with invert_axes=True, or with the rot option
    """
    fig = plot.state
    glyph_first = fig.renderers[0]  # will be the original plot
    glyph_last = fig.renderers[-1]  # will be the new plot
    right_axis_name = "twiny"
    # Create both axes if right axis does not exist
    if right_axis_name not in fig.extra_x_ranges.keys():
        # Recreate primary axis (left)
        # y_first_name = glyph_first.glyph.y
        # y_first_min = glyph_first.data_source.data[y_first_name].min()
        # y_first_max = glyph_first.data_source.data[y_first_name].max()
        # y_first_offset = (y_first_max - y_first_min) * 0.1
        # fig.y_range = Range1d(
        #    start=y_first_min - y_first_offset,
        #    end=y_first_max + y_first_offset
        # )
        # fig.y_range.name = glyph_first.y_range_name
        # Create secondary axis (right)

        # replace all y by x if inverted (and right -> below)
        y_last_name = glyph_last.glyph.x
        y_last_min = glyph_last.data_source.data[y_last_name].min()
        y_last_max = glyph_last.data_source.data[y_last_name].max()
        y_last_offset = (y_last_max - y_last_min) * 0.1
        fig.extra_x_ranges = {
            right_axis_name: Range1d(start=0, end=y_last_max + y_last_offset)
        }
        fig.add_layout(
            LinearAxis(x_range_name=right_axis_name, axis_label=glyph_last.glyph.x),
            "below",
        )
    # Set right axis for the last glyph added to the figure
    glyph_last.x_range_name = right_axis_name


def get_valid_postes_percentage(df, group_by: str):
    n_bilans = df["Id"].nunique()

    # there can be NaN or 0 values: we consider both as empty data
    x = (
        df.groupby(group_by)
        .emissions.agg(lambda i: i.ne(0, fill_value=0).sum())
        .rename("Nb. de bilans incluant le poste d'émissions")
    )
    x = x.to_frame()
    x["Part de bilans incluant le poste d'émissions (%)"] = (
        x["Nb. de bilans incluant le poste d'émissions"] / n_bilans * 100
    )
    return x


def _boxwhisker_upper_bound(x):
    # compute the upper bound of all whisker plots
    upper = 1.0
    for sub_poste in x[LABELS.poste_emissions].unique():
        if sub_poste is None:
            continue
        y = x[
            (x[LABELS.poste_emissions] == sub_poste)
            & ~pd.isna(x[LABELS.emissions_par_salarie])
        ]
        upper = max(upper, _get_upper_bar(y[LABELS.emissions_par_salarie].values))
    return upper
