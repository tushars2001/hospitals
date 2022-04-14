from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from . import models


@staff_member_required(login_url='/identity/')
def homepage_view(request):
    recent_data = models.recent_updates()
    return render(request, "homepage.html", {'recent_data': recent_data})


def contact(request):
    return render(request, "contact.html")


def about(request):
    return render(request, "about.html")


@staff_member_required(login_url='/identity/')
def schedule(request):
    return render(request, "schedule.html")

