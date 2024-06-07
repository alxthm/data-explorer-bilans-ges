import pandas as pd
import panel as pn
import param
from panel.widgets import MultiChoice

from src.data.make_dataset import DATA_PATH
from src.visualization.utils import section
from src.visualization.visualize import (
    _get_upper_bar,
    LABELS,
)

# -- Notes on flex-box and responsive sizing
#
# Adding `responsive=True` to hvplot options is required for the plot to shrink/grow according to min_width and
# max_width (otherwise it just has a constant width).
# (Also, these responsive and aspect options need to be passed to the .plot() function, not in .opts():
# https://github.com/holoviz/hvplot/issues/350#issuecomment-619015585).
#
# Also note that the frame_height / frame_width hvplot options, although nice to set the size of the inside plot (no
# matter the size of the legend and axes), is not responsive.
#
# To work inside a flexbox, the `flex` styles option of panel widgets (e.g. Column) need to be set accordingly.
#   `flex: <flex-grow> <flex-shrink> <flex-basis>`
#
# * `flex-basis` sets the size of the item before shrinking/growing is applied
#   * `auto` uses the "value of the width" (?). In practice, for responsive hvplot widgets, it stretches the width to
#     fill the screen, which we don't want.
#   * `max-content` means "intrinsic preferred width". In practice, for responsive hvplot widgets, it seems identical
#     to `min-content` and `fit-content`, and seems to use the max_width, which is what we want.
# * `flex-grow` indicates how much free space should the item take (in the primary direction).
# * `flex-shrink` indicates how much negative free space should the item take.

SIZE = dict(
    responsive=True,
    height=450,
    min_width=750,
    max_width=1100,
)
STYLES = {
    "border": "1px solid WhiteSmoke",
}


@pn.cache
def get_df() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH / "processed/bilans-ges-benchmark.csv")
    df = df.rename(
        columns={
            "naf1": LABELS.secteur_activite,
            "poste_name": LABELS.category_emissions,
            "sub_poste_name": LABELS.poste_emissions,
            "emissions_par_salarie": LABELS.emissions_par_salarie,
            "emissions": LABELS.emissions_total,
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


FILTERS = dict(
    type_structure=dict(col=LABELS.type_structure),
    secteur_activite=dict(col=LABELS.secteur_activite),
    category_emissions=dict(col=LABELS.category_emissions),
    poste_emissions=dict(col=LABELS.poste_emissions),
    annee=dict(col="Année de reporting", sort=True),
    mode_consolidation=dict(col="Mode de consolidation"),
)

GROUP_BY_OPTIONS = [
    LABELS.poste_emissions,
    LABELS.type_structure,
    LABELS.secteur_activite,
]


def get_benchmark_dashboard():
    df = get_df()

    plot_col = pn.widgets.Select(
        name="Indicateur",
        options=[LABELS.emissions_par_salarie, LABELS.emissions_total],
    )
    group_by = pn.widgets.Select(
        name="Group by",
        options=GROUP_BY_OPTIONS,
    )
    widgets = {key: get_multi_choice(df, **kw) for key, kw in FILTERS.items()}
    # nested parameters don't seem to work well, so we pass all options directly as kwarg
    kwargs = dict(
        **{f"{k}_all": w.param.select_all for k, w in widgets.items()},
        **{f"{k}_options": w.param.selected_options for k, w in widgets.items()},
    )

    data = pn.bind(filter_options, df=df, secteur_activite="all", **kwargs)
    data = pn.bind(aggregate_bilans, df=data, plot_col=plot_col, group_by=group_by)
    plot_emissions_widget = pn.bind(
        plot_emissions, df=data, plot_col=plot_col, group_by=group_by
    )
    plot_n_bilans_widget = pn.bind(plot_n_bilans, df=data, group_by=group_by)
    n_bilans_widget = pn.bind(n_bilans_text, df=data)

    return pn.FlexBox(
        pn.Column(
            "## Filtrer les bilans",
            pn.WidgetBox(
                plot_col,
                group_by,
                *(w.widget() for w in widgets.values()),
                margin=10,
            ),
            n_bilans_widget,
            styles={
                "flex": "0 0 auto",
                **STYLES,
            },
        ),
        pn.Column(
            "## Émissions",
            plot_emissions_widget,
            "## Nb. bilans",
            plot_n_bilans_widget,
            styles={
                # Set flex-grow to 1 so the graph gets priority for growing
                "flex": "1 0 max-content",
                **STYLES,
            },
        ),
        pn.Column(
            "## Notes",
            section("benchmark/notes"),
            styles={
                # Set flex-grow to 0 so the notes don't get priority for growing. They can shrink if needed though
                "flex": "0 1 auto",
                **STYLES,
            },
            max_width=400,
        ),
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

    for key, opts in FILTERS.items():
        select_all: bool = kwargs.get(f"{key}_all", True)
        selected_options: list[str] = kwargs.get(f"{key}_options")
        col_name = opts["col"]
        if not select_all:
            x = x[x[col_name].isin(selected_options)]

    # drop nan values and zeros
    with pd.option_context("future.no_silent_downcasting", True):
        # the context is just here to remove a pandas warning
        x = x.fillna(0)
    x = x[x != 0]

    return x


def aggregate_bilans(df: pd.DataFrame, *, plot_col: str, group_by: str):
    """Aggregate data so that a group_by on the resulting data makes sense.

    Basically, before grouping emissions by an inter-bilan categories, we first need to group all the emissions
    per bilan (Id) and sum them together.
    This then allows doing other stats (mean, median, ...) on the total emissions per bilan.

    Note that, if the data was filtered prior (e.g. excluding some categories of emissions), then the stats will
    be on the filtered data, not on the total bilan emissions.

                     ▲          ┌─┐
                     │          │ │
                     │    ┌─┐   ├─┤
                     │    │ │   │ │
                     │    ├─┤   ├─┤
                     │    ├─┤   │ │   ┌─┐
                     │    │ │   ├─┤   │ │
    Intra-bilan      │    ├─┤   ├─┤   │ │
    categories       │    │ │   │ │   │ │
    (poste_emissions)│    │ │   ├─┤   ├─┤   ┌─┐
                     │    │ │   ├─┤   │ │   │ │
                     │    ├─┤   │ │   │ │   ├─┤
                     │    │ │   │ │   ├─┤   │ │
                     │    └─┘   └─┘   └─┘   └─┘

                          ────────────────────►    Bilans (Id)

                         │                │ │  │
                         └────────────────┘ └──┘

                          ────────────────────►    Inter-bilan categories
                                                   (secteur_activite,
                                                   type_structure, ...)

    """
    match group_by:
        case LABELS.poste_emissions:
            # We are grouping by an "intra-bilan" category, which means we don't want to aggregate emissions per bilan
            return df

        case LABELS.type_structure | LABELS.secteur_activite:
            # Get rid of intra-bilan categories (e.g. poste_emissions) by summing them together
            x = df.groupby([group_by, "Id"], dropna=False)[plot_col].sum()
            return x.reset_index()

        case _:
            raise ValueError(f"{group_by=} not supported")


def plot_emissions(
    df: pd.DataFrame,
    *,
    plot_col: str,
    group_by: str,
):
    x = df.copy()

    box = x.plot(
        kind="box",
        # Note: it would be possible here to pass `by=[LABELS.categorie_emissions, LABELS.poste_emissions]`
        # in order to group postes by category (with a multi-level index). But this does not work when combining
        # with a regular scatter plot.
        by=group_by,
        y=plot_col,
        **SIZE,
    )

    match plot_col:
        case LABELS.emissions_par_salarie:
            opts = dict(
                ylabel="tCO2 eq. / salarié",
                ylim=(0, _boxwhisker_upper_bound(x, group_by=group_by) + 1.0),
            )
        case LABELS.emissions_total:
            opts = dict(
                ylabel="tCO2 eq.",
                logx=True,
            )
        case _:
            raise ValueError(plot_col)

    return box.opts(
        invert_axes=True,
        # This is important to properly clear the axes when changing widget options (otherwise, both the emission
        # and the n_bilans plot keep their y-axis forever, even after un-selecting some options)
        shared_axes=False,
        **opts,
    )


def plot_n_bilans(df: pd.DataFrame, group_by: str):
    x = df.groupby(group_by, sort=False)

    if group_by == LABELS.poste_emissions:
        n_bilan_label = "Nb. de bilans incluant le poste d'émissions"
        part_bilan_label = "Part de bilans incluant le poste d'émissions (%)"
        y_col = part_bilan_label

        # there can be NaN or 0 values in 'emissions': we consider both as empty data
        x = (
            x[LABELS.emissions_total]
            .agg(lambda i: i.ne(0, fill_value=0).sum())
            .rename(n_bilan_label)
        )
        x = x.to_frame()
        n_bilans = df["Id"].nunique()
        x[part_bilan_label] = x[n_bilan_label] / n_bilans * 100
    else:
        y_col = "Nb. de bilans"
        x = x.Id.nunique().rename(y_col)

    fig = x.plot(
        kind="bar",
        y=y_col,
        # display all the data (absolute nb. in addition of the %) in the hover toolbox
        hover_cols="all",
        **SIZE,
    )

    return fig.opts(
        invert_axes=True,
        shared_axes=False,
        alpha=0.5,
    )


def n_bilans(df: pd.DataFrame):
    return df.Id.nunique()


def n_bilans_text(df: pd.DataFrame):
    return f"**Nb. total de bilans sélectionnés: {n_bilans(df)}**"


# Helper functions


def _boxwhisker_upper_bound(x, group_by: str):
    # compute the upper bound of all whisker plots
    upper = 1.0
    for category in x[group_by].unique():
        if category is None:
            continue
        y = x[(x[group_by] == category) & ~pd.isna(x[LABELS.emissions_par_salarie])]
        upper = max(upper, _get_upper_bar(y[LABELS.emissions_par_salarie].values))
    return upper
