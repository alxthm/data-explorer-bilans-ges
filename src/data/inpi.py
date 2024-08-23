import logging
from datetime import datetime

import pandas as pd

from src.settings import DATA_PATH, RAW_ADEME_DATA_PATH, FILTERED_FINANCIAL_DATA_PATH


def get_fiscal_year(date):
    # Get the fiscal year based on the month of the date
    return date.year if date.month >= 7 else date.year - 1


def keep_one_bilan(df_bilan, prio: dict):
    df_bilan["type_bilan_priority"] = df_bilan["type_bilan"].map(prio)
    df_bilan = df_bilan.sort_values(
        ["siren", "annee_cloture_exercice", "type_bilan_priority"],
        ascending=[True, False, True],
    )
    df_bilan = df_bilan.drop_duplicates(
        subset=["siren", "annee_cloture_exercice"], keep="first"
    )
    df_bilan = df_bilan.drop(columns=["type_bilan_priority"])
    return df_bilan


def process_bilans_financiers():
    """
    Process financial data from INPI.

    The original CSV (~300Mb) can be downloaded from
    https://www.data.gouv.fr/fr/datasets/r/9d213815-1649-4527-9eb4-427146ef2e5b
    The documentation can be found at : https://www.data.gouv.fr/fr/datasets/ratios-financiers-bce-inpi/

    This code is partly taken from the data pipeline of the "Annuaire des Entreprises" :
    https://github.com/annuaire-entreprises-data-gouv-fr/search-infra/tree/4386f3c2bc54ba8635b050769a34015a3f97a8dd/workflows/data_pipelines/bilans_financiers
    """
    # Keep only selected fields.
    # Another field (in the original INPI database, but not in this .csv) could
    # be helpful : the duration of the "exercice comptable", since it is not always 1 year
    fields = [
        "siren",
        "chiffre_d_affaires",
        "resultat_net",
        "date_cloture_exercice",
        "type_bilan",
    ]

    # Read csv (keep only the interesting fields for us)
    _raw_data_path = DATA_PATH / "raw/heavy/ratios_inpi_bce.csv"
    logging.info(f"loading {_raw_data_path}...")
    df_bilan = pd.read_csv(_raw_data_path, dtype=str, sep=";", usecols=fields)

    logging.info(f"loaded 'ratios_inpi_bce.csv' ({len(df_bilan)} rows)")

    # Rename columns
    df_bilan = df_bilan.rename(columns={"chiffre_d_affaires": "ca"})

    # Convert columns to appropriate data types
    df_bilan["date_cloture_exercice"] = pd.to_datetime(
        df_bilan["date_cloture_exercice"], format="%Y-%m-%d"
    )
    df_bilan["ca"] = df_bilan["ca"].astype(float)
    df_bilan["resultat_net"] = df_bilan["resultat_net"].astype(float)

    # Get the current fiscal year
    df_bilan["annee_cloture_exercice"] = df_bilan["date_cloture_exercice"].apply(
        get_fiscal_year
    )

    # Filter out rows with fiscal years greater than the current fiscal year
    current_fiscal_year = get_fiscal_year(datetime.now())
    df_bilan = df_bilan[df_bilan["annee_cloture_exercice"] <= current_fiscal_year]
    logging.info(
        f"dropped fiscal years that are in the future (remaining: {len(df_bilan)} rows)"
    )

    # Drop duplicates based on siren, fiscal year, and type_bilan
    df_bilan = df_bilan.drop_duplicates(
        subset=["siren", "annee_cloture_exercice", "type_bilan"], keep="last"
    )
    logging.info(f"dropped duplicate entries (remaining: {len(df_bilan)} rows)")

    df_bilan = keep_one_bilan(
        df_bilan,
        {
            # Consolidated entries takes priority
            "K": "1-K",
            # Then complete entries
            "C": "2-C",
            # Then simplified entries
            "S": "3-S",
        },
    )
    logging.info(
        f"combined entries to keep one bilan per year per entity, with consolidated bilans first"
        f" (remaining: {len(df_bilan)} rows)"
    )
    logging.info(f'{df_bilan["type_bilan"].value_counts()}')

    df_bilan.to_csv(DATA_PATH / "interim/synthese_bilans_financiers.csv", index=False)

    # This is also possible if we need it
    # df_bilan_operational_first = keep_one_bilan(df_bilan, {
    #     # Complete entries take priority
    #     'C': '1-C',
    #     # Then simplified entries
    #     'S': '2-S',
    #     # Then consolidated entries
    #     'K': '3-K',
    # })


def filter_bilans_financiers_keep_only_ademe_sirens():
    df_bilan = pd.read_csv(
        DATA_PATH / "interim/synthese_bilans_financiers.csv", dtype=str
    )
    df_ademe = pd.read_csv(RAW_ADEME_DATA_PATH, sep=";")
    ademe_siren_codes = df_ademe["SIREN principal"].unique()
    df_bilan = df_bilan[df_bilan["siren"].isin(ademe_siren_codes)]
    df_bilan.to_csv(FILTERED_FINANCIAL_DATA_PATH, index=False)


if __name__ == "__main__":
    logging.basicConfig()

    # Ideally, all the raw data (including the INPI base data file) would be stored somewhere
    # (e.g. in a huggingface dataset?) and we would run this processing pipeline whenever we
    # need to make a change in the data.
    # For now, we run this pipeline locally, assuming the ratios_inpi_bce.csv file has been
    # downloaded manually and is in data/raw/heavy, and we save the light output to
    # data/interim/, to put it in the git repo.
    process_bilans_financiers()
    filter_bilans_financiers_keep_only_ademe_sirens()
