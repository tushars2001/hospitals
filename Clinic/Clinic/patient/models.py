from django.db import models
from django.db import connection
from ..home.models import dict_fetchall
from datetime import datetime, timedelta
import pdb


def add(postdata):
    fields = postdata
    print(fields)
    if fields['idpatients']:
        sql = """
                update `clinic`.`patients`
                    set `first_name` = %(first_name)s,
                     `last_name` = %(last_name)s,
                     `gender` = %(gender)s,
                     `dob` = %(dob)s,
                     `phone` = %(phone)s,
                     `email` = %(email)s,
                     `address_line_1` = %(address_line_1)s,
                     `address_line_2` = %(address_line_2)s,
                     `address_line_3` = %(address_line_3)s,
                     `city` = %(city)s,
                     `zip` = %(zip)s,
                     `state` = %(state)s,
                     `history` = %(history)s
                      where idpatients = %(idpatients)s
                """

        print(sql)

        with connection.cursor() as cursor:
            cursor.execute(sql, fields)
            data = cursor.fetchall()
            cursor.close()

        fields['patient_id'] = fields['idpatients']
    else:
        sql = """
        INSERT INTO `clinic`.`patients`
            (
            `first_name`,
            `last_name`,
            `gender`,
            `dob`,
            `phone`,
            `email`,
            `address_line_1`,
            `address_line_2`,
            `address_line_3`,
            `city`,
            `zip`,
            `state`,
            `history`)
            VALUES
            (
            %(first_name)s,
            %(last_name)s,
            %(gender)s,
            %(dob)s,
            %(phone)s,
            %(email)s,
            %(address_line_1)s,
            %(address_line_2)s,
            %(address_line_3)s,
            %(city)s,
            %(zip)s,
            %(state)s,
            %(history)s
            );
    
        """

        last_id = "SELECT LAST_INSERT_ID()"

        print(sql)

        with connection.cursor() as cursor:
            cursor.execute(sql, fields)
            data = cursor.fetchall()
            cursor.close()

        with connection.cursor() as cursor:
            cursor.execute(last_id)
            data = cursor.fetchall()
            cursor.close()
        print("!!!! LAST INSERT ID !!!!")
        fields['patient_id'] = data[0][0]

    return fields['patient_id']


def get_patient_by_id(patient_id):
    sql = """
          SELECT `patients`.`idpatients`,
    `patients`.`first_name`,
    `patients`.`last_name`,
    `patients`.`gender`,
    `patients`.`dob`,
    `patients`.`phone`,
    `patients`.`email`,
    `patients`.`address_line_1`,
    `patients`.`address_line_2`,
    `patients`.`address_line_3`,
    `patients`.`city`,
    `patients`.`zip`,
    `patients`.`state`,
    `patients`.`date_created`,
    `patients`.`history`
FROM `clinic`.`patients`
where idpatients=%(patient_id)s
        """
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, {'patient_id': patient_id})
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def search_patients_by_name(first_name, last_name):
    where = 'where 1=0 '
    if len(first_name):
        where = where + " or first_name like '%" + first_name + "%' "

    if len(last_name):
        where = where + " or last_name like '%" + last_name + "%' "
    sql = """
          SELECT `patients`.`idpatients`,
    `patients`.`first_name`,
    `patients`.`last_name`,
    `patients`.`gender`,
    `patients`.`dob`,
    `patients`.`phone`,
    `patients`.`email`,
    `patients`.`address_line_1`,
    `patients`.`address_line_2`,
    `patients`.`address_line_3`,
    `patients`.`city`,
    `patients`.`zip`,
    `patients`.`state`,
    `patients`.`date_created`,
    `patients`.`history`
FROM `clinic`.`patients`
        """ + where
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def search_patients_by_phone(phone):
    where = 'where 1=0 '
    if len(phone):
        where = where + " or phone like '%" + phone + "%' "

    sql = """
          SELECT `patients`.`idpatients`,
    `patients`.`first_name`,
    `patients`.`last_name`,
    `patients`.`gender`,
    `patients`.`dob`,
    `patients`.`phone`,
    `patients`.`email`,
    `patients`.`address_line_1`,
    `patients`.`address_line_2`,
    `patients`.`address_line_3`,
    `patients`.`city`,
    `patients`.`zip`,
    `patients`.`state`,
    `patients`.`date_created`,
    `patients`.`history`
FROM `clinic`.`patients`
        """ + where
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def get_visits_by_id(patient_id):
    sql = """
          SELECT `visits`.`idvisits`,
    `visits`.`idpatients`,
    `visits`.`visit_date`,
    `visits`.`notes`,
    `visits`.`idprescription`
FROM `clinic`.`visits`
where idpatients=%(patient_id)s
order by visit_date desc

        """
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, {'patient_id': patient_id})
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def get_visit_by_visit_id(visit_id):
    sql = """
          SELECT `visits`.`idvisits`,
    `visits`.`idpatients`,
    `visits`.`visit_date`,
    `visits`.`notes`,
    `visits`.`idprescription`
FROM `clinic`.`visits`
where idvisits=%(visit_id)s
order by visit_date desc

        """
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, {'visit_id': visit_id})
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def get_prescription_by_visit(visit_id):
    sql = """
         SELECT 
         m.`name`,
         `p`.`idprescriptions`,
            `p`.`idvisit`,
            `p`.`idmedicins`,
            `p`.`frequency`,
            `p`.`duration`,
            `p`.`quantity`,
            `p`.`notes`,
            `p`.`cost`
        FROM `clinic`.`prescriptions` p, `clinic`.`medicins` m
        where p.idmedicins = m.idmedicins and p.idvisit=%(visit_id)s
        order by p.idprescriptions

        """
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, {'visit_id': visit_id})
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def get_prescriptions_by_patient(patient_id):
    visits = get_visits_by_id(patient_id)
    prescriptions = []
    print(visits)
    for i in range(len(visits)):
        prescription = get_prescription_by_visit(visits[i]['idvisits'])
        prescriptions.append({'visit_id': visits[i]['idvisits'], 'prescription': prescription})

    return prescriptions


def addrx(req):
    print(req)
    fields = {}

    if req['frequency'].isdigit():
        fields['frequency'] = req['frequency']
    else:
        fields['frequency'] = None

    if req['duration'].isdigit():
        fields['duration'] = req['duration']
    else:
        fields['duration'] = None

    if len(req['quantity']) > 0:
        fields['quantity'] = req['quantity']
    else:
        fields['quantity'] = None

    if len(req['notes']) > 0:
        fields['notes'] = req['notes']
    else:
        fields['notes'] = None

    fields['notes'] = req['notes']
    fields['visit_id'] = req['visit_id']
    fields['cost'] = req['cost']

    medicine_id = get_medicine_id(req['medicine_name'])
    fields['medicine_id'] = medicine_id

    sql = """
        INSERT INTO `clinic`.`prescriptions`
        (
        `idvisit`,
        `idmedicins`,
        `frequency`,
        `duration`,
        `quantity`,
        `notes`,
        `cost`)
        VALUES
        (
        %(visit_id)s,
        %(medicine_id)s,
        %(frequency)s,
        %(duration)s,
        %(quantity)s,
        %(notes)s,
        %(cost)s
        )
        """

    with connection.cursor() as cursor:
        cursor.execute(sql, fields)
        data = cursor.fetchall()
        cursor.close()

    return fields


def updateNotes(req):
    print(req)
    fields = {}

    if len(req['notes']) > 0:
        fields['notes'] = req['notes']
    else:
        fields['notes'] = None

    fields['visit_id'] = req['visit_id']

    sql = """
        UPDATE `clinic`.`visits`
        SET
        `notes` = %(notes)s
        WHERE `idvisits` = %(visit_id)s;
        """

    with connection.cursor() as cursor:
        cursor.execute(sql, fields)
        data = cursor.fetchall()
        cursor.close()

    return fields


def deleterx(idprescriptions):
    fields = {'idprescriptions': idprescriptions}

    sql = """
        delete from `clinic`.`prescriptions`
        WHERE `idprescriptions` = %(idprescriptions)s;
        """

    with connection.cursor() as cursor:
        cursor.execute(sql, fields)
        data = cursor.fetchall()
        cursor.close()

    return fields


def delete_visits(visit_id):
    fields = {'visit_id': visit_id}

    sql = """
        delete from `clinic`.`visits`
        WHERE `idvisits` = %(visit_id)s;
        """

    with connection.cursor() as cursor:
        cursor.execute(sql, fields)
        data = cursor.fetchall()
        cursor.close()

    return fields


def get_medicine_id(name):
    medicine_id = None
    sql = """
        SELECT idmedicins FROM clinic.medicins where upper(name) = upper(%(name)s);
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, {'name': name})
        data = cursor.fetchall()
        cursor.close()

    if len(data) == 0:
        sql = """
            INSERT INTO `clinic`.`medicins` (`name`) VALUES (%(name)s)
        """
        last_id = "SELECT LAST_INSERT_ID()"

        print(sql)

        with connection.cursor() as cursor:
            cursor.execute(sql, {'name': name})
            data = cursor.fetchall()
            cursor.close()

        with connection.cursor() as cursor:
            cursor.execute(last_id)
            data = cursor.fetchall()
            cursor.close()
        print("!!!! LAST INSERT ID !!!!")
        medicine_id = data[0][0]

    else:
        medicine_id = data[0][0]

    return medicine_id


def add_visits(patient_id):
    fields = {'patient_id': patient_id}

    sql = """
        INSERT INTO `clinic`.`visits`
        (
            `idpatients`,
            `visit_date`
        )
        VALUES
        (
            %(patient_id)s,
            current_timestamp
        )
        """

    last_id = "SELECT LAST_INSERT_ID()"

    print(sql)

    with connection.cursor() as cursor:
        cursor.execute(sql, fields)
        data = cursor.fetchall()
        cursor.close()

    with connection.cursor() as cursor:
        cursor.execute(last_id)
        data = cursor.fetchall()
        cursor.close()
    print("!!!! LAST INSERT ID !!!!")
    visit_id = data[0][0]

    return visit_id
