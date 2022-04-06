from django.shortcuts import render, redirect
from django.http import JsonResponse
from ..medicine.models import get_types
from . import models
import pdb


def admin(request):
    r = request
    res = {'status': 'success', 'error': '', 'data': None, 'report': None, 'added': None, 'types': get_types}

    if r.method == 'POST' and 'title' in r.POST and len(r.POST['title']) and 'amount' in r.POST and len(r.POST['amount']):
        res['added'] = models.add_expense(r.POST)

    if r.method == "GET" and 'idexpense' in r.GET:
        res['data'] = models.get_expense(r.GET['idexpense'])

    if r.method == 'GET' and 'categories' in r.GET and 'fromDate' in r.GET and 'toDate' in r.GET:
        #Filters
        filters = {'categories': r.GET['categories'], 'fromDate': r.GET['fromDate'], 'toDate': r.GET['toDate'] }
        res['report'] = models.get_data(filters)
    else:
        res['report'] = models.get_raw_data()

    return render(request, "expense_admin.html", res)
