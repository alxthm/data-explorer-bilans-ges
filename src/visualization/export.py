import hvplot
import shutil
from pathlib import Path

from src.visualization.panel_figures.profiles import (
    TailleEntreprise,
    get_df,
    plot_type_structure,
)

EXPORT_FOLDER = Path(
    "/Users/alexandre/Documents/Climate Change/CarbonTrackr/Blogs/blog_posts"
)


def profils_entreprises(df):
    root = EXPORT_FOLDER / "01-profils-entreprises/img"
    shutil.rmtree(root, ignore_errors=True)

    # Blog post 01
    (root / "01").mkdir(parents=True)
    i = 0
    hvplot.save(
        plot_type_structure(df).opts(
            title="Type de structures ayant déposé des\n"
            "bilans GES sur le site de l'ADEME"
        ),
        filename=root / f"01/{i:2d}-type-structures.png",
        toolbar=False,
    )
    i += 1
    for type_structure, txt in [
        ("Entreprise", "par des entreprises,\n par taille d'entreprise"),
        ("Association", "par des associations"),
        ("Établissement public", "par établissements publics"),
        (
            "Collectivité territoriale (dont EPCI)",
            "par des collectivités territoriales\n (dont EPCI)",
        ),
    ]:
        hvplot.save(
            TailleEntreprise(df)
            .plot(type_structure=type_structure)
            .opts(title=f"Bilans GES déposés sur le site de l'ADEME {txt}"),
            filename=root / f"01/{i:2d}-tailles-{type_structure}.png",
            toolbar=False,
        )
        i += 1


def main():
    df = get_df()
    profils_entreprises(df)


if __name__ == "__main__":
    main()
