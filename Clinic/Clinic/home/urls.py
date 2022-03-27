from django.urls import path
from .views import homepage_view, contact, about

urlpatterns = [
    path('', homepage_view),
    # path('contact/', contact),
    # path('about/', about),
]
