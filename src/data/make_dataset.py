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


def get_last_naf5(df):
    """
    Return a dataframe with a unique NAF5 per entity, for entities that have multiple NAF5
    in the database.

    Returns:
        A dataframe with 2 columns (SIREN / naf5). Each row corresponds to an entity that has
        at least 2 different naf5 number in the database (e.g. 2 different valid naf5, or 1 nan and 1 valid naf5).
        The naf5 column corresponds to the last valid naf5 in the database for this entity.
    """
    # SIREN is properly defined for all entries, so no need to specify dropna=False when grouping by SIREN

    y = df[["SIREN principal", "naf5", "month_publication"]]
    # call fillna because NaN acts weirdly with nunique()
    y = y.fillna("nan")
    # build the series of corrected naf5: focus on SIREN numbers that have more than 1 naf value
    z = y.groupby("SIREN principal").naf5.nunique()
    y = y.set_index("SIREN principal").loc[z > 1]
    # if there is a nan naf5, drop it and rely on the other SIREN number(s)
    # todo: fix this (for some reason it does not include entities with a nan naf5 in the output dict...)
    # y = y.drop(y[y.naf5 == "nan"].index)
    # when there are multiple valid naf5 values defined, take the last one (according to the publication date)
    y = y.sort_values(["SIREN principal", "month_publication"])
    y = y.groupby("SIREN principal").last()

    y = y.drop(columns=["month_publication"])
    return y


def enrich_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # Get useful stats for number of employees
    df["nb_salaries_range"] = df["Nombre de salariés/d'agents"].map(_nb_salaries_range)
    df["nb_salaries_min"] = df["nb_salaries_range"].map(_nb_salaries_min)
    df["nb_salaries_max"] = df["nb_salaries_range"].map(_nb_salaries_max)
    df["nb_salaries_mean"] = (df["nb_salaries_min"] + df["nb_salaries_max"]) / 2
    # arbitrary value for 10000+ companies
    df.loc[df.nb_salaries_max.isnull(), "nb_salaries_mean"] = 15000

    # Convert to a python date (month is enough)
    df["month_publication"] = pd.to_datetime(
        df["Date de publication"], dayfirst=True
    ).dt.to_period("M")

    df["naf5"] = df["APE(NAF) associé"].map(
        lambda x: None if pd.isna(x) else f"{x[:2]}.{x[2:]}"
    )

    # A few entities have multiple naf values registered (over multiple entries).
    # Introduce a 'naf5_last' column with a unique naf5 value per SIREN (typically the last one)
    d = get_last_naf5(df).to_dict()["naf5"]

    def _f(j):
        if j["SIREN principal"] in d:
            return d[j["SIREN principal"]]
        return j["naf5"]

    df["naf5_last"] = df.apply(_f, axis=1)
    df = df.rename(columns={"naf5_last": "naf5", "naf5": "naf5_non_unique"})

    # Get a readable name for NAF
    _naf5_to_nafi = _load_naf5_to_nafi_data()
    _naf_to_libelle = _load_naf_to_libelle_data()

    def get_nafi(naf5: Optional[str], niv: int) -> Optional[str]:
        if naf5 is None or naf5 not in _naf5_to_nafi[f"NIV{niv}"]:
            return None
        return _naf5_to_nafi[f"NIV{niv}"][naf5]

    def naf_to_libelle(naf5: Optional[str], niv: int) -> Optional[str]:
        if naf5 is None or naf5 not in _naf5_to_nafi[f"NIV{niv}"]:
            return None
        return _naf_to_libelle[f"NIV{niv}"][get_nafi(naf5, niv)]

    for i in range(1, 5):
        df[f"naf{i}"] = df.naf5.map(lambda x: naf_to_libelle(x, niv=i))
        df[f"naf{i}_code"] = df.naf5.map(lambda x: get_nafi(x, niv=i))
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
        ...  '6.1': '6.1 - Autres émissions directes'},
        ...  'nom_scope': {'1.1': '1',
        ...  '1.2': '1',
        ...  '1.3': '1',
        ...  '1.4': '1',
        ...  '1.5': '1',
        ...  '2.1': '2',
        ...  '2.2': '2',
        ...  '3.1': '3',
        ...  '3.2': '3',
        ...  ...
        ...  '5.4': '3',
        ...  '6.1': '3'}}}
    """
    df_category_name = pd.read_csv(
        DATA_PATH / "raw/mapping-poste-emissions-ademe.csv", sep=";", dtype=str
    )
    poste_code_to_name = df_category_name.set_index("code").to_dict()
    # add explicit names
    # Emission categories 1 and 2 = scope 1 and 2 (resp.). All other categories belong to scope 3.
    poste_code_to_name["nom_scope"] = {
        k: cat if (cat := k.split(".")[0]) in ("1", "2") else "3"
        for k, v in poste_code_to_name["nom_poste"].items()
    }
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
            "Structure obligée",
        ],
        value_vars=_emission_cols,
        value_name="emissions",
        var_name="poste_emissions",
    )

    df["emissions_par_salarie"] = df["emissions"] / df["nb_salaries_mean"]
    # clip to 1 (instead of 0) to be able to apply log
    df["emissions_clipped"] = df["emissions"].clip(lower=1e-3)
    df["scope_name"] = df["poste_emissions"].map(
        lambda x: poste_code_to_name["nom_scope"][x]
    )
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
