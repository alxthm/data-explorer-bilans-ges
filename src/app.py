import pandas as pd
import panel as pn

from src.data.make_dataset import DATA_PATH
from src.visualization.visualize import select_widget, _get_hvplot

pn.extension()


@pn.cache
def get_df():
    return pd.read_csv(DATA_PATH / "processed/bilans-ges-benchmark.csv")


df = get_df()

intro_txt = """
# Analyse des BEGES disponibles sur le site de l'ADEME

Source:
* [Bilans GES ADEME](https://bilans-ges.ademe.fr/bilans). Données jusqu'au 28/09/2023 uniquement (export aussi disponible sur [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/bilan-ges/)).

Etudes précédentes
* Bilan des Bilans carbone (2010) - https://www.greenit.fr/sites/greenit.fr/files/BC-Synthese.pdf

⚠️ Limitations à garder en tête
* Les données d'entrée sont biaisées: toutes les entreprises soumises à la réglementation ne publient pas leur BEGES sur le site de l'ADEME. Il est possible que ce les "bons élèves" aient plus facilement tendance à realiser et publier leur BEGES, et que les données d'entrée soient donc biaisées
* Il y a une grande variabilité dans les scopes et le périmètre des études: d'un secteur à l'autre, d'une année à l'autre, d'une entreprise à l'autre, etc. Par exemple, jusqu'en juillet 2022, la prise en compte du scope 3 n'était pas obligatoire ([cf décret](https://www.ecologie.gouv.fr/decret-bilan-des-emissions-gaz-effet-serre-beges))

**Bug d'affichage**: les points "outliers" (en dehors du box plot) ne sont pas visibles
"""

outro_txt = """
_Reminder: how to interpret a boxplot?_

<div>
<img src="https://upload.wikimedia.org/wikipedia/commons/1/1a/Boxplot_vs_PDF.svg" width="500"/>
</div>

Source: By Jhguch at en.wikipedia, CC BY-SA 2.5, https://commons.wikimedia.org/w/index.php?curid=14524285
"""

plot_col = pn.widgets.Select(
    name="Indicateur", options=["emissions_par_salarie", "emissions_clipped"]
)
mode_consolidation = select_widget(df, "Mode de consolidation")
annee = select_widget(df, "Année de reporting", sort=True)
shared_widget_box = pn.WidgetBox(plot_col, mode_consolidation, annee)

plot_by_secteur_activite = pn.bind(
    lambda **kw: _get_hvplot(df, group_by=["naf1"], secteur_activite="all", **kw),
    annee=annee,
    mode_consolidation=mode_consolidation,
    plot_col=plot_col,
)

secteur_activite = select_widget(df, "naf1", "Secteur d'activité")
plot_by_poste_emission = pn.bind(
    lambda **kw: _get_hvplot(df, group_by=["poste_name", "sub_poste_name"], **kw),
    secteur_activite=secteur_activite,
    annee=annee,
    mode_consolidation=mode_consolidation,
    plot_col=plot_col,
)

dashboard = pn.Row(
    shared_widget_box,
    pn.Column(
        pn.Column(
            "## Émissions totales, par secteur d'activité",
            plot_by_secteur_activite,
        ),
        pn.Column("## Postes d'émissions", secteur_activite, plot_by_poste_emission),
    ),
)
pane = pn.Column(intro_txt, dashboard, outro_txt)

pane.servable()
