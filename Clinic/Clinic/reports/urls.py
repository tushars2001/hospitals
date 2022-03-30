from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin),
    path('data/', views.data)
    # path('search/', get_patient_by_id),
    # path('visits/', visits),
    # path('visits/prescription/', prescription),
]
