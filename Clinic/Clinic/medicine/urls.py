from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin),
    path('type/', views.type),
    path('type/add/', views.type_add),
    path('type/delete/', views.type_delete),
    path('type/unmapped/', views.type_unmapped),
    path('type/mapped/', views.type_mapped),
    path('mapping/', views.mapping),
    path('add_items/', views.add_items),
    path('updates/', views.updates),
    path('lookup/', views.lookup),
    # path('search/', get_patient_by_id),
    # path('visits/', visits),
    # path('visits/prescription/', prescription),
]
