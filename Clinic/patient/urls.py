from django.urls import path
from . import views

urlpatterns = [
    path('', views.add),
    path('add/', views.add),
    path('search/', views.get_patient_by_id),
    path('searchByName/', views.search_patients_by_name),
    path('searchByPhone/', views.search_patients_by_phone),
    path('visits/', views.visits),
    path('visits/add/', views.add_visits),
    path('visits/delete/', views.delete_visits),
    path('visits/prescription/', views.prescription),
    path('visits/addrx/', views.addrx),
    path('visits/deleterx/', views.deleterx),
    path('visits/updateNotes/', views.updateNotes),
    path('print_prescription/', views.print_prescription),
    path('print_summary/', views.print_summary),
    path('schedule/', views.schedule_appointment),
]
