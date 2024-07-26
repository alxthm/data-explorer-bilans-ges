# These constants are valid for the data exported up to 2023

# Total number of bilans GES in the database
N_BILANS_TOTAL = 5639
# Total number of entities with a different SIREN in the database
N_ENTITES_TOTAL = 4021
# Number of existing postes d'emissions (1.1, 1.2, ..., 6.1, ...)
N_POSTES_EMISSIONS = 22
# The sum of all emissions (tCO2) in the database (note that there are some negative values in the database,
# which reduce this total)
TOTAL_EMISSIONS = 1000384393.1213682

EMISSIONS_PER = {
    "Année de reporting": {
        "count": {
            2009: 2,
            2010: 10,
            2011: 73,
            2012: 46,
            2013: 51,
            2014: 561,
            2015: 535,
            2016: 367,
            2017: 318,
            2018: 952,
            2019: 921,
            2020: 514,
            2021: 935,
            2022: 350,
            2023: 4,
        },
        "Émission_par_salarié_mean": {
            2009: 45.8,
            2010: 24.8,
            2011: 23.5,
            2012: 1785.4,
            2013: 18.0,
            2014: 76.3,
            2015: 108.8,
            2016: 20.0,
            2017: 30.9,
            2018: 151.0,
            2019: 50.0,
            2020: 138.9,
            2021: 224.6,
            2022: 267.6,
            2023: 55.4,
        },
        "Émission_par_salarié_median": {
            2009: 45.8,
            2010: 19.8,
            2011: 6.9,
            2012: 7.4,
            2013: 7.0,
            2014: 4.5,
            2015: 3.6,
            2016: 3.8,
            2017: 3.2,
            2018: 3.6,
            2019: 5.5,
            2020: 3.1,
            2021: 4.4,
            2022: 8.1,
            2023: 36.2,
        },
    },
    "Catégorie d'émissions": {
        "count": {
            "1 - Émissions directes": 5639,
            "2 - Énergie": 5639,
            "3 - Déplacement": 5639,
            "4 - Produits achetés": 5639,
            "5 - Produits vendus": 5639,
            "6 - Autres émissions indirectes": 5639,
        },
        "Émission_par_salarié_mean": {
            "1 - Émissions directes": 50.6,
            "2 - Énergie": 5.1,
            "3 - Déplacement": 21.9,
            "4 - Produits achetés": 36.1,
            "5 - Produits vendus": 19.8,
            "6 - Autres émissions indirectes": 2.6,
        },
        "Émission_par_salarié_median": {
            "1 - Émissions directes": 1.5,
            "2 - Énergie": 0.3,
            "3 - Déplacement": 0.0,
            "4 - Produits achetés": 0.2,
            "5 - Produits vendus": 0.0,
            "6 - Autres émissions indirectes": 0.0,
        },
    },
    "Type de structure": {
        "count": {
            "Association": 162,
            "Collectivité territoriale (dont EPCI)": 459,
            "Entreprise": 3642,
            "Établissement public": 1146,
            "État": 230,
        },
        "Émission_par_salarié_mean": {
            "Association": 29.3,
            "Collectivité territoriale (dont EPCI)": 225.6,
            "Entreprise": 176.8,
            "Établissement public": 13.3,
            "État": 3.9,
        },
        "Émission_par_salarié_median": {
            "Association": 2.2,
            "Collectivité territoriale (dont EPCI)": 13.4,
            "Entreprise": 5.3,
            "Établissement public": 2.3,
            "État": 0.5,
        },
    },
}
