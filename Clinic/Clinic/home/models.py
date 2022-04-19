from django.db import models
from django.db import connection
from datetime import datetime, timedelta
import pdb


def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def recent_updates():
    sql = """
        select distinct p.idpatients, p.first_name, p.last_name from clinic.patients p,
        (SELECT idpatients, date_created FROM clinic.patients 
        union
        select idpatients, visit_date FROM clinic.visits 
        union
        select v.idpatients, p.date_created FROM clinic.prescriptions p,  clinic.visits v where p.idvisit=v.idvisits
        order by 2 desc 
        limit 5) main
        where p.idpatients = main.idpatients

    """

    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def add_schedule(records, username):
    inserted = 0

    sql = "delete from `clinic`.`schedule` where username = %(username)s"

    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, {'username': username})
        cursor.close()

    for record in records:
        if record['time_from']:
            am_pm = 0
            if record['time_from'].split(' ')[1] == 'PM':
                am_pm = 12
            record['time_from'] = str(int(record['time_from'].split(' ')[0].split(':')[0]) + am_pm + \
                                  int(record['time_from'].split(' ')[0].split(':')[1])/100)

            if record['time_to']:
                am_pm = 0
                if record['time_to'].split(' ')[1] == 'PM':
                    am_pm = 12
                record['time_to'] = str(int(record['time_to'].split(' ')[0].split(':')[0]) + am_pm + \
                                      int(record['time_to'].split(' ')[0].split(':')[1]) / 100)

        sql = """
               INSERT INTO `clinic`.`schedule`
                (
                `username`,
                `type`,
                `day_name`,
                `day_date`,
                `time_from`,
                `time_to`,
                `full_day`,
                `available`)
                VALUES
                (
                %(username)s,
                %(type)s,
                %(day_name)s,
                %(day_date)s,
                %(time_from)s,
                %(time_to)s,
                %(full_day)s,
                %(available)s)
            """

        print(sql)
        print(record)
        with connection.cursor() as cursor:
            cursor.execute(sql, record)
            cursor.close()
            inserted = inserted + 1

    return inserted


def get_specific_non_availability(dt, username):
    sql = """
        SELECT count(*) as availability FROM clinic.schedule where day_date = %(dt)s and username = %(username)s and
         `type` = 'D' and available = 'N' and full_day = 'Y'
    """
    print(sql)

    with connection.cursor() as cursor:
        cursor.execute(sql, {'dt': dt, 'username': username})
        data = dict_fetchall(cursor)
        cursor.close()

    return data[0]['availability']


def get_general_availability(dt, username):
    day = datetime.strptime(dt, '%Y-%m-%d').strftime('%A').lower()+'s'
    sql = """
            SELECT count(*) as availability FROM clinic.schedule where day_name = %(day)s 
            and `type` = 'W' and available = 'Y' and username = %(username)s
        """
    print(sql)

    with connection.cursor() as cursor:
        cursor.execute(sql, {'day': day, 'username': username})
        data = dict_fetchall(cursor)
        cursor.close()

    return data[0]['availability']


def get_slot_availability(dt, username):
    return True


def specific_availability(dt, username):
    sql = """
            SELECT count(*) as availability FROM clinic.schedule where day_date = %(dt)s and username = %(username)s and
             `type` = 'D' and available = 'Y'
        """
    print(sql)

    with connection.cursor() as cursor:
        cursor.execute(sql, {'dt': dt, 'username': username})
        data = dict_fetchall(cursor)
        cursor.close()

    return data[0]['availability']


def get_schedule(username):
    sql = """
            SELECT `schedule`.`idschedule`,
        `schedule`.`username`,
        `schedule`.`type`,
        IFNULL(`schedule`.`day_name`,'') as day_name,
        IFNULL(DATE_FORMAT(`schedule`.`day_date`,'%%Y-%%m-%%d'),'') as day_date,
        case 
        when time_from >= 13 
        then replace(concat(format(round(time_from - 12,2),2), ' PM'),'.',':')
        when time_from >= 12 and time_from < 13
        then replace(concat(format(round(time_from,2),2), ' NOON'), '.',':')
        when time_from is null then ''
        else replace(concat(format(round(time_from,2),2), ' AM'), '.', ':') 
        end as time_from ,
        case 
        when time_to >= 13 
        then replace(concat(format(round(time_to - 12,2),2), ' PM'),'.',':')
        when time_to >= 12 and time_to < 13
        then replace(concat(format(round(time_to,2),2), ' NOON'), '.',':')
        when time_to is null then ''
        else replace(concat(format(round(time_to,2),2), ' AM'), '.', ':') 
        end as time_to ,
        IFNULL(`schedule`.`full_day`,'') full_day,
        IFNULL(`schedule`.`available`,'') available
    FROM clinic.schedule where username = %(username)s order by 1 
        """

    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, {'username': username})
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def get_available_slots(dt, username, reason):
    data = []
    slots = []

    if reason == 'general_availability':
        day_name = datetime.strptime(dt, '%Y-%m-%d').strftime('%A').lower()+'s'
        sql = "SELECT time_from, time_to FROM clinic.schedule where username = %(username)s and day_name = %(day_name)s order by idschedule"

        print(sql)
        with connection.cursor() as cursor:
            cursor.execute(sql, {'username': username, 'day_name': day_name})
            data = dict_fetchall(cursor)
            cursor.close()

    if reason == 'specific_availability':
        sql = """
            SELECT time_from, time_to FROM clinic.schedule where username = %(username)s and day_date = %(dt)s and 
            `type`='D' and available='Y' order by idschedule;
        """
        print(sql)
        with connection.cursor() as cursor:
            cursor.execute(sql, {'username': username, 'dt': dt})
            data = dict_fetchall(cursor)
            cursor.close()
    for slot in range(23):
        for record in data:
            if record['time_from'] <= slot < record['time_to']:
                if not is_booked(dt, slot, username):
                    slots.append(slot)
            if record['time_from'] <= (slot + .3) < record['time_to']:
                if not is_booked(dt, (slot + .3), username):
                    slots.append(slot + .3)

    return slots


def is_booked(dt, slot, username):
    sql = """
    SELECT count(*) as cnt FROM clinic.appointments where username = %(username)s and status = 'S' 
    and dt = %(dt)s and from_time <= %(slot)s and %(slot)s < to_time
    """
    data = []
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, {'username': username, 'dt': dt, 'slot': slot})
        data = dict_fetchall(cursor)
        cursor.close()

    return data[0]['cnt']


def book_appointment(dt, time_from, time_to, patient_id, username):
    data = []
    appointment_id = None
    fields = {'dt': dt, 'time_from': time_from, 'time_to': time_to, 'idpatients':patient_id, 'username': username}
    sql = """
        INSERT INTO `clinic`.`appointments`
        (
        `username`,
        `idpatients`,
        `dt`,
        `from_time`,
        `to_time`,
        `status`)
        VALUES
        (
        %(username)s,
        %(idpatients)s,
        %(dt)s,
        %(time_from)s,
        %(time_to)s,
        'S'
        );
    """
    last_id = "SELECT LAST_INSERT_ID()"

    print(sql)

    with connection.cursor() as cursor:
        cursor.execute(sql, fields)
        cursor.close()

    with connection.cursor() as cursor:
        cursor.execute(last_id)
        data = cursor.fetchall()
        cursor.close()
    print("!!!! LAST INSERT ID !!!!")
    appointment_id = data[0][0]

    return appointment_id


def cancel_appointment(idappointments):
    data = []
    fields = {'idappointments': idappointments}
    sql = """
        update `clinic`.`appointments`
        set `status` = 'C'
        where idappointments = %(idappointments)s
    """

    print(sql)

    with connection.cursor() as cursor:
        cursor.execute(sql, fields)
        cursor.close()

    appointment_id = idappointments

    return appointment_id


def get_appointments(patient_id = None, username = None, dt_from = None, dt_to=None, status=None):
    data = []

    where = " where a.idpatients = p.idpatients "

    if patient_id:
        where = where + " and a.idpatients = %(patient_id)s "

    if username:
        where = where + " and a.username = %(username)s "

    if dt_from:
        where = where + " and a.dt >= %(dt_from)s "

    if dt_to:
        where = where + " and a.dt <= %(dt_to)s "

    if status:
        where = where + " and a.status = %(status)s "

    fields = {'patient_id': patient_id, 'username': username, 'dt_from': dt_from, 'dt_to': dt_to, 'status': status}

    sql = """
            SELECT a.`idappointments`,
            a.`username`,
            a.`idpatients`,
            a.`dt`,
            a.`from_time`,
            a.`to_time`,
            a.`status`,
            p.`first_name`,
            p.`last_name`
        FROM `clinic`.`appointments` a, `patients` p
    """ + where + " order by dt, from_time"

    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, fields )
        data = dict_fetchall(cursor)
        cursor.close()

    return data
