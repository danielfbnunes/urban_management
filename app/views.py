from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_202_ACCEPTED, \
    HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_200_OK
from rest_framework_gis.filters import DistanceToPointFilter

from urban_management import queries
from .serializers import OccurrenceSerializer


@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    state, message, data, token = queries.login(request.data)

    if state:
        return Response({"data": data, "token": token}, status=HTTP_202_ACCEPTED)

    return Response({'detail': message}, status=HTTP_404_NOT_FOUND)


@permission_classes((AllowAny,))
class OccurrencesAPIView(generics.ListCreateAPIView):
    queryset = queries.get_all_occurrences()
    serializer_class = OccurrenceSerializer
    filter_backends = (DistanceToPointFilter, DjangoFilterBackend)
    distance_filter_field = 'point'
    filterset_fields = ['author__user__username', 'category']


@api_view(["POST"])
def add_occurrence(request):
    try:
        user_id = get_user_id_from_token(request)
        author = queries.get_author_by_id(user_id)
    except:
        return Response({'detail': 'Only authenticated authors can add occurrences'}, status=HTTP_403_FORBIDDEN)

    state, message, occurrence = queries.add_occurrence(author, request.data)
    if state:
        return Response({"data": occurrence}, status=HTTP_201_CREATED)

    return Response({"detail": message}, status=HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def update_occurrence(request, id):
    user_id = get_user_id_from_token(request)

    if queries.get_user_by_id(user_id).is_superuser:
        state, message, occurrence = queries.update_occurrence(id, request.data)
        if state:
            return Response({"data": occurrence}, status=HTTP_200_OK)
        return Response({"detail": message}, status=HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Only authenticated admins can update an occurrences'}, status=HTTP_403_FORBIDDEN)


def get_user_id_from_token(request):
    auth_token = request.META["HTTP_AUTHORIZATION"].split()[1]
    user_id = Token.objects.get(key=auth_token).user_id

    return user_id
