from datetime import date
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from . import models
import pdb
from dateutil.parser import parse
from django.http import HttpResponse, JsonResponse


@staff_member_required(login_url='/identity/')
def homepage_view(request):
    recent_data = models.recent_updates()
    username = 'admin'
    today = date.today().strftime("%Y-%m-%d")
    appointments = models.get_appointments(None, username, today, None, 'S')
    return render(request, "homepage.html", {'recent_data': recent_data, 'appointments': appointments})


def contact(request):
    return render(request, "contact.html")


def about(request):
    return render(request, "about.html")


@staff_member_required(login_url='/identity/')
def schedule(request):
    username = 'admin'
    if request.method == 'POST':
        r = request.POST
        records = []
        days = ['mondays', 'tuesdays', 'wednesdays', 'thursdays', 'fridays', 'saturdays', 'sundays']
        record = {'username': username, 'type': None, 'day_name': None, 'day_date': None,
                  'time_from': None, 'time_to': None, 'full_day': None, 'available': None}

        for day in days:
            if day + '_availability' in r and r[day + '_availability'] == 'checked': # if out on full days
                record = {'username': username, 'type': 'W', 'day_name': day, 'day_date': None,
                          'time_from': None, 'time_to': None, 'full_day': 'Y', 'available': 'N'}
                records.append(record.copy())
            else: # else add specific times for days for 4 var
                for i in range(3):
                    if r[day + '_' + str((i+1)) + '_1'] != 'NA' and r[day + '_' + str((i+1)) + '_2'] != 'NA':
                        record = {'username': username, 'type': 'W', 'day_name': day, 'day_date': None,
                                  'time_from': r[day + '_' + str((i+1)) + '_1'],
                                  'time_to': r[day + '_' + str((i+1)) + '_2'], 'full_day': 'N', 'available': 'Y'}
                        records.append(record.copy())

        for key, value in request.POST.items():
            if key.startswith('specific_non_availability_date_') and is_date(value):
                num = key.split('_')[-1]
                # check if whole day not available
                if 'specific_non_availability_whole_day_' + num in r and r['specific_non_availability_whole_day_' + num] == 'on':
                    record = {'username': username, 'type': 'D', 'day_name': None, 'day_date': value,
                              'time_from': None, 'time_to': None, 'full_day': 'Y', 'available': 'N'}
                    records.append(record.copy())
                else: # else insert specific times on days
                    if 'specific_non_availability_' + num + '_1' in r and 'specific_non_availability_' + num + '_2' \
                        in r and r['specific_non_availability_' + num + '_1'] != 'NA' \
                            and r['specific_non_availability_' + num + '_2'] != 'NA':
                        record = {'username': username, 'type': 'D', 'day_name': None, 'day_date': value,
                                  'time_from': r['specific_non_availability_' + num + '_1'],
                                  'time_to': r['specific_non_availability_' + num + '_2'], 'full_day': 'N', 'available': 'N'}
                        records.append(record.copy())

            if key.startswith('specific_availability_date_') and is_date(value):
                num = key.split('_')[-1]
                if 'specific_availability_' + num + '_1' in r and 'specific_availability_' + num + '_2' \
                    in r and r['specific_availability_' + num + '_1'] != 'NA' \
                        and r['specific_availability_' + num + '_2'] != 'NA':
                    record = {'username': username, 'type': 'D', 'day_name': None, 'day_date': value,
                              'time_from': r['specific_availability_' + num + '_1'],
                              'time_to': r['specific_availability_' + num + '_2'], 'full_day': 'N', 'available': 'Y'}
                    records.append(record.copy())
        if len(records):
            add = models.add_schedule(records, username)
    schedule_data = models.get_schedule(username)
    # pdb.set_trace()
    return render(request, "schedule.html", {'schedule_data': schedule_data})


def get_availability(request):
    data = {}
    dt = None
    username = 'admin'
    if request.method == 'POST' and 'dt' in request.POST and is_date(request.POST['dt']):
        dt = request.POST['dt']
    elif request.method == 'GET' and 'dt' in request.GET and is_date(request.GET['dt']):
        dt = request.GET['dt']
    else:
        return JsonResponse({'status': 'failure', 'message': 'Invalid Request'})

    data = check_availability(dt, username)

    return JsonResponse(data)


def check_availability(dt, username):
    data = {'date': dt}

    specific_non_availability = models.get_specific_non_availability(dt, username)
    if specific_non_availability:
        data['available'] = False
        data['reason'] = 'specific_non_availability'
    else:
        general_availability = models.get_general_availability(dt, username)
        slot_availability = models.get_slot_availability(dt, username)
        if general_availability:
            if slot_availability:
                data['available'] = True
                data['reason'] = 'general_availability'
            else:
                data['available'] = False
                data['reason'] = 'slot_availability'
        else:
            specific_availability = models.specific_availability(dt, username)
            if specific_availability:
                if slot_availability:
                    data['available'] = True
                    data['reason'] = 'specific_availability'
                else:
                    data['available'] = False
                    data['reason'] = 'slot_availability'
            else:
                data['available'] = False
                data['reason'] = 'general_availability'
    return data


def get_available_slots(request):
    data = {}
    dt = None
    username = 'admin'
    if request.method == 'POST' and 'dt' in request.POST and is_date(request.POST['dt']):
        dt = request.POST['dt']
    elif request.method == 'GET' and 'dt' in request.GET and is_date(request.GET['dt']):
        dt = request.GET['dt']
    else:
        return JsonResponse({'status': 'failure', 'message': 'Invalid Request'})

    data['date'] = dt
    check = check_availability(dt, username)
    if check['available']:
        data['slots'] = models.get_available_slots(dt, username, check['reason'])

    return JsonResponse(data)


def book_appointment(request):
    res = {}
    r = request.POST
    username = 'admin'
    if request.method == 'POST' and 'dt' in r and 'time_from' in r and 'time_to' in r and 'patient_id' in r:
        res = f_book_appointment(r['dt'], r['time_from'], r['time_to'], r['patient_id'], username)
    else:
        res = {'status': 'failure', 'message': 'Invalid Request', 'data': {}}

    return JsonResponse(res)


def cancel_appointment(request):
    res = {}
    r = request.POST
    username = 'admin'
    if request.method == 'POST' and 'idappointments' in r :
        res['idappointments'] = models.cancel_appointment(r['idappointments'])
    else:
        res = {'status': 'failure', 'message': 'Invalid Request', 'data': {}}

    return JsonResponse(res)


def f_book_appointment(dt, time_from, time_to, patient_id, username):
    """

    :rtype: object
    """
    res = {'dt': dt, 'time_from': time_from, 'time_to': time_to,
           'appointment_id': models.book_appointment(dt, time_from, time_to, patient_id, username)}

    return res


def get_appointments(request):
    r = request.GET
    res = {}
    if request.method == 'GET' and 'patient_id' in r and 'username' in r and 'date_from' in r and \
            'date_to' in r and 'status' in r:
        res['data'] = models.get_appointments(r['patient_id'], r['username'], r['date_from'], r['date_to'], r['status'])
    else:
        res = {'status': 'failure', 'message': 'Invalid Request'}

    return JsonResponse(res)


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False
