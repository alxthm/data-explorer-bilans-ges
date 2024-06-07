import itertools

import numpy as np
import pytest
import random

from src.visualization.panel_figures.benchmark import (
    get_df,
    filter_options,
    FILTERS,
    aggregate_bilans,
    n_bilans,
)
from src.visualization.visualize import LABELS
from tests.constants import N_POSTES_EMISSIONS, N_BILANS_TOTAL, TOTAL_EMISSIONS


@pytest.fixture
def df():
    return get_df()


def test_full_data(df):
    # Even though the emissions for many rows are 0 or nan, we have 22 rows per bilan in the full dataframe.
    assert len(df) == N_BILANS_TOTAL * N_POSTES_EMISSIONS

    # Default filtering options should not remove any data
    x = filter_options(
        df, secteur_activite="all", **{f"{k}_all": True for k in FILTERS}
    )
    assert len(x) == N_BILANS_TOTAL * N_POSTES_EMISSIONS

    # Check that the sum of all emissions is consistent
    assert (
        TOTAL_EMISSIONS
        == df[LABELS.emissions_total].sum()
        == (df[LABELS.emissions_par_salarie] * df["nb_salaries_mean"]).sum()
    )


def test_filter_options():
    # Build a random (but reproducible, thanks to the seed) set of filtering options
    # that a user could choose.
    # This can be a starting point to then manually adjust.
    options = {}
    for k, v in FILTERS.items():
        all_options = get_df()[v["col"]].unique().tolist()
        # to be able to sort, we can't mix str with float
        # all_options = ["nan" if np.isnan(x) else x for x in all_options]
        # to be more deterministic
        # all_options = sorted(all_options)
        options[k] = [
            "all",
            random.sample(all_options, k=1),
            random.sample(all_options, k=len(all_options) // 2),
        ]
    return options


_filter_options = {
    "type_structure": [
        "all",
        ["Collectivité territoriale (dont EPCI)"],
        ["Établissement public", "Entreprise"],
    ],
    "secteur_activite": [
        "all",
        [
            "Activités extra-territoriales",
            "Activités financières et d'assurance",
            "Industries extractives",
            "Agriculture, sylviculture et pêche",
            "Hébergement et restauration",
            "Activités spécialisées, scientifiques et techniques",
            "Activités immobilières",
            "Industrie manufacturière",
            "Transports et entreposage",
            "Enseignement",
        ],
    ],
    "category_emissions": [
        "all",
        ["3 - Déplacement", "4 - Produits achetés", "2 - Énergie"],
    ],
    "poste_emissions": [
        "all",
        [
            "6.1 - Autres émissions directes",
            "5.4 - Investissements",
            "1.1 - Émissions directes des sources fixes de combustion",
            "1.2 - Émissions directes des sources mobiles de combustion",
            "3.2 - Transport de marchandise aval",
            "4.1 - Achat de biens",
            "4.5 - Achat de services",
            "4.2 - Immobilisation de biens",
            "3.4 - Déplacements des visiteurs et des clients",
            "5.1 - Utilisation des produits vendus",
            "4.3 - Gestion des déchets",
            "1.3 - Émissions directes des procédés hors énergie",
        ],
    ],
    "annee": ["all", [2009, 2011, 2012, 2014, 2021, 2015, 2022]],
    "mode_consolidation": ["all"],
}
_all_options = itertools.product(*_filter_options.values())


@pytest.mark.parametrize(
    ["group_by", "filters"],
    itertools.product(
        (
            LABELS.poste_emissions,
            LABELS.type_structure,
            LABELS.secteur_activite,
        ),
        _all_options,
    ),
)
def test_after_filter_and_group_by(df, group_by, filters):
    filters = dict(zip(_filter_options.keys(), filters))
    # Compute expected sanity values
    z = _filtered_df(df, filters)
    expected_total_emissions = z[LABELS.emissions_total].sum()
    expected_n_bilans = z["Id"].nunique()
    expected_postes_emissions = z[LABELS.poste_emissions].nunique()

    # Apply the functions we want to test
    filter_kwargs = dict(
        **{f"{k}_all": (v == "all") for k, v in filters.items()},
        **{f"{k}_options": v for k, v in filters.items()},
    )
    df_filtered = filter_options(df, secteur_activite="all", **filter_kwargs)
    assert n_bilans(df_filtered) == expected_n_bilans
    x = aggregate_bilans(
        df_filtered, plot_col=LABELS.emissions_total, group_by=group_by
    )
    x2 = aggregate_bilans(
        df_filtered, plot_col=LABELS.emissions_par_salarie, group_by=group_by
    )

    # Total emissions grouped by the y_axis column...
    # ... in the original dataframe
    emissions_df = (
        z.groupby(group_by, dropna=False)[LABELS.emissions_total].sum().values
    )
    # ... and in the filtered and aggregated dataframe
    emissions_x = x.groupby(group_by, dropna=False)[LABELS.emissions_total].sum().values
    emissions_x2 = (
        x2.groupby(group_by, dropna=False)[LABELS.emissions_par_salarie].sum().values
        * df_filtered.groupby(group_by, dropna=False)["nb_salaries_mean"].sum().values
    )
    # They should all match, category by category
    assert np.allclose(emissions_df, emissions_x, emissions_x2)
    # The total as well

    assert np.allclose(emissions_x.sum(), expected_total_emissions)

    if group_by == LABELS.poste_emissions:
        # For intra-bilan group_by, we should have 1 row per bilan (Id) and per poste emissions
        assert len(x) == expected_n_bilans * expected_postes_emissions
    else:
        # For inter-bilan group_by, we should have 1 row per bilan (Id)
        assert len(x) == expected_n_bilans


def _filtered_df(df, opts):
    # alternative (and simpler) implementation of filter_options, just for sanity checks
    for k, v in opts.items():
        if v != "all":
            df = df[df[FILTERS[k]["col"]].isin(v)]
    return df
