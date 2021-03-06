from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_202_ACCEPTED, \
    HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_200_OK
from rest_framework_gis.filters import DistanceToPointFilter

from urban_management import queries
from .serializers import OccurrenceSerializer, LoginSerializer, LoginResponseSerializer, ErrorResponseSerializer, \
    AddOccurrenceSerializer, OccurrenceResponseSerializer, UpdateOccurrenceSerializer


@swagger_auto_schema(method="post", request_body=LoginSerializer,
                     responses={HTTP_202_ACCEPTED: openapi.Response('Login successful', LoginResponseSerializer),
                                HTTP_400_BAD_REQUEST: openapi.Response('Login rejected', ErrorResponseSerializer)})
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    """
    Login in the API.
    :param request: Credentials to the login.
    :return: Response 202 and JSON with the username and token, if the login was accepted.
             Response 400 if the credentials are wrong or if the request body doesnt follow the guidelines.
    """
    state, error, data = queries.login(request.data)

    if state:
        return Response(data, status=HTTP_202_ACCEPTED)

    return Response(error, status=HTTP_400_BAD_REQUEST)


@permission_classes((AllowAny,))
class OccurrencesAPIView(generics.ListCreateAPIView):
    """
    Filter occurrences based on the category, author and location range.
    """
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
    """
    Create a new occurrence. NOTE: the authenticated user must be an author.
    :param request: Data related to the occurrence that will be created.
    :return: Response 201 with the created occurrence.
             Response 403 if the authenticated user is not an author.
             Response 400 if the request body doesnt follow the guidelines or if there was any error creating the
             occurrence.
    """
    try:
        user_id = get_user_id_from_token(request)
        # the authenticated user must be an author
        author = queries.get_author_by_id(user_id)
    except:
        error = ErrorResponseSerializer({'detail': 'Only authenticated authors can add occurrences'}).data
        return Response(error, status=HTTP_403_FORBIDDEN)

    try:
        data = queries.add_occurrence(author, request.data)
        return Response(data, status=HTTP_201_CREATED)
    except Exception as e:
        error = ErrorResponseSerializer({'detail': str(e)}).data
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
    """
    Update an occurrence. NOTE: the authenticated user must be an admin.
    :param request: Data with the new status for the occurrence.
    :param id: Id of the occurrence to update.
    :return: Response 200 and the updated occurrence if everything went fine.
             Response 403 if the authenticated user is not an admin.
             Response 400 if the request body doesnt follow the guidelines, if there was any error updating the
             occurrence or if there isn't any occurrence with the id passed.
    """
    user_id = get_user_id_from_token(request)

    if queries.get_user_by_id(user_id).is_superuser:
        try:
            data = queries.update_occurrence(id, request.data)
            return Response(data, status=HTTP_200_OK)
        except Exception as e:
            error = ErrorResponseSerializer({'detail': str(e)}).data
            return Response(error, status=HTTP_400_BAD_REQUEST)

    error = ErrorResponseSerializer({'detail': 'Only authenticated admins can update an occurrences'}).data
    return Response(error, status=HTTP_403_FORBIDDEN)


def get_user_id_from_token(request):
    auth_token = request.META["HTTP_AUTHORIZATION"].split()[1]
    user_id = Token.objects.get(key=auth_token).user_id

    return user_id
