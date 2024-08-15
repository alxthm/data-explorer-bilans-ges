from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data/"
# Path to the (uncompressed) dataset of Bilans GES
RAW_ADEME_DATA_PATH = DATA_PATH / "raw/heavy/export-inventaires-opendata-21-07-2024.csv"
# Path to the financial data (C.A. from INPI data), after filtering to keep only
# entries already present in the ADEME dataset
FILTERED_FINANCIAL_DATA_PATH = (
    DATA_PATH / "interim/synthese_bilans_financiers_ademe_only.csv"
)
