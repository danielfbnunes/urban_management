from django.urls import path

from app.views import *

urlpatterns = [
    # access
    path("login", login, name="login"),

    # occurrence
    path("add_occurrence", add_occurrence, name="add_occurrence"),
    path("update_occurrence/<int:id>", update_occurrence, name="update_occurrence")
]
