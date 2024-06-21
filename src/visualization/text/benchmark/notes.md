ℹ️ **Documentation**
* Chaque point sur le graphe des "Émissions" correspond à un bilan GES déposé sur le site de l'ADEME.
* Les points de données avec des émissions nulles sont ignorés.
* Avec un "Group By" par scope, catégorie ou poste d'émissions :
  * Pour chaque poste d'émissions, seuls les bilans avec des émissions spécifiées et non-nulles sont considérés.
  * Pour chaque scope / catégorie d'émissions, les postes d'émissions sont agrégés : seuls les bilans avec au moins un poste d'émissions non-nul sont considérés. 
* 💡 [Aide : comment interpréter une figure "Box Plot" ?](https://ir.uoregon.edu/B%26W)

⚠️ **Limitations**
* Pour l'instant, seules les données Bilans GES de l'ADEME jusqu'au 28/09/2023 sont prises en compte sur ce site.
* Les bilans GES publiés ne sont pas soumis à un audit, et contrairement à l'étude de l'ADEME, qui a enlevé "quelques résultats aberrants", ici tous les résultats sont pris en compte. Il vaut donc mieux se fier à la médiane plutôt qu'à la moyenne (moins robuste aux valeurs aberrantes).  
* De manière générale, il n'est pas pertinent de comparer des bilans GES d'entreprises différentes, car les scopes et le périmètre des études sont trop variables. Par exemple, jusqu'en juillet 2022, la prise en compte du scope 3 n'était pas obligatoire ([cf décret](https://www.ecologie.gouv.fr/decret-bilan-des-emissions-gaz-effet-serre-beges)) pour publier un Bilan GES.
* Les données du "nombre d'employés" sont approximatives : pour chaque entité ayant publié sur le site de l'ADEME, on prend la moyenne de la fourchette spécifiée (e.g. pour `"250-499 employés"`, on utilise `(250 + 499) / 2`).
