from django import template
from wagtail.models import Page, Site

register = template.Library()


@register.simple_tag(takes_context=True)
def menu_principal(context):
    """Pages de premier niveau cochées « Afficher dans les menus » (onglet Promotion de l'éditeur)."""
    request = context.get("request")
    site = Site.find_for_request(request) if request else None
    if not site:
        return Page.objects.none()
    return site.root_page.get_children().live().in_menu()


@register.simple_tag(takes_context=True)
def accueil(context):
    request = context.get("request")
    site = Site.find_for_request(request) if request else None
    return site.root_page if site else None


@register.filter
def dans_rubrique(page, rubrique):
    """Vrai si la page affichée est la rubrique du menu ou l'une de ses sous-pages."""
    return bool(page) and getattr(page, "path", "").startswith(rubrique.path)


@register.simple_tag(takes_context=True)
def page_par_slug(context, slug):
    racine = accueil(context)
    if not racine:
        return None
    return racine.get_descendants().live().filter(slug=slug).first()


@register.simple_tag
def description(page):
    """Résumé de la page pour les moteurs de recherche et les partages : description SEO, chapeau ou introduction."""
    for champ in ("search_description", "chapeau", "introduction"):
        valeur = getattr(page, champ, "")
        if valeur:
            return valeur
    return ""
