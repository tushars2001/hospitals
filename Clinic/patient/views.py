from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from . import models
from django.http import HttpResponse, JsonResponse
import pdb
from django.utils.html import escape


def add(request):
    fields2 = [
        {'first_name': '', 'required': True, 'type': 'char'},
        {'last_name': '', 'required': False, 'type': 'char'},
        {'dob': '', 'required': False, 'type': 'date'},
        {'age': '', 'required': False, 'type': 'double'},
        {'phone': '', 'required': False, 'type': 'char'},
        {'email': '', 'required': False, 'type': 'email'},
        {'address1': '', 'required': False, 'type': 'char'},
        {'address2': '', 'required': False, 'type': 'char'},
        {'address3': '', 'required': False, 'type': 'char'},
        {'city': '', 'required': False, 'type': 'char'},
        {'state': '', 'required': False, 'type': 'char'},
        {'zip': '', 'required': False, 'type': 'int'},
        {'history': '', 'required': False, 'type': 'char'},
    ]
    fields = {}
    res = {'status': 'unknown', 'error': '', 'data': {}}
    print(request)
    if request.method == "POST":  # Add patient
        if 'first_name' in request.POST and len(request.POST['first_name']) > 0:
            fields['first_name'] = request.POST['first_name']
        else:
            res['error'] = res['error'] + "First Name is missing."

        if 'last_name' in request.POST:
            fields['last_name'] = request.POST['last_name']
        else:
            fields['last_name'] = None

        if 'gender' in request.POST:
            fields['gender'] = request.POST['gender']
        else:
            fields['gender'] = None

        if 'dob' in request.POST and len(request.POST['dob']):
            fields['dob'] = request.POST['dob']
        else:
            fields['dob'] = None

        if 'age' in request.POST and len(request.POST['age']):
            fields['age'] = request.POST['age']
        else:
            fields['age'] = None

        if 'phone' in request.POST:
            fields['phone'] = request.POST['phone']
        else:
            fields['phone'] = None

        if 'email' in request.POST:
            fields['email'] = request.POST['email']
        else:
            fields['email'] = None

        if 'address_line_1' in request.POST:
            fields['address_line_1'] = request.POST['address_line_1']
        else:
            fields['address1'] = None

        if 'address_line_2' in request.POST:
            fields['address_line_2'] = request.POST['address_line_2']
        else:
            fields['address_line_2'] = None

        if 'address_line_3' in request.POST:
            fields['address_line_3'] = request.POST['address_line_3']
        else:
            fields['address_line_3'] = None

        if 'city' in request.POST:
            fields['city'] = request.POST['city']
        else:
            fields['city'] = None

        if 'state' in request.POST:
            fields['state'] = request.POST['state']
        else:
            fields['state'] = None

        if 'zip' in request.POST and request.POST['zip'].isdigit():
            fields['zip'] = request.POST['zip']
        else:
            fields['zip'] = None

        if 'history' in request.POST:
            fields['history'] = request.POST['history']
        else:
            fields['history'] = None

        if 'idpatients' in request.POST and request.POST['idpatients'].isdigit():
            fields['idpatients'] = request.POST['idpatients']
        else:
            fields['idpatients'] = None

        patient_id = None

        if len(res['error']) == 0:
            if 'idpatients' in request.POST and request.POST['idpatients'].isdigit():
                edit = models.add(fields)
                patient_id = request.POST['idpatients']
                res['status'] = 'Success'
                res['action'] = "Edit"
            else:
                patient_id = models.add(fields)
                res['status'] = 'Success'
                res['action'] = "Add"
                response = redirect("/patient/search/?new=1&patient_id=" + str(patient_id))
                return response

            res['data'] = models.get_patient_by_id(patient_id)
        else:
            res['status'] = 'Failure'

    if request.method == "GET" and 'idpatients' in request.GET:  # Edit patient
        res['data'] = models.get_patient_by_id(request.GET['idpatients'])
        # pdb.set_trace()
        res['action'] = "Edit"

    return render(request, "add.html", res)


def update(request):
    return render(request, "update.html")


def get_patient_by_id(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'patient_id' in request.POST and request.POST['patient_id'].isdigit():
        res['data'] = models.get_patient_by_id(request.POST['patient_id'])
    else:
        if 'patient_id' in request.GET and request.GET['patient_id'].isdigit():
            res['data'] = models.get_patient_by_id(request.GET['patient_id'])
            if 'new' in request.GET and request.GET['new']:
                res['new'] = 1
        else:
            res['error'] = 'Invalid Data provided.'

    return render(request, "search.html", res)


def search_patients_by_name(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'first_name' in request.POST and 'last_name' in request.POST:
        res['data'] = models.search_patients_by_name(request.POST['first_name'], request.POST['last_name'])
    else:
        res['error'] = 'Invalid Data provided.'

    return render(request, "search_names.html", res)


def search_patients_by_phone(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'phone' in request.POST:
        res['data'] = models.search_patients_by_phone(request.POST['phone'])
    else:
        res['error'] = 'Invalid Data provided.'

    return render(request, "search_names.html", res)


def visits(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'patient_id' in request.GET and request.GET['patient_id'].isdigit():
        res['data'] = models.get_visits_by_id(request.GET['patient_id'])
    else:
        res['error'] = 'Invalid Data provided.'

    return JsonResponse(res)


def prescription(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'visit_id' in request.GET and request.GET['visit_id'].isdigit():
        res['data'] = models.get_prescription_by_visit(request.GET['visit_id'])
    else:
        res['error'] = 'Invalid Data provided.'
    pdb.set_trace()
    return JsonResponse(res)


def addrx(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'visit_id' in request.GET and request.GET['visit_id'].isdigit():
        res['data'] = models.addrx(request.GET)
    else:
        res['error'] = 'Invalid Data provided.'

    return JsonResponse(res)


def deleterx(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'idprescriptions' in request.GET and request.GET['idprescriptions'].isdigit():
        res['data'] = models.deleterx(request.GET['idprescriptions'])
        res['data']['idvisit'] = request.GET['idvisit']
    else:
        res['error'] = 'Invalid Data provided.'

    return JsonResponse(res)


def delete_visits(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'visit_id' in request.GET and request.GET['visit_id'].isdigit():
        res['data'] = models.delete_visits(request.GET['visit_id'])
        res['data']['idvisit'] = request.GET['visit_id']
    else:
        res['error'] = 'Invalid Data provided.'

    return JsonResponse(res)


def updateNotes(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'visit_id' in request.GET and request.GET['visit_id'].isdigit():
        res['data'] = models.updateNotes(request.GET)
    else:
        res['error'] = 'Invalid Data provided.'

    return JsonResponse(res)


def updatePrescription(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'visit_id' in request.GET and request.GET['visit_id'].isdigit():
        res['data'] = models.updatePrescription(request.GET)
    else:
        res['error'] = 'Invalid Data provided.'

    return JsonResponse(res)


def add_visits(request):
    res = {'status': 'success', 'error': '', 'data': {}}
    if 'patient_id' in request.GET and request.GET['patient_id'].isdigit():
        res['data'] = models.add_visits(request.GET['patient_id'])
    else:
        res['error'] = 'Invalid Data provided.'

    return JsonResponse(res)


def print_prescription(request):
    res = {'status': 'success', 'error': '', 'data': {}}

    if request.method == 'GET' and 'idvisits' in request.GET and request.GET['idvisits'].isdigit()\
            and 'idpatients' in request.GET and request.GET['idpatients'].isdigit():
        res['data']['prescription_info'] = models.get_prescription_by_visit(request.GET['idvisits'])
        res['data']['patient_info'] = models.get_patient_by_id(request.GET['idpatients'])
        res['data']['visit_info'] = models.get_visit_by_visit_id(request.GET['idvisits'])
    else:
        res['status'] = 'failure'
        res['error'] = "invalid request"

    return render(request, "prescription.html", res)


def print_summary(request):
    res = {'status': 'success', 'error': '', 'data': {}}

    if request.method == 'GET' and 'idpatients' in request.GET and request.GET['idpatients'].isdigit():
        res['data']['patient_info'] = models.get_patient_by_id(request.GET['idpatients'])
        res['data']['visits_info'] = models.get_visits_by_id(request.GET['idpatients'])
        res['data']['prescriptions_info'] = models.get_prescriptions_by_patient(request.GET['idpatients'])
    else:
        res['status'] = 'failure'
        res['error'] = "invalid request"

    return render(request, "patient_summary.html", res)


def schedule_appointment(request):
    res = {'status': 'success', 'error': '', 'data': {}}

    if 'patient_id' in request.POST and request.POST['patient_id'].isdigit():
        res['data'] = models.get_patient_by_id(request.POST['patient_id'])
    else:
        res['error'] = 'Invalid Data provided.'

    return render(request, "schedule_appointment.html", res)
