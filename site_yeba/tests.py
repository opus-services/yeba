from datetime import timedelta

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import ActivitePage, ActivitesIndex, ContactPage


@override_settings(ADMINS=[("contact@yeba.cd", "contact@yeba.cd")])
class SiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("peupler_yeba", "--exemples", stdout=open("/dev/null", "w"))

    def test_toutes_les_pages_repondent(self):
        for url in ["/", "/qui-sommes-nous/", "/qui-sommes-nous/gouvernance/", "/projets/", "/projets/data-cd/",
                    "/activites/", "/activites/?type=atelier", "/activites/conference-budget-etat/",
                    "/actualites/", "/actualites/bienvenue/", "/nous-soutenir/", "/contact/", "/mentions-legales/",
                    "/recherche/", "/recherche/?q=budget", "/sitemap.xml", "/robots.txt", "/sante/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_peuplement_relancable(self):
        call_command("peupler_yeba", stdout=open("/dev/null", "w"))
        self.assertEqual(ContactPage.objects.count(), 1)
        self.assertEqual(ActivitePage.objects.filter(slug="conference-budget-etat").count(), 1)

    def test_accueil_montre_projets_et_activites(self):
        reponse = self.client.get("/")
        self.assertContains(reponse, "data.cd")
        self.assertContains(reponse, "Le budget de l&#x27;État expliqué aux citoyens")
        self.assertNotContains(reponse, "s&#x27;informer à l&#x27;ère des réseaux sociaux")  # activité passée

    def test_agenda_separe_a_venir_et_passees(self):
        contexte = self.client.get("/activites/").context
        self.assertNotIn("table-ronde-exemple", [a.slug for a in contexte["a_venir"]])
        self.assertIn("table-ronde-exemple", [a.slug for a in contexte["passees"]])
        filtre = self.client.get("/activites/?type=atelier").context
        self.assertEqual([a.genre for a in filtre["a_venir"]], ["atelier"])

    def test_campagne_en_cours_reste_a_venir(self):
        index = ActivitesIndex.objects.get()
        maintenant = timezone.now()
        index.add_child(instance=ActivitePage(title="En cours", slug="en-cours", genre="campagne",
                                              debut=maintenant - timedelta(days=2), fin=maintenant + timedelta(days=2)))
        self.assertIn("en-cours", [a.slug for a in ActivitePage.a_venir()])

    def test_formulaire_de_contact(self):
        reponse = self.client.post("/contact/", {
            "nom_et_prenom": "Test", "e_mail": "test@exemple.cd", "objet": "Question", "message": "Bonjour",
        })
        self.assertContains(reponse, "votre message a bien été envoyé")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["contact@yeba.cd"])

    def test_formulaire_piege_a_robots(self):
        reponse = self.client.post("/contact/", {
            "nom_et_prenom": "Robot", "e_mail": "r@exemple.cd", "objet": "Question", "message": "Spam",
            "site_internet": "http://spam.example",
        })
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(ContactPage.objects.get().get_submission_class().objects.count(), 0)

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_page_introuvable(self):
        reponse = self.client.get("/nexiste-pas/")
        self.assertEqual(reponse.status_code, 404)
        self.assertContains(reponse, "Page introuvable", status_code=404)
