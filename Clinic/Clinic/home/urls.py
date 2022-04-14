from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage_view),
    path('schedule/', views.schedule)
    # path('contact/', contact),
    # path('about/', about),
]
