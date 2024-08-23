import pprint

import pytest

from src.visualization.visualize import LABELS
from tests import constants
import pandas as pd
from src.visualization.panel_figures import benchmark


@pytest.fixture
def df():
    return benchmark.get_df()


def test_main_figures(df):
    """
    This test is helpful to:
    - have the main figures (number of bilans, median, ...) stored explicitely somewhere
    - make sure these figures do not change by accident (e.g. by changing an algorithm)
    - see how these figures evolve when updating the dataset
    """
    d = {}
    for group_by in [
        LABELS.type_structure,
        LABELS.annee_reporting,
        LABELS.category_emissions,
    ]:
        x = benchmark.aggregate_bilans(df, group_by=group_by)
        x_mean = x.groupby(group_by)[[LABELS.emissions_par_collaborateur]].mean()
        x_median = x.groupby(group_by)[[LABELS.emissions_par_collaborateur]].median()
        x_count = (
            x.groupby(group_by)[[LABELS.emissions_par_collaborateur]]
            .count()
            .rename(columns={LABELS.emissions_par_collaborateur: "count"})
        )
        x = pd.merge(x_mean, x_median, on=group_by, suffixes=("_mean", "_median"))
        x = pd.merge(x, x_count, on=group_by)
        d[group_by] = x.round(1).to_dict()
    # helpful to update the constant
    # pprint is used to sort (recursively) the dict keys
    print(print(pprint.pformat(d).replace("\n", "")))
    assert d == constants.EMISSIONS_PER
