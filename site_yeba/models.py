"""Les types de pages du site de Yeba et les réglages modifiables dans l'administration.

Arbre du site :
    Accueil
    ├── Pages simples (Qui sommes-nous, Gouvernance, Nous soutenir, Mentions légales…)
    ├── Nos projets ── Projet (data.cd, Yeba Réflexion…)
    ├── Actualités ── Actualité
    ├── Activités ── Activité (conférence, atelier, campagne…)
    └── Contact (formulaire)
"""

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from .blocks import CorpsBlock, PilierBlock

PAR_PAGE = 12


def _image(label="Image principale", aide=""):
    return models.ForeignKey(
        "wagtailimages.Image", verbose_name=label, help_text=aide,
        null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )


def _a_venir():
    """Activités pas encore terminées : la fin (ou à défaut le début) est dans le futur."""
    maintenant = timezone.now()
    return models.Q(fin__gte=maintenant) | models.Q(fin__isnull=True, debut__gte=maintenant)


def _paginer(request, elements):
    return Paginator(elements, PAR_PAGE).get_page(request.GET.get("page"))


class PageYeba(Page):
    """Champs communs : un chapeau et une image, repris dans les listes, les aperçus et les partages."""

    chapeau = models.TextField("Chapeau", blank=True,
                               help_text="Deux ou trois phrases qui résument la page (listes, moteurs de recherche, réseaux sociaux).")
    image = _image()

    search_fields = Page.search_fields + [index.SearchField("chapeau")]

    class Meta:
        abstract = True


# --- Réglages et éléments réutilisables ----------------------------------------------------------------------------


@register_setting(icon="cog")
class Coordonnees(BaseGenericSetting):
    adresse = models.TextField("Adresse du siège", blank=True)
    email = models.EmailField("E-mail de contact", blank=True)
    telephone = models.CharField("Téléphone", max_length=40, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=40, blank=True, help_text="Numéro au format international, ex. +243…")
    facebook = models.URLField("Facebook", blank=True)
    x = models.URLField("X (Twitter)", blank=True)
    linkedin = models.URLField("LinkedIn", blank=True)
    youtube = models.URLField("YouTube", blank=True)
    instagram = models.URLField("Instagram", blank=True)
    tiktok = models.URLField("TikTok", blank=True)
    page_soutien = models.ForeignKey("wagtailcore.Page", verbose_name="Page « Nous soutenir »", null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name="+",
                                     help_text="Cible du bouton « Nous soutenir » de l'en-tête.")

    panels = [
        MultiFieldPanel([FieldPanel("adresse"), FieldPanel("email"),
                         FieldRowPanel([FieldPanel("telephone"), FieldPanel("whatsapp")])], heading="Coordonnées"),
        MultiFieldPanel([FieldPanel("facebook"), FieldPanel("x"), FieldPanel("linkedin"), FieldPanel("youtube"),
                         FieldPanel("instagram"), FieldPanel("tiktok")], heading="Réseaux sociaux"),
        FieldPanel("page_soutien"),
    ]

    class Meta:
        verbose_name = "Coordonnées et réseaux sociaux"

    def reseaux(self):
        noms = [("facebook", "Facebook"), ("x", "X"), ("linkedin", "LinkedIn"), ("youtube", "YouTube"),
                ("instagram", "Instagram"), ("tiktok", "TikTok")]
        return [(libelle, getattr(self, champ)) for champ, libelle in noms if getattr(self, champ)]


@register_snippet
class Partenaire(index.Indexed, models.Model):
    nom = models.CharField("Nom", max_length=150)
    logo = _image("Logo")
    lien = models.URLField("Site internet", blank=True)
    ordre = models.PositiveSmallIntegerField("Ordre d'affichage", default=0)
    visible = models.BooleanField("Afficher sur l'accueil", default=True)

    panels = [FieldPanel("nom"), FieldPanel("logo"), FieldPanel("lien"),
              FieldRowPanel([FieldPanel("ordre"), FieldPanel("visible")])]
    search_fields = [index.SearchField("nom")]

    class Meta:
        ordering = ["ordre", "nom"]
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"

    def __str__(self):
        return self.nom


# --- Pages -----------------------------------------------------------------------------------------------------------


class AccueilPage(Page):
    accroche = models.CharField("Grand titre", max_length=160, default="Savoir pour agir")
    introduction = models.TextField("Introduction", blank=True)
    image = _image("Image du bandeau", "Facultative. Sans image, le bandeau est en bleu fleuve.")
    bouton_texte = models.CharField("Texte du bouton", max_length=60, blank=True)
    bouton_page = models.ForeignKey("wagtailcore.Page", verbose_name="Page du bouton", null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="+")
    axes_titre = models.CharField("Titre des axes", max_length=120, blank=True, default="Ce que nous faisons")
    axes = StreamField([("axe", PilierBlock())], verbose_name="Axes d'action", blank=True)
    appel_titre = models.CharField("Titre de l'appel", max_length=120, blank=True)
    appel_texte = models.TextField("Texte de l'appel", blank=True)
    appel_page = models.ForeignKey("wagtailcore.Page", verbose_name="Page de l'appel", null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name="+")

    content_panels = Page.content_panels + [
        MultiFieldPanel([FieldPanel("accroche"), FieldPanel("introduction"), FieldPanel("image"),
                         FieldRowPanel([FieldPanel("bouton_texte"), FieldPanel("bouton_page")])], heading="Bandeau"),
        MultiFieldPanel([FieldPanel("axes_titre"), FieldPanel("axes")], heading="Axes d'action"),
        MultiFieldPanel([FieldPanel("appel_titre"), FieldPanel("appel_texte"), FieldPanel("appel_page")],
                        heading="Appel en bas de page (nous soutenir, nous rejoindre…)"),
    ]
    subpage_types = ["site_yeba.PageSimple", "site_yeba.ProjetsIndex", "site_yeba.ActualitesIndex",
                     "site_yeba.ActivitesIndex", "site_yeba.ContactPage"]
    parent_page_types = ["wagtailcore.Page"]
    max_count = 1

    class Meta:
        verbose_name = "Page d'accueil"

    def get_context(self, request, *args, **kwargs):
        contexte = super().get_context(request, *args, **kwargs)
        contexte["projets"] = ProjetPage.objects.live().filter(mis_en_avant=True).specific()[:4]
        contexte["activites"] = ActivitePage.a_venir()[:3]
        contexte["actualites"] = ActualitePage.objects.live().order_by("-date", "-first_published_at")[:3]
        contexte["partenaires"] = Partenaire.objects.filter(visible=True)
        return contexte


class PageSimple(PageYeba):
    corps = StreamField(CorpsBlock(), verbose_name="Contenu", blank=True)

    content_panels = Page.content_panels + [FieldPanel("chapeau"), FieldPanel("image"), FieldPanel("corps")]
    search_fields = PageYeba.search_fields + [index.SearchField("corps")]
    subpage_types = ["site_yeba.PageSimple"]

    class Meta:
        verbose_name = "Page simple"
        verbose_name_plural = "Pages simples"


class ProjetsIndex(PageYeba):
    content_panels = Page.content_panels + [FieldPanel("chapeau")]
    subpage_types = ["site_yeba.ProjetPage"]
    parent_page_types = ["site_yeba.AccueilPage"]
    max_count = 1

    class Meta:
        verbose_name = "Liste des projets"

    def get_context(self, request, *args, **kwargs):
        contexte = super().get_context(request, *args, **kwargs)
        contexte["projets"] = ProjetPage.objects.child_of(self).live().specific()
        return contexte


class ProjetPage(PageYeba):
    STATUTS = [("en_cours", "En cours"), ("en_preparation", "En préparation"), ("termine", "Terminé")]

    statut = models.CharField("Statut", max_length=20, choices=STATUTS, default="en_cours")
    logo = _image("Logo du projet", "Facultatif. Sinon, l'image principale est utilisée dans les listes.")
    site_web = models.URLField("Site du projet", blank=True)
    lancement = models.CharField("Lancement", max_length=60, blank=True, help_text="Par exemple : 2026, janvier 2027")
    mis_en_avant = models.BooleanField("Afficher sur l'accueil", default=True)
    corps = StreamField(CorpsBlock(), verbose_name="Présentation", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("chapeau"),
        MultiFieldPanel([FieldRowPanel([FieldPanel("statut"), FieldPanel("lancement")]), FieldPanel("site_web"),
                         FieldPanel("mis_en_avant")], heading="Fiche"),
        FieldRowPanel([FieldPanel("logo"), FieldPanel("image")]),
        FieldPanel("corps"),
    ]
    search_fields = PageYeba.search_fields + [index.SearchField("corps")]
    parent_page_types = ["site_yeba.ProjetsIndex"]
    subpage_types = []

    class Meta:
        verbose_name = "Projet"

    def get_context(self, request, *args, **kwargs):
        contexte = super().get_context(request, *args, **kwargs)
        contexte["actualites"] = ActualitePage.objects.live().filter(projet=self).order_by("-date")[:3]
        contexte["activites"] = ActivitePage.objects.live().filter(projet=self).order_by("-debut")[:3]
        return contexte


class ActualitesIndex(PageYeba):
    content_panels = Page.content_panels + [FieldPanel("chapeau")]
    subpage_types = ["site_yeba.ActualitePage"]
    parent_page_types = ["site_yeba.AccueilPage"]
    max_count = 1

    class Meta:
        verbose_name = "Liste des actualités"

    def get_context(self, request, *args, **kwargs):
        contexte = super().get_context(request, *args, **kwargs)
        actualites = ActualitePage.objects.child_of(self).live().order_by("-date", "-first_published_at")
        contexte["actualites"] = _paginer(request, actualites)
        return contexte


class ActualitePage(PageYeba):
    date = models.DateField("Date", default=timezone.localdate)
    auteur = models.CharField("Auteur", max_length=120, blank=True)
    projet = models.ForeignKey("site_yeba.ProjetPage", verbose_name="Projet concerné", null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="actualites")
    corps = StreamField(CorpsBlock(), verbose_name="Texte", blank=True)

    content_panels = Page.content_panels + [
        FieldRowPanel([FieldPanel("date"), FieldPanel("auteur")]),
        FieldPanel("chapeau"), FieldPanel("image"), FieldPanel("corps"), FieldPanel("projet"),
    ]
    search_fields = PageYeba.search_fields + [index.SearchField("corps"), index.FilterField("date")]
    parent_page_types = ["site_yeba.ActualitesIndex"]
    subpage_types = []

    class Meta:
        verbose_name = "Actualité"


class ActivitesIndex(PageYeba):
    content_panels = Page.content_panels + [FieldPanel("chapeau")]
    subpage_types = ["site_yeba.ActivitePage"]
    parent_page_types = ["site_yeba.AccueilPage"]
    max_count = 1

    class Meta:
        verbose_name = "Liste des activités"

    def get_context(self, request, *args, **kwargs):
        contexte = super().get_context(request, *args, **kwargs)
        activites = ActivitePage.objects.child_of(self).live()
        genre = request.GET.get("type", "")
        if genre in dict(ActivitePage.GENRES):
            activites = activites.filter(genre=genre)
        a_venir = _a_venir()
        contexte["genres"] = ActivitePage.GENRES
        contexte["genre_choisi"] = genre
        contexte["a_venir"] = activites.filter(a_venir).order_by("debut")
        contexte["passees"] = _paginer(request, activites.exclude(a_venir).order_by("-debut"))
        return contexte


class ActivitePage(PageYeba):
    GENRES = [
        ("conference", "Conférence"),
        ("seminaire", "Séminaire"),
        ("atelier", "Atelier"),
        ("table_ronde", "Table ronde"),
        ("formation", "Formation"),
        ("campagne", "Campagne de sensibilisation"),
        ("terrain", "Action de terrain"),
        ("autre", "Autre"),
    ]

    genre = models.CharField("Type d'activité", max_length=20, choices=GENRES, default="conference")
    debut = models.DateTimeField("Début")
    fin = models.DateTimeField("Fin", null=True, blank=True, help_text="Facultatif (campagne sur plusieurs jours…)")
    lieu = models.CharField("Lieu", max_length=200, blank=True, help_text="Salle, adresse")
    ville = models.CharField("Ville", max_length=80, blank=True, default="Kinshasa")
    en_ligne = models.BooleanField("Aussi en ligne", default=False)
    inscription = models.URLField("Lien d'inscription", blank=True)
    projet = models.ForeignKey("site_yeba.ProjetPage", verbose_name="Projet concerné", null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="activites")
    corps = StreamField(CorpsBlock(), verbose_name="Présentation et compte rendu", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("genre"),
        MultiFieldPanel([FieldRowPanel([FieldPanel("debut"), FieldPanel("fin")]),
                         FieldRowPanel([FieldPanel("lieu"), FieldPanel("ville")]),
                         FieldRowPanel([FieldPanel("en_ligne"), FieldPanel("inscription")])], heading="Quand et où"),
        FieldPanel("chapeau"), FieldPanel("image"), FieldPanel("corps"), FieldPanel("projet"),
    ]
    search_fields = PageYeba.search_fields + [index.SearchField("corps"), index.SearchField("ville"),
                                              index.FilterField("debut")]
    parent_page_types = ["site_yeba.ActivitesIndex"]
    subpage_types = []

    class Meta:
        verbose_name = "Activité"

    def clean(self):
        super().clean()
        if self.fin and self.debut and self.fin < self.debut:
            raise ValidationError({"fin": "La fin doit venir après le début."})

    @property
    def passee(self):
        return (self.fin or self.debut) < timezone.now()

    @classmethod
    def a_venir(cls):
        return cls.objects.live().filter(_a_venir()).order_by("debut")


class ChampContact(AbstractFormField):
    page = ParentalKey("site_yeba.ContactPage", on_delete=models.CASCADE, related_name="form_fields")


class ContactPage(AbstractEmailForm):
    introduction = RichTextField("Introduction", blank=True, features=["bold", "italic", "link"])
    remerciement = RichTextField("Message après envoi", blank=True, features=["bold", "italic", "link"])

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("introduction"),
        InlinePanel("form_fields", label="Champs du formulaire"),
        FieldPanel("remerciement"),
        MultiFieldPanel([FieldRowPanel([FieldPanel("from_address"), FieldPanel("to_address")]),
                         FieldPanel("subject")], heading="Envoi par e-mail des messages reçus"),
    ]
    parent_page_types = ["site_yeba.AccueilPage"]
    subpage_types = []
    max_count = 1
    landing_page_template = "site_yeba/contact_page_merci.html"

    class Meta:
        verbose_name = "Page de contact"

    def serve(self, request, *args, **kwargs):
        # Piège à robots : un champ caché que seuls les robots remplissent. On fait comme si l'envoi avait réussi.
        if request.method == "POST" and request.POST.get("site_internet"):
            return self.render_landing_page(request, None, *args, **kwargs)
        return super().serve(request, *args, **kwargs)

