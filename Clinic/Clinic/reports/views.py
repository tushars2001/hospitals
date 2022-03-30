from django.shortcuts import render, redirect
from django.http import JsonResponse
from ..medicine.models import get_types
from . import models
import pdb
import requests
import json
import time
from random import randrange


def admin(request):
    res = {'status': 'success', 'error': '', 'data': {}, 'types': get_types}
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

    return render(request, "reports_admin.html", res)


def is_json(data):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True


def data(request):
    BASE_URL = 'https://www.1mg.com/pharmacy_api_gateway/v4/drug_skus/by_prefix?'
    RELATIVE_PATH = ''
    prefix_terms = ['a', 'b', 'c']
    # , 'd','e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
    #                     'u', 'v', 'w', 'x', 'y', 'z'
    # page:87,prefixa,rec 29
    for i in range(len(prefix_terms)):
        page = 1
        if prefix_terms[i] == 'a':
            page = 291
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
