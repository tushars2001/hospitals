from django.shortcuts import render, redirect
from django.http import JsonResponse
from ..medicine.models import get_types
from . import models
import pdb
import requests
import json
import time
from random import randrange
from datetime import date, timedelta


def admin(request):
    res = {'status': 'success', 'error': '', 'data': {}, 'types': {}}
    return render(request, "reports_admin.html", res)


def revenue(request):
    res = {'status': 'success', 'error': '', 'data': {}, 'types': get_types()}

    if request.method == 'GET' and 'categories' in request.GET and 'fromDate' in request.GET and 'toDate' in request.GET:
        #Filters
        filters = {'categories': request.GET['categories'], 'fromDate': request.GET['fromDate'], 'toDate': request.GET['toDate'] }
        grouping = {}

        if 'group_category' in request.GET and request.GET['group_category'] == 'true':
            grouping['category'] = True
        if 'group_item' in request.GET and request.GET['group_item'] == 'true':
            grouping['item'] = True
        if 'group_patient' in request.GET and request.GET['group_patient'] == 'true':
            grouping['patient'] = True
        if 'group_date' in request.GET and request.GET['group_date'] == 'true':
            grouping['date'] = True
        res['data'] = models.get_data(filters, grouping)
        res['filters'] = filters
        res['grouping'] = grouping
    else:
        res['data'] = models.get_raw_data()

    return render(request, "reports_revenue.html", res)


def expense(request):
    r = request
    res = {'status': 'success', 'error': '', 'data': None, 'report': None, 'added': None, 'types': get_types()}

    if r.method == 'GET' and 'categories' in r.GET and 'fromDate' in r.GET and 'toDate' in r.GET:
        #Filters
        filters = {'categories': r.GET['categories'], 'fromDate': r.GET['fromDate'], 'toDate': r.GET['toDate']}
        res['filters'] = filters
        res['report'] = models.get_expense_data(filters)
    else:
        res['report'] = models.get_expense_raw_data()

    return render(request, "reports_expense.html", res)


def profit_loss(request):
    res = {'status': 'success', 'error': '', 'data': {}, 'types': get_types()}
    r = request
    toDate = date.today().replace(day=1) - timedelta(days=1)
    fromDate = date.today().replace(day=1) - timedelta(days=toDate.day)

    filters = {'categories': None, 'fromDate': str(fromDate), 'toDate': str(toDate)}
    if r.method == 'GET' and 'categories' in r.GET and 'fromDate' in r.GET and 'toDate' in r.GET:
        #Filters
        filters = {'categories': r.GET['categories'], 'fromDate': r.GET['fromDate'], 'toDate': r.GET['toDate'] }
    # res['revenue'] = models.get_data(filters, None)
    # res['expense'] = models.get_expense_data(filters)
    res['filters'] = filters
    res['p_l'] = models.get_p_l(filters.copy())
    return render(request, "profit_loss.html", res)


def is_json(data):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True


def data(request):
    BASE_URL = 'https://www.1mg.com/pharmacy_api_gateway/v4/drug_skus/by_prefix?'
    RELATIVE_PATH = ''
    prefix_terms = ['e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                         'u', 'v', 'w', 'x', 'y', 'z']
    # page:87,prefixa,rec 29
    for i in range(len(prefix_terms)):
        page = 1
        if prefix_terms[i] == 'e':
            page = 304
        while True:
            q_param = "prefix_term=" + prefix_terms[i] + "&page=" + str(page) + "&per_page=30"
            time.sleep(randrange(3,8))
            # MAKE REQUEST:
            raw_result = requests.get(BASE_URL + RELATIVE_PATH + q_param)
            if is_json(raw_result.text):
                # JSON RESPONSE: convert response to JSON
                json_result = json.loads(raw_result.text)
                count = json_result["meta"]['count']

                for j in range(count):
                    type = json_result['data']['skus'][j]['type']
                    name = json_result['data']['skus'][j]['name']
                    price = json_result['data']['skus'][j]['price']
                    short_composition = json_result['data']['skus'][j]['short_composition']

                    models.insert_imports(type, name, price, short_composition)
                    print("inserted, page:" + str(page) + ",prefix" + prefix_terms[i] + ",rec " + str(j))
                if int(count) < 30:
                    break
                else:
                    page = page + 1

    return JsonResponse({'success': True})
