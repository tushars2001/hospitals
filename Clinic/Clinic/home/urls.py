from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage_view),
    path('schedule/', views.schedule),
    path('availability/', views.get_availability),
    path('slots/', views.get_available_slots),
    path('book_appointment/', views.book_appointment),
    path('get_appointments/', views.get_appointments),
    path('cancel_appointment/', views.cancel_appointment),
    # path('contact/', contact),
    # path('about/', about),
]
