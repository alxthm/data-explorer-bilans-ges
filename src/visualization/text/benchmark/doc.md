ℹ️ **Documentation et hypothèses de calcul**

* Chaque point sur le graphe des "Émissions" correspond à un bilan GES déposé sur le site de l'ADEME.
* *L'année de reporting* correspond à l'année sur laquelle porte l'étude de bilan GES. Elle est en général différente de *l'année de publication* qui correspond à l'année de la publication sur le site de l'ADEME.
* Avec un "Group By" par scope, catégorie ou poste d'émissions :
  * Pour chaque poste d'émissions, seuls les bilans avec des émissions spécifiées et non-nulles sont considérés.
  * Pour chaque scope / catégorie d'émissions, les postes d'émissions sont agrégés : seuls les bilans avec au moins un poste d'émissions non-nul sont considérés. 
* 💡 [Aide : comment interpréter une figure "Box Plot" ?](https://ir.uoregon.edu/B%26W)

ℹ️ **Hypothèses de calcul**

* Les points de données avec des émissions nulles sont ignorés.
* Les données du "nombre de collaborateurs" sont approximatives : pour chaque entité ayant publié sur le site de l'ADEME, on prend la moyenne de la fourchette spécifiée (e.g. pour "250-499 employés", on utilise (250 + 499) / 2).
  * Selon le site de l'ADEME, pour les entreprises cela correspond au "nombre de salariés", et pour les organismes publics au "nombre d'agents".
