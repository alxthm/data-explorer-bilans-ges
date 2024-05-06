import pytest

from src.visualization.panel_figures.profiles import get_df, TailleEntreprise
from src.visualization.visualize import df_nunique, LABELS

# Total number of bilans GES in the database
N_BILANS_TOTAL = 5639
# Total number of entities with a different SIREN in the database
N_ENTITES_TOTAL = 4021


class TestDataCoherence:
    @pytest.fixture
    def df(self):
        return get_df()

    def test_total(self, df):
        assert len(df) == N_BILANS_TOTAL
        assert df.Id.nunique() == N_BILANS_TOTAL
        # make sure we have 1 unique Id per row
        assert df.Id.nunique() == len(df)
        # make sure all rows have a well-defined SIREN number
        assert df["SIREN principal"].isna().sum() == 0

        # make sure each entity has exactly 1 naf5 (nan is allowed)
        assert (
            df.groupby("naf5", dropna=False)["SIREN principal"].nunique().sum()
            == N_ENTITES_TOTAL
        )

    def test_taille_entreprises(self, df):
        # Check the 'Type de structure' plot
        x = df_nunique(df, groupby="Type de structure")[
            ["Type de structure", LABELS.n_bilans, LABELS.n_entites]
        ]
        assert x[LABELS.n_bilans].sum() == N_BILANS_TOTAL
        assert x[LABELS.n_entites].sum() == N_ENTITES_TOTAL

        # Check the 'Taille entreprises' plot, using the plot above
        n_bilans_entreprises = x.loc[
            x["Type de structure"] == "Entreprise", LABELS.n_bilans
        ].item()
        n_total, n_500_or_more, n_less_than_500, n_nan = TailleEntreprise(df)._numbers()
        assert n_total == (n_500_or_more + n_less_than_500 + n_nan)
        assert n_total == n_bilans_entreprises
