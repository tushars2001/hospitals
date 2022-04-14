from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin),
    path('data/', views.data),
    path('revenue/', views.revenue),
    path('expense/', views.expense),
    path('profit-loss/', views.profit_loss),
    # path('search/', get_patient_by_id),
    # path('visits/', visits),
    # path('visits/prescription/', prescription),
]
