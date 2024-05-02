import hvplot
from pathlib import Path

from src.visualization.panel_figures.profiles import TailleEntreprise, get_df

EXPORT_FOLDER = Path(
    "/Users/alexandre/Documents/Climate Change/CarbonTrackr/Blogs/blog_posts"
)


def main():
    df = get_df()

    hvplot.save(
        TailleEntreprise(df)
        .plot(type_structure="Entreprise")
        .opts(
            title="Bilans GES déposés sur le site de l'ADEME, par taille d'entreprise"
        ),
        filename=EXPORT_FOLDER / "01-combien-d-entreprises/taille.png",
        toolbar=False,
        title="Titre",
    )


if __name__ == "__main__":
    main()
