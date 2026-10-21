"""Crée l'arbre des pages du site et ses contenus de départ, tirés des statuts de l'ASBL.

    python manage.py peupler_yeba              pages de départ (à relancer sans risque : une page qui existe déjà
                                               n'est jamais modifiée, on peut donc la retoucher dans l'administration)
    python manage.py peupler_yeba --exemples   ajoute des activités et une actualité d'exemple, pour essayer le site
                                               en local. À NE PAS utiliser sur le site en ligne.
"""

import json
from datetime import timedelta
from email.utils import parseaddr
from urllib.parse import urlsplit

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from wagtail.models import Page, Site

from site_yeba.models import (
    AccueilPage, ActivitePage, ActivitesIndex, ActualitePage, ActualitesIndex, ChampContact, ContactPage, Coordonnees,
    PageSimple, ProjetPage, ProjetsIndex,
)


def corps(*blocs):
    """Contenu d'un StreamField : ("paragraphe", "<p>…</p>"), ("intertitre", "…"), ("bouton", {...})…"""
    return json.dumps([{"type": genre, "value": valeur} for genre, valeur in blocs])


def liste(*elements):
    return "<ul>" + "".join(f"<li>{e}</li>" for e in elements) + "</ul>"


class Command(BaseCommand):
    help = "Crée les pages de départ du site de Yeba (sans toucher aux pages existantes)."

    def add_arguments(self, parser):
        parser.add_argument("--exemples", action="store_true",
                            help="Ajoute des activités et une actualité d'exemple (essais en local seulement).")

    def creer(self, parent, modele, slug, **champs):
        existante = parent.get_children().filter(slug=slug).first()
        if existante:
            return existante.specific
        page = modele(slug=slug, **champs)
        parent.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write(f"   + {page.title}")
        return page

    @transaction.atomic
    def handle(self, *args, **options):
        accueil = self.accueil()

        qui = self.creer(accueil, PageSimple, "qui-sommes-nous", title="Qui sommes-nous", show_in_menus=True,
                         chapeau="Yeba est une association citoyenne congolaise. Elle met à la disposition de tous "
                                 "des connaissances vérifiées, des outils pratiques et des espaces de réflexion et "
                                 "d'action sur la vie de la nation.",
                         corps=corps(
                             ("paragraphe", "<p>En lingala, <i>yeba</i> veut dire « sache ! ». Notre conviction est "
                                            "simple : un citoyen bien informé connaît ses droits, remplit ses devoirs "
                                            "et peut agir pour sa communauté. D'où notre devise : "
                                            "<b>savoir pour agir</b>.</p>"),
                             ("intertitre", "Notre mission"),
                             ("paragraphe", "<p>Yeba contribue à une citoyenneté éclairée et active en République "
                                            "démocratique du Congo. L'association s'adresse aux citoyens, aux "
                                            "communautés, aux entreprises et aux institutions, en RDC comme dans la "
                                            "diaspora.</p>"),
                             ("intertitre", "Nos objectifs"),
                             ("paragraphe", liste(
                                 "Produire, vérifier et diffuser une information fiable et accessible sur l'État, le "
                                 "droit, les démarches administratives, les institutions, l'économie, la société, le "
                                 "patrimoine, la culture et l'histoire de la RDC.",
                                 "Promouvoir la réflexion, la recherche et le débat d'idées sur les questions "
                                 "essentielles à la vie de la nation.",
                                 "Sensibiliser et former les citoyens et les entreprises à leurs droits, à leurs "
                                 "devoirs et aux bonnes pratiques.",
                                 "Encourager la participation de tous les Congolais, en RDC et dans la diaspora, à la "
                                 "vie publique et au développement de leurs communautés.",
                                 "Valoriser le patrimoine culturel et naturel congolais et les langues nationales.",
                                 "Promouvoir l'usage des données et du numérique au service de l'intérêt général.")),
                             ("intertitre", "Nos principes"),
                             ("encadre", {"titre": "Indépendance et neutralité",
                                          "texte": "<p>Yeba est indépendante de tout parti politique, de toute "
                                                   "confession religieuse et de tout groupe d'intérêt. Elle ne "
                                                   "soutient aucun candidat ni aucune formation politique.</p>"}),
                             ("paragraphe", liste(
                                 "<b>Des sources citées</b> : chaque fiche indique ses sources et la date de sa "
                                 "dernière vérification.",
                                 "<b>Les faits d'un côté, les analyses de l'autre</b> : les analyses sont signées par "
                                 "leurs auteurs.",
                                 "<b>Des erreurs corrigées</b> publiquement et rapidement dès qu'elles sont signalées.",
                                 "<b>La transparence</b> : tout partenaire ou financeur d'un contenu, d'un événement ou "
                                 "d'une campagne est mentionné, et aucun n'a de droit de regard avant publication.")),
                         ))
        self.creer(qui, PageSimple, "gouvernance", title="Gouvernance",
                   chapeau="Comment l'association est dirigée et contrôlée.",
                   corps=corps(
                       ("paragraphe", "<p>Yeba est une association sans but lucratif régie par la loi n° 004/2001 du "
                                      "20 juillet 2001. Ses organes sont les suivants.</p>"),
                       ("intertitre", "L'Assemblée générale"),
                       ("paragraphe", "<p>Organe suprême de l'association, elle réunit les membres fondateurs et "
                                      "effectifs une fois par an. Elle élit les administrateurs, approuve les comptes "
                                      "et le rapport d'activités et fixe les grandes orientations.</p>"),
                       ("intertitre", "Le Conseil d'administration"),
                       ("paragraphe", "<p>Cinq à sept administrateurs bénévoles, élus pour trois ans, dont au moins "
                                      "deux administrateurs indépendants, un administrateur résidant en province et un "
                                      "administrateur issu de la diaspora.</p>"),
                       ("intertitre", "La Direction exécutive"),
                       ("paragraphe", "<p>Le Directeur exécutif met en œuvre les décisions du Conseil et dirige "
                                      "l'équipe, les projets et le réseau de collaborateurs.</p>"),
                       ("intertitre", "Le Comité scientifique et éthique"),
                       ("paragraphe", "<p>Cinq à neuf personnalités reconnues pour leur compétence et leur intégrité. "
                                      "Le Comité veille au respect de la charte éditoriale et de la neutralité, propose "
                                      "les thèmes du centre de réflexion et relit les publications.</p>"),
                       ("intertitre", "Le contrôle des comptes"),
                       ("paragraphe", "<p>Deux commissaires aux comptes contrôlent la gestion chaque année. Les comptes "
                                      "annuels, le rapport d'activités et la liste des principaux financeurs sont "
                                      "publiés après leur approbation.</p>"),
                   ))

        projets = self.creer(accueil, ProjetsIndex, "projets", title="Nos projets", show_in_menus=True,
                             chapeau="Chaque projet porte son propre nom et sert la même mission : savoir pour agir.")
        datacd = self.creer(projets, ProjetPage, "data-cd", title="data.cd", statut="en_cours",
                            site_web="https://data.cd", lancement="2026",
                            chapeau="La plateforme qui explique la RDC : démarches administratives, institutions, "
                                    "histoire, patrimoine, chiffres clés et simulateurs, avec des sources citées.",
                            corps=corps(
                                ("paragraphe", "<p>data.cd rassemble en un seul endroit ce qu'il faut savoir pour "
                                               "vivre, travailler et entreprendre en RDC : comment obtenir un "
                                               "passeport ou un acte de naissance, qui fait quoi dans les "
                                               "institutions, combien coûte une démarche, ce que dit la loi.</p>"),
                                ("paragraphe", "<p>Chaque fiche cite ses sources et indique la date de sa dernière "
                                               "vérification. Les citoyens peuvent signaler une erreur ou une "
                                               "information dépassée.</p>"),
                                ("bouton", {"texte": "Visiter data.cd", "page": None, "lien": "https://data.cd"}),
                            ))
        reflexion = self.creer(projets, ProjetPage, "yeba-reflexion", title="Yeba Réflexion", statut="en_preparation",
                               chapeau="Le centre de réflexion de Yeba : conférences, séminaires, tables rondes et "
                                       "travaux de recherche sur les questions essentielles à la vie de la nation.",
                               corps=corps(
                                   ("paragraphe", "<p>Yeba Réflexion réunit chercheurs, praticiens, responsables "
                                                  "publics et citoyens pour débattre, dans le respect de la neutralité, "
                                                  "des grandes questions du pays : institutions, économie, éducation, "
                                                  "santé, culture.</p>"),
                                   ("paragraphe", "<p>Les thèmes sont proposés par le Comité scientifique et éthique. "
                                                  "Les comptes rendus et les notes de synthèse sont publiés sur ce "
                                                  "site.</p>"),
                               ))
        self.creer(projets, ProjetPage, "yeba-editions", title="Yeba Éditions", statut="en_preparation",
                   chapeau="Magazine, revue, notes et livres : les publications de Yeba, pour approfondir et "
                           "transmettre.",
                   corps=corps(
                       ("paragraphe", "<p>Yeba Éditions publiera des notes, des rapports, un magazine et une revue, "
                                      "ainsi que des ouvrages sur l'histoire, le patrimoine et la vie publique en "
                                      "RDC, sur papier et en ligne.</p>"),
                   ))

        activites = self.creer(accueil, ActivitesIndex, "activites", title="Activités", show_in_menus=True,
                               chapeau="Conférences, séminaires, ateliers, formations et campagnes de "
                                       "sensibilisation : l'agenda de Yeba.")
        actualites = self.creer(accueil, ActualitesIndex, "actualites", title="Actualités", show_in_menus=True,
                                chapeau="Les nouvelles de l'association et de ses projets.")
        self.creer(actualites, ActualitePage, "bienvenue", title="Bienvenue sur le site de Yeba",
                   chapeau="L'association présente sa mission, ses projets et ses activités.",
                   corps=corps(
                       ("paragraphe", "<p>Ce site présente Yeba, ses projets, à commencer par data.cd, et son agenda : "
                                      "conférences, ateliers, séminaires et campagnes de sensibilisation.</p>"),
                       ("paragraphe", "<p>Vous souhaitez participer, devenir membre ou proposer un partenariat ? "
                                      "Écrivez-nous depuis la page Contact.</p>"),
                   ))

        soutenir = self.creer(accueil, PageSimple, "nous-soutenir", title="Nous soutenir",
                              chapeau="Membre, bénévole, point focal, partenaire ou donateur : chacun peut contribuer "
                                      "à une citoyenneté éclairée.",
                              corps=corps(
                                  ("intertitre", "Devenir membre"),
                                  ("paragraphe", "<p>Les <b>membres effectifs</b> participent activement à la vie de "
                                                 "l'association et votent à l'Assemblée générale. Les <b>Amis de "
                                                 "Yeba</b> soutiennent l'association par une cotisation ou un don "
                                                 "régulier.</p>"),
                                  ("intertitre", "Rejoindre le réseau"),
                                  ("paragraphe", "<p>Yeba s'appuie sur des coordinateurs provinciaux, des points "
                                                 "focaux dans les villes et les territoires, des relais dans les "
                                                 "quartiers et les villages, des experts et des bénévoles, en RDC et "
                                                 "dans la diaspora.</p>"),
                                  ("intertitre", "Devenir partenaire"),
                                  ("paragraphe", "<p>Institutions, universités, médias, organisations de la société "
                                                 "civile, entreprises et partenaires techniques et financiers peuvent "
                                                 "soutenir un projet, une activité ou une campagne. Chaque partenaire "
                                                 "est mentionné publiquement ; aucun n'a de droit de regard sur les "
                                                 "contenus avant leur publication.</p>"),
                                  ("intertitre", "Faire un don"),
                                  ("paragraphe", "<p>Les coordonnées bancaires et de monnaie électronique de "
                                                 "l'association seront publiées ici dès l'ouverture de ses comptes.</p>"),
                              ))
        contact = self.contact(accueil)
        self.creer(accueil, PageSimple, "mentions-legales", title="Mentions légales",
                   corps=corps(
                       ("intertitre", "Éditeur"),
                       ("paragraphe", "<p>Yeba, association sans but lucratif de droit congolais. Siège : Kinshasa, "
                                      "[adresse à compléter]. Directeur de la publication : [à compléter].</p>"),
                       ("intertitre", "Hébergement"),
                       ("paragraphe", "<p>Opalstack (Opalstack LLC, États-Unis).</p>"),
                       ("intertitre", "Données personnelles"),
                       ("paragraphe", "<p>Les messages envoyés par le formulaire de contact servent uniquement à vous "
                                      "répondre. Ils ne sont ni vendus ni transmis à des tiers. Pour les faire "
                                      "supprimer, écrivez-nous depuis la page Contact.</p>"),
                   ))

        # Liens de l'accueil vers les pages créées (seulement s'ils sont encore vides).
        if not accueil.axes:
            accueil.axes = corps(
                ("axe", {"titre": "Informer", "page": datacd.pk,
                         "texte": "Une information fiable et sourcée sur l'État, le droit, les démarches, les "
                                  "institutions, l'histoire et le patrimoine de la RDC."}),
                ("axe", {"titre": "Réfléchir", "page": reflexion.pk,
                         "texte": "Un centre de réflexion qui organise conférences, séminaires, tables rondes et "
                                  "travaux de recherche."}),
                ("axe", {"titre": "Sensibiliser", "page": activites.pk,
                         "texte": "Des campagnes d'éducation civique et des formations pour les citoyens, les écoles, "
                                  "les communautés et les entreprises."}),
                ("axe", {"titre": "Agir ensemble", "page": soutenir.pk,
                         "texte": "Un réseau de points focaux, de relais et de bénévoles sur tout le territoire et "
                                  "dans la diaspora."}),
            )
            accueil.bouton_texte, accueil.bouton_page = "Découvrir Yeba", qui
            accueil.appel_titre = "Rejoignez le mouvement"
            accueil.appel_texte = "Devenez membre, bénévole, point focal ou partenaire de Yeba."
            accueil.appel_page = soutenir
            accueil.save_revision().publish()

        coordonnees = Coordonnees.load()
        if not coordonnees.page_soutien:
            coordonnees.page_soutien = soutenir
            coordonnees.save()

        if options["exemples"]:
            self.exemples(activites, actualites, datacd, reflexion)
        self.stdout.write(self.style.SUCCESS(f"Site prêt ({Page.objects.live().count() - 1} pages publiées). "
                                             f"Contact : {contact.url}"))

    def accueil(self):
        """Remplace la page de bienvenue de Wagtail par l'accueil de Yeba et la rattache au site."""
        accueil = AccueilPage.objects.first()
        racine = Page.get_first_root_node()
        if not accueil:
            accueil = AccueilPage(
                title="Accueil", slug="accueil", accroche="Savoir pour agir",
                introduction="Association citoyenne congolaise, Yeba met à la disposition de chacun des "
                             "connaissances vérifiées, des outils pratiques et des espaces de réflexion et d'action "
                             "sur la vie de la nation.",
            )
            racine.add_child(instance=accueil)
            accueil.save_revision().publish()
            self.stdout.write("   + Accueil")
        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            Site.objects.create(hostname="localhost", port=80, root_page=accueil, is_default_site=True,
                                site_name="Yeba")
        elif site.root_page_id != accueil.pk:
            ancienne = site.root_page
            site.root_page, site.site_name = accueil, "Yeba"
            site.save()
            # La page « Welcome to your new Wagtail site! » créée à l'installation de Wagtail.
            if ancienne.specific_class is Page and not ancienne.get_children().exists():
                ancienne.delete()
        # Adresse du site (liens absolus du plan du site, des e-mails) : celle de DJANGO_SITE_URL tant que Wagtail
        # a encore son « localhost » d'installation.
        site = Site.objects.get(is_default_site=True)
        adresse = urlsplit(settings.SITE_URL)
        if site.hostname == "localhost" and adresse.hostname not in (None, "localhost", "127.0.0.1"):
            site.hostname = adresse.hostname
            site.port = adresse.port or (443 if adresse.scheme == "https" else 80)
            site.save()
        return accueil

    def contact(self, accueil):
        existante = accueil.get_children().filter(slug="contact").first()
        if existante:
            return existante.specific
        destinataires = ", ".join(adresse for _, adresse in settings.ADMINS)
        page = ContactPage(
            title="Contact", slug="contact", show_in_menus=True,
            introduction="<p>Une question, une proposition de partenariat, l'envie de rejoindre l'association ? "
                         "Écrivez-nous, nous vous répondrons dans les meilleurs délais.</p>",
            remerciement="<p>Merci, votre message a bien été envoyé. Nous vous répondrons dans les meilleurs "
                         "délais.</p>",
            to_address=destinataires, from_address=parseaddr(settings.DEFAULT_FROM_EMAIL)[1],
            subject="Nouveau message depuis le site de Yeba",
        )
        champs = [
            ("Nom et prénom", "singleline", True, ""),
            ("E-mail", "email", True, ""),
            ("Téléphone", "singleline", False, ""),
            ("Objet", "dropdown", True, "Question\nDevenir membre\nBénévolat ou point focal\nPartenariat\nPresse\nAutre"),
            ("Message", "multiline", True, ""),
        ]
        for ordre, (libelle, genre, requis, choix) in enumerate(champs):
            page.form_fields.add(ChampContact(sort_order=ordre, label=libelle, field_type=genre, required=requis,
                                              choices=choix))
        accueil.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write("   + Contact")
        return page

    def exemples(self, activites, actualites, datacd, reflexion):
        jour = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        a = lambda jours, heure: jour + timedelta(days=jours, hours=heure)  # noqa: E731
        self.creer(activites, ActivitePage, "conference-budget-etat", title="Le budget de l'État expliqué aux citoyens",
                   genre="conference", debut=a(30, 15), fin=a(30, 18), lieu="Lieu à confirmer", projet=reflexion,
                   chapeau="D'où vient l'argent public, où va-t-il, et comment le suivre ? Une conférence suivie d'un "
                           "échange avec le public.",
                   corps=corps(("paragraphe", "<p>Activité d'exemple créée pour essayer le site.</p>")))
        self.creer(activites, ActivitePage, "atelier-acte-de-naissance", title="Atelier : l'acte de naissance pas à pas",
                   genre="atelier", debut=a(45, 10), fin=a(45, 13), lieu="Lieu à confirmer", projet=datacd,
                   chapeau="Où aller, quels documents apporter, combien cela coûte : un atelier pratique pour les "
                           "jeunes parents.",
                   corps=corps(("paragraphe", "<p>Activité d'exemple créée pour essayer le site.</p>")))
        self.creer(activites, ActivitePage, "campagne-90-jours", title="Campagne « 90 jours pour déclarer une naissance »",
                   genre="campagne", debut=a(60, 8), fin=a(90, 17), ville="Kinshasa et Kongo-Central",
                   chapeau="Une campagne de sensibilisation dans les maternités, les marchés et les radios "
                           "communautaires.",
                   corps=corps(("paragraphe", "<p>Activité d'exemple créée pour essayer le site.</p>")))
        self.creer(activites, ActivitePage, "table-ronde-exemple", title="Table ronde : s'informer à l'ère des réseaux sociaux",
                   genre="table_ronde", debut=a(-20, 14), fin=a(-20, 17), lieu="Lieu à confirmer", en_ligne=True,
                   projet=reflexion,
                   chapeau="Journalistes, chercheurs et étudiants ont échangé sur la vérification de l'information.",
                   corps=corps(("paragraphe", "<p>Activité d'exemple créée pour essayer le site.</p>")))
        self.creer(actualites, ActualitePage, "exemple-actualite", title="Les points focaux se préparent",
                   date=timezone.localdate() - timedelta(days=3), projet=datacd,
                   chapeau="Actualité d'exemple : le réseau des points focaux se met en place dans les communes "
                           "de Kinshasa.",
                   corps=corps(("paragraphe", "<p>Actualité d'exemple créée pour essayer le site.</p>")))
