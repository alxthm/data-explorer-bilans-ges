# These constants are valid for the data exported up to 2023

# Total number of bilans GES in the database
N_BILANS_TOTAL = 7180
# Total number of entities with a different SIREN in the database
N_ENTITES_TOTAL = 4824
# Number of existing postes d'emissions (1.1, 1.2, ..., 6.1, ...)
N_POSTES_EMISSIONS = 22
# The sum of all emissions (tCO2) in the database (note that there are some negative values in the database,
# which reduce this total)
TOTAL_EMISSIONS = 2073617687.5238597

EMISSIONS_PER = {
    "Année de reporting": {
        "Intensité_carbone_salarié_mean": {
            2009: 45.8,
            2010: 26.7,
            2011: 22.8,
            2012: 1711.2,
            2013: 18.2,
            2014: 76.0,
            2015: 108.5,
            2016: 19.9,
            2017: 30.9,
            2018: 150.3,
            2019: 56.3,
            2020: 2634.0,
            2021: 247.5,
            2022: 1008.7,
            2023: 662.6,
            2024: 34.7,
        },
        "Intensité_carbone_salarié_median": {
            2009: 45.8,
            2010: 25.4,
            2011: 6.8,
            2012: 7.1,
            2013: 7.7,
            2014: 4.5,
            2015: 3.6,
            2016: 3.8,
            2017: 3.4,
            2018: 3.7,
            2019: 5.6,
            2020: 3.2,
            2021: 5.4,
            2022: 14.2,
            2023: 32.7,
            2024: 19.7,
        },
        "count": {
            2009: 2,
            2010: 12,
            2011: 75,
            2012: 48,
            2013: 51,
            2014: 563,
            2015: 537,
            2016: 369,
            2017: 324,
            2018: 957,
            2019: 948,
            2020: 537,
            2021: 1060,
            2022: 1419,
            2023: 266,
            2024: 12,
        },
    },
    "Catégorie d'émissions": {
        "Intensité_carbone_salarié_mean": {
            "1 - Émissions directes": 243.3,
            "2 - Énergie": 7.1,
            "3 - Déplacement": 27.8,
            "4 - Produits achetés": 80.8,
            "5 - Produits vendus": 151.4,
            "6 - Autres émissions indirectes": 3.0,
        },
        "Intensité_carbone_salarié_median": {
            "1 - Émissions directes": 1.5,
            "2 - Énergie": 0.3,
            "3 - Déplacement": 0.0,
            "4 - Produits achetés": 0.5,
            "5 - Produits vendus": 0.0,
            "6 - Autres émissions indirectes": 0.0,
        },
        "count": {
            "1 - Émissions directes": 7180,
            "2 - Énergie": 7180,
            "3 - Déplacement": 7180,
            "4 - Produits achetés": 7180,
            "5 - Produits vendus": 7180,
            "6 - Autres émissions indirectes": 7180,
        },
    },
    "Type de structure": {
        "Intensité_carbone_salarié_mean": {
            "Association": 50.0,
            "Collectivité territoriale (dont EPCI)": 195.7,
            "Entreprise": 727.0,
            "Établissement public": 21.3,
            "État": 25.3,
        },
        "Intensité_carbone_salarié_median": {
            "Association": 2.4,
            "Collectivité territoriale (dont EPCI)": 14.0,
            "Entreprise": 6.8,
            "Établissement public": 2.7,
            "État": 1.2,
        },
        "count": {
            "Association": 195,
            "Collectivité territoriale (dont EPCI)": 545,
            "Entreprise": 4862,
            "Établissement public": 1330,
            "État": 248,
        },
    },
}
