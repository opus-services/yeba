from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.http import urlencode
from wagtail.models import Page


def recherche(request):
    q = request.GET.get("q", "").strip()[:100]
    resultats = Page.objects.live().public().exclude(depth__lte=2).search(q) if q else Page.objects.none()
    page = Paginator(resultats, 12).get_page(request.GET.get("page"))
    return render(request, "site_yeba/recherche.html", {"page": None, "q": q, "resultats": page, "extra": urlencode({"q": q})})


def robots(request):
    lignes = ["User-agent: *", "Disallow: /admin/", "Disallow: /django-admin/", "Disallow: /recherche/",
              f"Sitemap: {settings.SITE_URL}/sitemap.xml"]
    return HttpResponse("\n".join(lignes) + "\n", content_type="text/plain")


def sante(request):
    return JsonResponse({"ok": True})
