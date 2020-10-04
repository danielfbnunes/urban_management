from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_202_ACCEPTED, \
    HTTP_201_CREATED, HTTP_403_FORBIDDEN

from urban_management import queries
from .serializers import LoginSerializer, UserSerializer


@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    user_serializer = LoginSerializer(data=request.data)
    if not user_serializer.is_valid():
        return Response(user_serializer.errors, status=HTTP_400_BAD_REQUEST)

    user = authenticate(
        username=user_serializer.data['username'],
        password=user_serializer.data['password']
    )

    if not user:
        return Response({'detail': 'Invalid credentials'}, status=HTTP_404_NOT_FOUND)

    token, _ = Token.objects.get_or_create(user=user)
    user_serialized = UserSerializer(user)

    return Response({"data": user_serialized.data, "token": token.key}, status=HTTP_202_ACCEPTED)


@api_view(["POST"])
def add_occurrence(request):
    try:
        auth_token = request.META["HTTP_AUTHORIZATION"].split()[1]
        user_id = Token.objects.get(key=auth_token).user_id
        author = queries.get_author_by_id(user_id)
    except:
        return Response({'detail': 'Only authenticated authors can add occurrences'}, status=HTTP_403_FORBIDDEN)

    state, message, occurrence = queries.add_occurrence(author, request.data)
    if state:
        return Response({"data": occurrence}, status=HTTP_201_CREATED)
    else:
        return Response({"detail": message}, status=HTTP_400_BAD_REQUEST)
