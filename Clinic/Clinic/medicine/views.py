from django.shortcuts import render, redirect
from django.http import JsonResponse
from . import models
import pdb
# Create your views here.

def lookup(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'keyword' in request.GET and len(request.GET['keyword']) > 1:
        res['data'] = models.lookup(request.GET['keyword'])
    else:
        res['error'] = 'Invalid Data provided.'

    return JsonResponse(res)


def admin(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    return render(request, "admin.html", res)


def mapping(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    return render(request, "mapping.html", res)


def updates(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    return render(request, "updates.html", res)


def add_items(request):
    res = {'status': 'success', 'error': '', 'data': models.get_types()}
    return render(request, "updates.html", res)


def add_items_add(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if request.method == 'GET' and 'idmedicine_type' in request.GET \
            and 'item_names[]' in request.GET and len(request.GET['item_names[]']):
        if request.GET['idmedicine_type'].isdigit():
            idmedicine_type = request.GET['idmedicine_type']
        else:
            idmedicine_type = None
        added = models.add_items(request.GET.getlist('item_names[]'), idmedicine_type)

        if not added:
            res = {'status': 'failure', 'error': 'Some Error Occurred.', 'data': {}}
        else:
            res = {'status': 'success', 'error': '', 'data': added}

    return JsonResponse(res)


def type(request):
    res = {'status': 'success', 'error': '', 'data': models.get_types()}
    return render(request, "type.html", res)


def type_add(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'name' in request.GET and len(request.GET):
        check_type = models.get_type_by_name(request.GET['name'])
        if check_type:
            res = {'status': 'failure', 'error': 'Category Already Exists', 'data': {}}
        else:
            res['data'] = models.add_type(request.GET['name'])
    else:
        res = {'status': 'failure', 'error': 'Invalid Request', 'data': {}}

    return JsonResponse(res)


def type_delete(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'idmedicine_type' in request.GET and request.GET['idmedicine_type'].isdigit():
        check_type = models.delete_type(request.GET['idmedicine_type'])
        if check_type:
            res = {'status': 'failure', 'error': 'Error Deleting', 'data': {}}
    else:
        res = {'status': 'failure', 'error': 'Invalid Request', 'data': {}}

    return JsonResponse(res)


def type_unmapped(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if request.method == 'POST':
        if 'idmedicins' in request.POST and 'idmedicine_type' in request.POST:
            map = models.map(request.POST['idmedicine_type'], request.POST.getlist('idmedicins'))
        else:
            res = {'status': 'failure', 'error': 'Invalid Data Provided', 'data': {}}
    else:
        res = {'status': 'success', 'error': '', 'data': models.get_unmapped_medicine(),
               'data_type': models.get_types()}

    return render(request, "type_unmapped.html", res)


def type_mapped(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if request.method == 'POST':
        pdb.set_trace()
        if 'idmedicins' in request.POST:
            print("UPDATING NULL!")
            map = models.map(None, request.POST.getlist('idmedicins'))
        else:
            res = {'status': 'failure', 'error': 'Invalid Data Provided', 'data': {}}

    res = {'status': 'success', 'error': '', 'data': models.get_mapped_medicine()}

    return render(request, "type_mapped.html", res)
