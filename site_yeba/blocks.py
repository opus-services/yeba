"""Briques de contenu proposées dans l'éditeur : on compose le corps d'une page en les empilant."""

from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

TEXTE_COURANT = ["bold", "italic", "link", "document-link", "ol", "ul", "h3"]


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    legende = blocks.CharBlock(label="Légende", required=False)
    credit = blocks.CharBlock(label="Crédit photo", required=False)

    class Meta:
        icon = "image"
        label = "Image"
        template = "site_yeba/blocs/image.html"


class CitationBlock(blocks.StructBlock):
    texte = blocks.TextBlock(label="Citation")
    auteur = blocks.CharBlock(label="Auteur", required=False)

    class Meta:
        icon = "openquote"
        label = "Citation"
        template = "site_yeba/blocs/citation.html"


class ChiffreBlock(blocks.StructBlock):
    valeur = blocks.CharBlock(label="Chiffre", help_text="Par exemple : 26, 1 451, 90 jours")
    libelle = blocks.CharBlock(label="Ce qu'il mesure")


class ChiffresBlock(blocks.StructBlock):
    titre = blocks.CharBlock(label="Titre", required=False)
    chiffres = blocks.ListBlock(ChiffreBlock(), label="Chiffres", min_num=1, max_num=6)

    class Meta:
        icon = "pick"
        label = "Chiffres clés"
        template = "site_yeba/blocs/chiffres.html"


class BoutonBlock(blocks.StructBlock):
    texte = blocks.CharBlock(label="Texte du bouton")
    page = blocks.PageChooserBlock(label="Page du site", required=False)
    lien = blocks.URLBlock(label="ou lien externe", required=False)

    class Meta:
        icon = "link"
        label = "Bouton"
        template = "site_yeba/blocs/bouton.html"


class EncadreBlock(blocks.StructBlock):
    titre = blocks.CharBlock(label="Titre")
    texte = blocks.RichTextBlock(label="Texte", features=TEXTE_COURANT)

    class Meta:
        icon = "help"
        label = "Encadré"
        template = "site_yeba/blocs/encadre.html"


class DocumentBlock(blocks.StructBlock):
    document = DocumentChooserBlock()
    titre = blocks.CharBlock(label="Titre affiché", required=False, help_text="Vide : le titre du document")

    class Meta:
        icon = "doc-full"
        label = "Document à télécharger"
        template = "site_yeba/blocs/document.html"


class CorpsBlock(blocks.StreamBlock):
    paragraphe = blocks.RichTextBlock(label="Texte", features=TEXTE_COURANT)
    intertitre = blocks.CharBlock(label="Intertitre", template="site_yeba/blocs/intertitre.html", icon="title")
    image = ImageBlock()
    citation = CitationBlock()
    chiffres = ChiffresBlock()
    encadre = EncadreBlock()
    bouton = BoutonBlock()
    document = DocumentBlock()
    video = EmbedBlock(label="Vidéo (YouTube, Facebook…)", icon="media", template="site_yeba/blocs/video.html")


class PilierBlock(blocks.StructBlock):
    titre = blocks.CharBlock(label="Titre")
    texte = blocks.TextBlock(label="Texte")
    page = blocks.PageChooserBlock(label="Page liée", required=False)

    class Meta:
        icon = "list-ul"
        label = "Axe"
