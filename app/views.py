from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_202_ACCEPTED, \
    HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_200_OK
from rest_framework_gis.filters import DistanceToPointFilter

from urban_management import queries
from .serializers import OccurrenceSerializer, LoginSerializer, LoginResponseSerializer, ErrorResponseSerializer, \
    AddOccurrenceSerializer, OccurrenceResponseSerializer, UpdateOccurrenceSerializer


@swagger_auto_schema(method="post", request_body=LoginSerializer,
                     responses={HTTP_202_ACCEPTED: openapi.Response('Login successful', LoginResponseSerializer),
                                HTTP_404_NOT_FOUND: openapi.Response('Login rejected', ErrorResponseSerializer)})
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    state, error, data = queries.login(request.data)

    if state:
        return Response(data, status=HTTP_202_ACCEPTED)

    return Response(error, status=HTTP_404_NOT_FOUND)


@permission_classes((AllowAny,))
class OccurrencesAPIView(generics.ListCreateAPIView):
    queryset = queries.get_all_occurrences()
    serializer_class = OccurrenceSerializer
    filter_backends = (DistanceToPointFilter, DjangoFilterBackend)
    distance_filter_field = 'point'
    filterset_fields = ['author__user__username', 'category']


@swagger_auto_schema(method="post", request_body=AddOccurrenceSerializer,
                     responses={
                         HTTP_201_CREATED: openapi.Response('Occurrence created', OccurrenceResponseSerializer),
                         HTTP_400_BAD_REQUEST: openapi.Response('The request body contains errors',
                                                                ErrorResponseSerializer),
                         HTTP_403_FORBIDDEN: openapi.Response('Only authenticated authors can add occurrences',
                                                              ErrorResponseSerializer)})
@api_view(["POST"])
def add_occurrence(request):
    try:
        user_id = get_user_id_from_token(request)
        author = queries.get_author_by_id(user_id)
    except:
        error = ErrorResponseSerializer({'detail': 'Only authenticated authors can add occurrences'}).data
        return Response(error, status=HTTP_403_FORBIDDEN)

    state, error, data = queries.add_occurrence(author, request.data)
    if state:
        return Response(data, status=HTTP_201_CREATED)

    return Response(error, status=HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="put", request_body=UpdateOccurrenceSerializer,
                     responses={
                         HTTP_200_OK: openapi.Response('Occurrence updated', OccurrenceResponseSerializer),
                         HTTP_400_BAD_REQUEST: openapi.Response('The request body contains errors',
                                                                ErrorResponseSerializer),
                         HTTP_403_FORBIDDEN: openapi.Response('Only authenticated admins can add occurrences',
                                                              ErrorResponseSerializer)})
@api_view(["PUT"])
def update_occurrence(request, id):
    user_id = get_user_id_from_token(request)

    if queries.get_user_by_id(user_id).is_superuser:
        state, error, data = queries.update_occurrence(id, request.data)
        if state:
            return Response(data, status=HTTP_200_OK)
        return Response(error, status=HTTP_400_BAD_REQUEST)

    error = ErrorResponseSerializer({'detail': 'Only authenticated admins can update an occurrences'}).data
    return Response(error, status=HTTP_403_FORBIDDEN)


def get_user_id_from_token(request):
    auth_token = request.META["HTTP_AUTHORIZATION"].split()[1]
    user_id = Token.objects.get(key=auth_token).user_id

    return user_id
