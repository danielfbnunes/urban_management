from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.authtoken.models import Token

from app.models import Author
from app.models import Occurrence
from app.serializers import OccurrenceSerializer, UserSerializer, LoginSerializer, ErrorResponseSerializer, \
    LoginResponseSerializer, AddOccurrenceSerializer, UpdateOccurrenceSerializer


def login(data):
    login_serializer = LoginSerializer(data=data)
    if not login_serializer.is_valid():
        response = ErrorResponseSerializer({'detail': 'Invalid body'}).data
        return False, response, None

    user = authenticate(
        username=login_serializer.data["username"],
        password=login_serializer.data["password"]
    )

    if not user:
        response = ErrorResponseSerializer({'detail': 'Invalid credentials'}).data
        return False, response, None

    token, _ = Token.objects.get_or_create(user=user)
    data = UserSerializer(user).data

    response = LoginResponseSerializer({'data': data, 'token': token}).data
    return True, None, response


def get_all_occurrences():
    return Occurrence.objects.all()


def get_author_by_id(id):
    return Author.objects.get(user_id=id)


def get_user_by_id(id):
    return User.objects.get(id=id)


@transaction.atomic()
def add_occurrence(author, data):
    add_occurrence_serializer = AddOccurrenceSerializer(data=data)
    if not add_occurrence_serializer.is_valid():
        raise Exception('Invalid body')

    description = add_occurrence_serializer.data["description"]
    latitude = add_occurrence_serializer.data["latitude"]
    longitude = add_occurrence_serializer.data["longitude"]
    category = add_occurrence_serializer.data["category"]

    try:
        occurrence = Occurrence.objects.create(author=author, description=description,
                                               point=f"POINT({latitude} {longitude})", category=category)

        data = OccurrenceSerializer(occurrence).data
        response = {'data': data}
    except:
        raise Exception('Error creating occurrence')

    return response


@transaction.atomic()
def update_occurrence(id, data):
    update_occurrence_serializer = UpdateOccurrenceSerializer(data=data)
    if not update_occurrence_serializer.is_valid():
        raise Exception('Invalid body')

    status = update_occurrence_serializer.data["status"]

    occurrence = Occurrence.objects.filter(id=id)

    if not occurrence.exists():
        raise Exception(f"Occurrence with id {id} doesnt exist")

    try:
        occurrence.update(status=status)

        occurrence_updated = Occurrence.objects.get(id=id)
        occurrence_updated.save()
        data = OccurrenceSerializer(occurrence_updated).data
        response = {'data': data}
    except:
        raise Exception('Error updating occurrence')

    return response
