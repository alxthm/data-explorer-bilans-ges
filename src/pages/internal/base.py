import panel as pn
from pathlib import Path

# TODO: find a way a load plotly only once for apps that need it
pn.extension("plotly", defer_load=True, loading_indicator=True)


def _get_navbar_link(href, name, active: bool):
    # Previous try : not useful, we don't need interactivity since we reload the page everytime...
    #     const items = document.querySelectorAll('#header-items .bk-panel-models-markup-HTML');
    #     var roots = Array.from(items).flatMap(item => item.shadowRoot ? [item.shadowRoot] : []);
    #     var links = roots.flatMap(root => root.querySelector('a') ? [root.querySelector('a') ] : []);
    #
    #     if (links.length) {
    #       links.forEach((link) => {
    #         link.addEventListener('click', (e) => {
    #           links.forEach((link) => {
    #               link.classList.remove('active');
    #           });
    #           // e.preventDefault();
    #           link.classList.add('active');
    #         });
    #       });
    #     }
    link = pn.pane.HTML(
        f"""
<a href="{href}"{' class="active"' if active else ''}>{name}</a>
""",
        styles={"color": "--header-color", "font-size": "1.15em"},
        stylesheets=[
            """
            a {
                color: var(--panel-on-background-color);
                text-decoration: none;
                padding: 0.5em .25em;
            }
            a:hover {
                color: var(--panel-primary-color);
                border-bottom: 3px solid var(--panel-primary-color);
            }
            a.active {
                color: var(--panel-primary-color);
                border-bottom: 3px solid var(--panel-primary-color);
            }
            """
        ],
    )
    return link


def _get_navbar_links(page):
    return [
        _get_navbar_link(href, n, active=(page == href))
        for href, n in [
            ("benchmark", "Benchmark Émissions"),
            ("profiles", "Profil des entreprises et des bilans publiés"),
            ("about", "À propos"),
        ]
    ]


def get_template(main, page):
    # Load the custom CSS: increase app font size
    # This must be done here (and cannot be done inside the template init),
    # so that the generated stylesheet is inserted before loading the
    # various scripts). Otherwise, the --bokeh-font-size is not considered
    # as defined.
    pn.config.raw_css.append("""
    :host {
        --bokeh-font-size: 1em;
    }
    """)

    template = pn.template.VanillaTemplate(
        title="Data Explorer - Bilans GES",
        main=[main],
        header=_get_navbar_links(page),
        header_background="--panel-background-color",
        header_color="--panel-on-background-color",
        raw_css=[
            """            
            #header {
                box-shadow: 0 .125rem .25rem 0 rgba(0, 0, 0, 0.1);
                position: static;
                flex-wrap: wrap;
            }

            #header-items {
                width: auto;
                flex-wrap: wrap;
            }
            
            #content {
                /* thanks to this, the header bar can scroll with the content
                instead of being sticky */
                overflow: visible;
            }
            </style>
            <script defer data-domain="bilans-ges.fr" src="https://sh.alxthm.com/js/script.js"></script>
            <style>
            """
        ],
        # For search engines description
        meta_description="Quelques graphiques pour mieux comprendre les bilans d'émission de gaz "
                         "à effet de serre (bilans GES) publiés sur le site de l'ADEME.",
        meta_viewport="width=device-width, initial-scale=1",
        favicon=(Path(__file__).parent / "favicon.svg").absolute(),
    )

    return template
