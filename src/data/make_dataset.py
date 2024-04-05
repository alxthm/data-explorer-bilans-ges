# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Optional

import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[2] / "data/"


def _load_naf5_to_nafi_data() -> dict[str, dict[str, str]]:
    # NIV5	    NIV4	NIV3	NIV2	NIV1
    # 01.11Z	01.11	01.1	01	    A
    # 01.12Z	01.12	01.1	01	    A
    _df_naf_5_niveaux = pd.read_excel(
        DATA_PATH / "raw/naf2008_5_niveaux.xls", dtype=str
    )
    _naf5_to_nafi = _df_naf_5_niveaux.set_index("NIV5").to_dict()
    return _naf5_to_nafi


def _load_naf_to_libelle_data() -> dict[str, dict[str, str]]:
    df_naf_v1_to_v2 = pd.read_excel(DATA_PATH / "raw/table_NAF2-NAF1.xls")
    df_naf_v1_to_v2 = df_naf_v1_to_v2.rename(
        columns={f"NAF\nrév. {i}": f"naf_v{i}" for i in (1, 2)}
    )
    _naf_v1_to_v2 = df_naf_v1_to_v2[["naf_v1", "naf_v2"]].set_index("naf_v1").to_dict()

    _naf_to_libelle = {}
    for n in range(1, 5):
        df_naf = pd.read_excel(
            DATA_PATH / f"raw/naf2008_liste_n{n}.xls", skiprows=2, dtype={"Code": str}
        )
        _naf_to_libelle[f"NIV{n}"] = df_naf.set_index("Code").to_dict()["Libellé"]
    return _naf_to_libelle


def _nb_salaries_range(x: str):
    """
    Examples:
        >>> _nb_salaries_range('Entre 5 000 et 9 999')
        '5000-9999'
        >>> _nb_salaries_range('Plus de 9 999')
        '9999-'
    """
    if pd.isna(x):
        return None
    if "Plus de" in x:
        x = x.removeprefix("Plus de ")
        i = int(x.replace(" ", ""))
        return f"{i}-"
    x = x.removeprefix("Entre ")
    i, j = x.split(" et ")
    i = int(i.replace(" ", ""))
    j = int(j.replace(" ", ""))
    x = f"{i}-{j}"
    return x


def _nb_salaries_min(x: Optional[str]):
    if x is None:
        return None
    return int(x.split("-")[0])


def _nb_salaries_max(x: Optional[str]):
    if x is None:
        return None
    i, j = x.split("-")
    if len(j) == 0:
        return None
    return int(j)


def enrich_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # Get useful stats for number of employees
    df["nb_salaries_range"] = df["Nombre de salariés/d'agents"].map(_nb_salaries_range)
    df["nb_salaries_min"] = df["nb_salaries_range"].map(_nb_salaries_min)
    df["nb_salaries_max"] = df["nb_salaries_range"].map(_nb_salaries_max)
    df["nb_salaries_mean"] = (df["nb_salaries_min"] + df["nb_salaries_max"]) / 2
    # arbitrary value for 10000+ companies
    df.loc[df.nb_salaries_max.isnull(), "nb_salaries_mean"] = 15000

    # Get a readable name for NAF
    df["naf5"] = df["APE(NAF) associé"].map(
        lambda x: None if pd.isna(x) else f"{x[:2]}.{x[2:]}"
    )
    _naf5_to_nafi = _load_naf5_to_nafi_data()
    _naf_to_libelle = _load_naf_to_libelle_data()

    def naf_to_libelle(naf5: Optional[str], niv: int) -> Optional[str]:
        if naf5 is None or naf5 not in _naf5_to_nafi[f"NIV{niv}"]:
            return None
        nafi = _naf5_to_nafi[f"NIV{niv}"][naf5]
        return _naf_to_libelle[f"NIV{niv}"][nafi]

    for i in range(1, 5):
        df[f"naf{i}"] = df.naf5.map(lambda x: naf_to_libelle(x, niv=i))

    # Convert to a python date (month is enough)
    df["month_publication"] = pd.to_datetime(
        df["Date de publication"], dayfirst=True
    ).dt.to_period("M")
    return df


def _load_emission_categories_code_to_name():
    """
    Examples:
        >>> {'nom_poste': {'1.1': '1 - Émissions directes',
        ...  '1.2': '1 - Émissions directes',
        ...   ...
        ...  '5.4': '5 - Produits vendus',
        ...  '6.1': '6 - Autres émissions indirectes'},
        ... 'nom_sous_poste': {'1.1': '1.1 - Émissions directes des sources fixes de combustion',
        ...  '1.2': '1.2 - Émissions directes des sources mobiles de combustion',
        ...  ...
        ...  '5.4': '5.4 - Investissements',
        ...  '6.1': '6.1 - Autres émissions directes'}}
    """
    df_category_name = pd.read_csv(
        DATA_PATH / "raw/mapping-poste-emissions-ademe.csv", sep=";", dtype=str
    )
    poste_code_to_name = df_category_name.set_index("code").to_dict()
    # add explicit names
    poste_code_to_name["nom_poste"] = {
        k: f'{k.split(".")[0]} - {v}'
        for k, v in poste_code_to_name["nom_poste"].items()
    }
    poste_code_to_name["nom_sous_poste"] = {
        k: f"{k} - {v}" for k, v in poste_code_to_name["nom_sous_poste"].items()
    }
    return poste_code_to_name


def transform_to_benchmark_df(df_enriched: pd.DataFrame) -> pd.DataFrame:
    poste_code_to_name = _load_emission_categories_code_to_name()

    _emission_cols = [c for c in df_enriched.columns if "Emissions publication" in c]
    _emission_cols = [c.split(" P")[-1] for c in _emission_cols]
    df = df_enriched.rename(
        columns={f"Emissions publication P{i}": i for i in _emission_cols}
    )
    df = df.melt(
        id_vars=[
            "Id",
            "SIREN principal",
            "Méthode BEGES (V4,V5)",
            "Type de structure",
            "Type de collectivité",
            "Mode de consolidation",
            "Recalcul",
            "Comparaison avec le précédent bilan",
            "nb_salaries_range",
            "nb_salaries_min",
            "nb_salaries_max",
            "nb_salaries_mean",
            "naf5",
            "naf1",
            "naf2",
            "naf3",
            "naf4",
            "month_publication",
            "Année de reporting",
        ],
        value_vars=_emission_cols,
        value_name="emissions",
        var_name="poste_emissions",
    )

    df["emissions_par_salarie"] = df["emissions"] / df["nb_salaries_mean"]
    # clip to 1 (instead of 0) to be able to apply log
    df["emissions_clipped"] = df["emissions"].clip(lower=1.0)
    df["poste_name"] = df["poste_emissions"].map(
        lambda x: poste_code_to_name["nom_poste"][x]
    )
    df["sub_poste_name"] = df["poste_emissions"].map(
        lambda x: poste_code_to_name["nom_sous_poste"][x]
    )
    return df


def main():
    """Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    df_raw = pd.read_csv(
        DATA_PATH / "raw/export-inventaires-opendata-28-09-2023.csv", sep=";"
    )

    df_enriched = enrich_df(df_raw)
    df_benchmark = transform_to_benchmark_df(df_enriched)

    df_enriched.to_csv(DATA_PATH / "processed/bilans-ges-all.csv", index=False)
    df_benchmark.to_csv(DATA_PATH / "processed/bilans-ges-benchmark.csv", index=False)


if __name__ == "__main__":
    main()
