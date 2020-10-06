from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.authtoken.models import Token

from app.models import Author
from app.models import Occurrence
from app.serializers import OccurrenceSerializer, UserSerializer, LoginSerializer, ErrorResponseSerializer, \
    LoginResponseSerializer, AddOccurrenceSerializer, UpdateOccurrenceSerializer


def login(data):
    """
    Function that logins an user in the API.
    :param data: JSON with the credentials: username and password.
    :return: JSON with the username and the token associated.
    """
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


# If the function raises an exception, the state is resected to the initial one (before the function).
@transaction.atomic()
def add_occurrence(author, data):
    """
    Function that adds a new occurrence created by the author.
    :param author: Author that reports the occurrence.
    :param data: JSON data specific to the occurrence event.
    :return: JSON that represents the occurrence created.
    """
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


# If the function raises an exception, the state is resected to the initial one (before the function).
@transaction.atomic()
def update_occurrence(id, data):
    """
    Function that updates the status of a specific occurrence.
    :param id: Id of the occurrence to update.
    :param data: JSON with the new status.
    :return: JSON with the occurrence, with the new status.
    """
    update_occurrence_serializer = UpdateOccurrenceSerializer(data=data)
    if not update_occurrence_serializer.is_valid():
        raise Exception('Invalid body')

    status = update_occurrence_serializer.data["status"]

    occurrence = Occurrence.objects.filter(id=id)
    if not occurrence.exists():
        raise Exception(f"Occurrence with id {id} doesnt exist")

    try:
        occurrence.update(status=status)

        # save the occurrence, originating a new modified date
        occurrence_updated = Occurrence.objects.get(id=id)
        occurrence_updated.save()
        data = OccurrenceSerializer(occurrence_updated).data
        response = {'data': data}
    except:
        raise Exception('Error updating occurrence')

    return response
