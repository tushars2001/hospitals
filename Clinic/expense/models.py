from django.db import models
from django.db import connection
from ..home.models import dict_fetchall
from datetime import datetime, timedelta
from django.db import connection, transaction, DatabaseError, IntegrityError, OperationalError
import pdb


def get_expense(idexpense):
    sql = """
        SELECT e.`idexpense`,
        e.`idmedicine_type`,
        e.`title`,
        e.`bill_num`,
        e.`expense_date`,
        e.`amount`,
        e.`paid_amount`,
        e.`due_amount`,
        e.`due_on`,
        e.`due_date`,
        e.`notes`,
        e.`dt_created`, 
        mt.`name`
    FROM `clinic`.`expense` e left join `clinic`.`medicine_type` mt on e.idmedicine_type = mt.idmedicine_type
    where e.idexpense = %(idexpense)s and not e.deleted  
        """
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, {'idexpense': idexpense})
        data = dict_fetchall(cursor)
        cursor.close()

    return data


def add_expense(req):
    print(req)
    fields = {}
    expense_id = None

    if len(req['title']) > 0:
        fields['title'] = req['title']
    else:
        fields['title'] = None

    if len(req['bill_num']) > 0:
        fields['bill_num'] = req['bill_num']
    else:
        fields['bill_num'] = None

    if len(req['expense_date']) > 0:
        fields['expense_date'] = req['expense_date']
    else:
        fields['expense_date'] = None

    if len(req['type']) > 0:
        fields['idmedicine_type'] = req['type']
    else:
        fields['idmedicine_type'] = None

    if len(req['amount']) > 0:
        fields['amount'] = req['amount']
    else:
        fields['amount'] = None

    if len(req['paid_amount']) > 0:
        fields['paid_amount'] = req['paid_amount']
    else:
        fields['paid_amount'] = None

    if len(req['due_amount']) > 0:
        fields['due_amount'] = req['due_amount']
    else:
        fields['due_amount'] = None

    if len(req['due_date']) > 0:
        fields['due_date'] = req['due_date']
    else:
        fields['due_date'] = None

    if len(req['due_on']) > 0:
        fields['due_on'] = req['due_on']
    else:
        fields['due_on'] = None

    if len(req['notes']) > 0:
        fields['notes'] = req['notes']
    else:
        fields['notes'] = None

    if 'idexpense' in req and req['idexpense'].isdigit():
        fields['idexpense'] = req['idexpense']

        sql = """
                update `clinic`.`expense`
                SET
                `title` = %(title)s,
                `bill_num` = %(bill_num)s,
                `expense_date` = %(expense_date)s,
                `amount` = %(amount)s,
                `paid_amount` = %(paid_amount)s,
                `due_amount` = %(due_amount)s,
                `due_on` = %(due_on)s,
                `due_date` = %(due_date)s,
                `notes` = %(notes)s
                where idexpense = %(idexpense)s
                """
        expense_id = req['idexpense']
    else:
        sql = """
                INSERT INTO `clinic`.`expense`
                (
                `idmedicine_type`,
                `title`,
                `bill_num`,
                `expense_date`,
                `amount`,
                `paid_amount`,
                `due_amount`,
                `due_on`,
                `due_date`,
                `notes`)
                VALUES
                (
                %(idmedicine_type)s,
                %(title)s,
                %(bill_num)s,
                %(expense_date)s,
                %(amount)s,
                %(paid_amount)s,
                %(due_amount)s,
                %(due_on)s,
                %(due_date)s,
                %(notes)s
                )
                """

    last_id = "SELECT LAST_INSERT_ID()"

    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql, fields)
        data = cursor.fetchall()
        cursor.close()

    if not expense_id:
        with connection.cursor() as cursor:
            cursor.execute(last_id)
            data = cursor.fetchall()
            cursor.close()
        print("!!!! LAST INSERT ID !!!!")
        expense_id = data[0][0]

    return expense_id


def delete_expense(idexpense):
    sql = """
    update `clinic`.`expense` set deleted = 1 where idexpense = %(idexpense)s
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, {'idexpense': idexpense})
        data = cursor.fetchall()
        cursor.close()

    return idexpense
