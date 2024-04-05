# Data sources

Where does the data in `data/raw/` comes from?

* `export-inventaires-opendata-28-09-2023.csv`: ADEME bilans GES [website](https://bilans-ges.ademe.fr/bilans). Data up to 28/09/2023 only (and the export is also available on [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/bilan-ges/))
* `mapping-poste-emissions-ademe.csv`: hand made from ADEME website. Maps "poste d'émission" (e.g. P1.1) to a readable name (e.g. Émissions directes des sources fixes de combustion)
* NAF mapping (Nomenclature d’activités française): downloaded from [NAF rév. 2, 2008](https://www.insee.fr/fr/information/2120875)

Additional sources of data that could be used
* https://data.ademe.fr/datasets/bilans-climat-simplifies
* https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/#/resources

  * # **Notes sur les effectifs: comment aller plus loin qu'une tranche, et avoir un chiffre precis?**
#
# Une option: utiliser les donnees sur pappers, dans la section "finance".
# * via leur API: Fiche entreprise / finance / effectif. Prix: Abonnement 5k jetons/mois = 100e/mois, 15k jetons / mois = 200e/mois (1 jeton = 1 fiche entreprise)
# * scrapping: requetes individuelles non possible, mais la premiere requete (principale, ex: https://www.pappers.fr/entreprise/rhontelecom-753942416) donne un html duquel on peut extraire les infos
#     * ex: `<finances v-cloak :data='[{"annee":2022,"date_de_cloture_exercice":"2022-12-31","duree_exercice":12,"chiffre_affaires":120474217,"resultat":21116739,... "rentabilite_fonds_propres":94.5,"rentabilite_economique":30.6,"valeur_ajoutee":9651500,"valeur_ajoutee_CA":64.9,"salaires_charges_sociales":4148610,"salaires_CA":27.9,"impots_taxes":198981}]' class="finances" ratios="1">
#  `
