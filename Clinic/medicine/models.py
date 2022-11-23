from django.db import models
from django.db import connection
from ..home.models import dict_fetchall
from datetime import datetime, timedelta
from django.db import connection, transaction, DatabaseError, IntegrityError, OperationalError
import pdb


def lookup(keyword):
    sql = """
    SELECT idmedicins, `name` FROM clinic.medicins
    where upper(`name`) like upper('""" + keyword + """%')
            """
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def get_types():
    sql = """
        SELECT `medicine_type`.`idmedicine_type`,
            `medicine_type`.`name`
        FROM `clinic`.`medicine_type`;
        """
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def get_type_by_name(name):
    sql = """
           SELECT count(*) as cnt
           FROM `clinic`.`medicine_type`
           where upper(name) = upper(%(name)s)
           """
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, {'name': name})
        data = dict_fetchall(cursor)
        cursor.close()

    return data[0]['cnt']


def get_type_by_id(idmedicine_type):
    sql = """
           SELECT count(*) as cnt
           FROM `clinic`.`medicine_type`
           where idmedicine_type = %(idmedicine_type)s
           """
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, {'idmedicine_type': idmedicine_type})
        data = dict_fetchall(cursor)
        cursor.close()

    return data[0]['cnt']


def add_type(name):
    fields = {'name': name}

    sql = """
        INSERT INTO `clinic`.`medicine_type`
        (
            `name`
        )
        VALUES
        (
            %(name)s
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
    idmedicine_type = data[0][0]

    return idmedicine_type


def delete_type(idmedicine_type):
    fields = {'idmedicine_type': idmedicine_type}

    sql = """
            delete from `clinic`.`medicine_type`
            WHERE `idmedicine_type` = %(idmedicine_type)s;
            """

    with connection.cursor() as cursor:
        cursor.execute(sql, fields)
        data = cursor.fetchall()
        cursor.close()

    return get_type_by_id(idmedicine_type)


def get_unmapped_medicine():
    sql = """
        SELECT idmedicins, `name` 
    FROM clinic.medicins 
    where length(`type`) is null or length(`type`) < 1;
    """

    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def get_mapped_medicine():
    sql = """
        SELECT m.idmedicins, m.`name`, t.idmedicine_type, t.`name` type_name
        FROM clinic.medicins m, clinic.medicine_type t
        where t.idmedicine_type = m.`type` and
         length(m.`type`) is not null and length(m.`type`) > 0;
    """

    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def map(idmedicine_type, idmedicines):
    sql = """
    update clinic.medicins
    set `type` = %(idmedicine_type)s
    where idmedicins in (""" + ','.join(idmedicines) + """)
    """

    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, {'idmedicine_type': idmedicine_type})
        cursor.close()

    return ''


def add_items(names, type):
    fields = {'name': None, 'type': type}
    res = {'added': [], 'not_added': []}
    for i in range(len(names)):
        fields['name'] = names[i].strip()
        sql = """
            INSERT INTO `clinic`.`medicins`
            (
                `name`, `type`
            )
            VALUES
            (
                %(name)s, %(type)s
            )
            """

        last_id = "SELECT LAST_INSERT_ID()"

        print(sql)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, fields)
                data = cursor.fetchall()
                cursor.close()

            with connection.cursor() as cursor:
                cursor.execute(last_id)
                data = cursor.fetchall()
                cursor.close()
            print("!!!! LAST INSERT ID !!!!")
            idmedicins = data[0][0]
            res['added'].append(fields['name'] + ": " + str(idmedicins))
        except DatabaseError as e:
            res['not_added'].append(fields['name'] + ": " + str(e).split(",")[1].replace("'", ""))

    return res
