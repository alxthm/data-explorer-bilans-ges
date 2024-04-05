# Data sources

Where does the data in `data/raw/` comes from?

* `export-inventaires-opendata-28-09-2023.csv`: ADEME bilans GES [website](https://bilans-ges.ademe.fr/bilans). Data up to 28/09/2023 only (and the export is also available on [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/bilan-ges/))
* `mapping-poste-emissions-ademe.csv`: hand made from ADEME website. Maps "poste d'émission" (e.g. P1.1) to a readable name (e.g. Émissions directes des sources fixes de combustion)
* NAF mapping (Nomenclature d’activités française): downloaded from [NAF rév. 2, 2008](https://www.insee.fr/fr/information/2120875)

Additional sources of data that could be used
* https://data.ademe.fr/datasets/bilans-climat-simplifies
* https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/#/resources
