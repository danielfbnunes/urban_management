from django.urls import path

from app.views import *

urlpatterns = [
    # access
    path("login", login),

    # occurrence
    path("get_occurrence", OccurrencesAPIView.as_view()),
    path("add_occurrence", add_occurrence),
    path("update_occurrence/<int:id>", update_occurrence)
]
