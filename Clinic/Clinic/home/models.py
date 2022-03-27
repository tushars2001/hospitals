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
