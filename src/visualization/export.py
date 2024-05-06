import argparse
import hvplot
import shutil
from pathlib import Path

from src.visualization.panel_figures.profiles import (
    TailleEntreprise,
    get_df,
    plot_type_structure,
    plot_annee_publication,
    plot_mois_publication,
    secteur_activite_n_entites_treemap,
    secteur_activite_ratio_treemap,
)

EXPORT_FOLDER = Path(
    "/Users/alexandre/Documents/Climate Change/CarbonTrackr/Blogs/blog_posts"
)


def gen_images_01(df, root):
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True)

    i = 0
    hvplot.save(
        plot_type_structure(df).opts(
            title="Type de structures ayant déposé des\n"
            "bilans GES sur le site de l'ADEME"
        ),
        filename=root / f"{i:2d}-type-structures.png",
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
            filename=root / f"{i:2d}-tailles-{type_structure}.png",
            toolbar=False,
        )
        i += 1


def gen_images_02(df, root):
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True)
    i = 0
    hvplot.save(
        plot_annee_publication(df).opts(
            title="Bilans GES déposés sur le site de l'ADEME, par année de publication\n"
            "et par année de reporting"
        ),
        filename=root / f"{i:2d}-annee-publication.png",
        toolbar=False,
    )
    i += 1
    hvplot.save(
        plot_mois_publication(df).opts(
            title="Bilans GES déposés sur le site de l'ADEME, par mois de publication"
        ),
        filename=root / f"{i:2d}-mois-publication.png",
        toolbar=False,
    )


def gen_images_03(df, root):
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True)
    i = 0
    fig = secteur_activite_n_entites_treemap(df).object
    name = f"{i:2d}-n_entites_treemap"
    for suffix in ("png", "svg", "pdf"):
        fig.write_image(root / f"{name}.{suffix}", scale=3)
    i += 1
    fig = secteur_activite_ratio_treemap(df).object
    name = f"{i:2d}-ratio_treemap"
    for suffix in ("png", "svg", "pdf"):
        fig.write_image(root / f"{name}.{suffix}", scale=3)


def profils_entreprises(df, blog_post):
    root = EXPORT_FOLDER / "01-profils-entreprises/img"

    if "01" in blog_post:
        gen_images_01(df, root / "01")

    if "02" in blog_post:
        gen_images_02(df, root / "02")

    if "03" in blog_post:
        gen_images_03(df, root / "03")


def main(blog_posts):
    df = get_df()
    profils_entreprises(df, blog_posts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("blog_posts", nargs="+")
    args = parser.parse_args()
    main(args.blog_posts)
