from django.urls import path

from app.views import *

urlpatterns = [
    # access
    path("login", login, name="login"),

    # post request
    path("add_occurrence", add_occurrence, name="add_occurrence")
]
