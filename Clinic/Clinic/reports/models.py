from django.db import models
from django.db import connection
from ..home.models import dict_fetchall
from django.db import connection, transaction, DatabaseError, IntegrityError, OperationalError
import pdb

# Create your models here.

def get_raw_data():
    sql = """
    SELECT p.idprescriptions,  v.idvisits, v.visit_date, pt.idpatients, pt.first_name,
        pt.last_name, m.idmedicins, m.`name`, mt.idmedicine_type, mt.`name` as category, p.cost FROM clinic.prescriptions p 
        left join clinic.visits v on p.idvisit = v.idvisits
        left join clinic.patients pt on v.idvisits = pt.idpatients
        left join clinic.medicins m on p.idmedicins = m.idmedicins
        left join clinic.medicine_type mt on m.`type` = mt.idmedicine_type
    """

    sql_summary = """
        SELECT sum(p.cost) as totals 
        FROM clinic.prescriptions p 
            left join clinic.visits v on p.idvisit = v.idvisits
            left join clinic.patients pt on v.idvisits = pt.idpatients
            left join clinic.medicins m on p.idmedicins = m.idmedicins
            left join clinic.medicine_type mt on m.`type` = mt.idmedicine_type
        """

    print(sql)
    print(sql_summary)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dict_fetchall(cursor)
        cursor.close()

    with connection.cursor() as cursor:
        cursor.execute(sql_summary)
        data_summary = dict_fetchall(cursor)
        cursor.close()

    return {'data': data, 'summary': data_summary}


def get_data(filters, grouping):
    where = "where 1=1 "

    if 'categories' in filters and len(filters['categories']):
        categories = filters['categories'].split(',')
        where = where + " and (1=2 "
        for i in range(len(categories)):
            if categories[i] == 'unassigned':
                where = where + " or mt.idmedicine_type is null "
            else:
                where = where + " or mt.idmedicine_type = " + categories[i]
        where = where + " ) "

    if 'fromDate' in filters and len(filters['fromDate']):
        where = where + " and v.visit_date >= %(fromDate)s "

    if 'toDate' in filters and len(filters['toDate']):
        where = where + " and v.visit_date <= %(toDate)s"

    fields = """
    p.idprescriptions,  v.idvisits, v.visit_date, pt.idpatients, pt.first_name,
        pt.last_name, m.idmedicins, m.`name`, mt.idmedicine_type, mt.`name` as category, p.cost
    """
    group_by = []
    group_by_clause = ""
    if len(grouping):
        fields = 'sum(p.cost) as cost'
        if 'category' in grouping and grouping['category']:
            fields = fields + ",mt.idmedicine_type, mt.`name` as category "
            group_by.append("mt.idmedicine_type, mt.`name`")
        if 'patient' in grouping and grouping['patient']:
            fields = fields + ",pt.idpatients, pt.first_name, pt.last_name "
            group_by.append("pt.idpatients, pt.first_name, pt.last_name")
        if 'item' in grouping and grouping['item']:
            fields = fields + ",m.idmedicins, m.`name` "
            group_by.append("m.idmedicins, m.`name`")
        if 'date' in grouping and grouping['date']:
            fields = fields + ",v.idvisits, v.visit_date "
            group_by.append("v.idvisits, v.visit_date")
        group_by_clause = "group by " + ",".join(group_by)

    sql = """
    SELECT  """ + fields + """  FROM clinic.prescriptions p
        left join clinic.visits v on p.idvisit = v.idvisits
        left join clinic.patients pt on v.idvisits = pt.idpatients
        left join clinic.medicins m on p.idmedicins = m.idmedicins
        left join clinic.medicine_type mt on m.`type` = mt.idmedicine_type
    """ + where + group_by_clause

    sql_summary = """
        SELECT sum(p.cost) as totals 
        FROM clinic.prescriptions p 
            left join clinic.visits v on p.idvisit = v.idvisits
            left join clinic.patients pt on v.idvisits = pt.idpatients
            left join clinic.medicins m on p.idmedicins = m.idmedicins
            left join clinic.medicine_type mt on m.`type` = mt.idmedicine_type
        """ + where

    print(sql)
    print(sql_summary)
    with connection.cursor() as cursor:
        cursor.execute(sql, filters)
        data = dict_fetchall(cursor)
        cursor.close()

    with connection.cursor() as cursor:
        cursor.execute(sql_summary, filters)
        data_summary = dict_fetchall(cursor)
        cursor.close()

    return {'data': data, 'summary': data_summary}


def insert_imports(type, name, price, short_composition):
    fields = {'type': type, 'name': name, 'price': price, 'short_composition': short_composition }

    sql = """
            INSERT INTO `clinic`.`medicine_import`
            (
            `type`,
            `price`,
            `name`,
            `short_composition`)
            VALUES
            (
            %(type)s,
            %(price)s,
            %(name)s,
            %(short_composition)s
            )

            """

    # print(sql)

    with connection.cursor() as cursor:
        cursor.execute(sql, fields)
        data = cursor.fetchall()
        cursor.close()

    return True

