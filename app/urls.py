from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from app.views import *

schema_view = get_schema_view(
    openapi.Info(
        title="Urban Management API",
        default_version="v1",
        description="Urban Management is an API that allows users to report occurrences, update their status and "
                    "search for created occurrences based on some filters "
    ),
    permission_classes=(AllowAny,),
    public=True)

urlpatterns = [
    # access
    path("login", login),

    # occurrence
    path("get_occurrence", OccurrencesAPIView.as_view()),
    path("add_occurrence", add_occurrence),
    path("update_occurrence/<int:id>", update_occurrence),

    path('docs/', schema_view.with_ui('swagger', cache_timeout=0))
]
