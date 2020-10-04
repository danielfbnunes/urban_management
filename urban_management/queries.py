from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.authtoken.models import Token

from app.models import Author
from app.models import Occurrence
from app.serializers import OccurrenceSerializer, UserSerializer


def login(data):
    username = data.get('username')
    password = data.get('password')

    user = authenticate(
        username=username,
        password=password
    )

    if not user:
        error_message = 'Invalid credentials'
        return False, error_message, None, None

    token, _ = Token.objects.get_or_create(user=user)
    data = UserSerializer(user).data

    return True, None, data, token.key


def get_all_occurrences():
    return Occurrence.objects.all()


def get_author_by_id(id):
    return Author.objects.get(user_id=id)


def get_user_by_id(id):
    return User.objects.get(id=id)


def add_occurrence(author, data):
    transaction.set_autocommit(False)

    description = data.get("description")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    category = data.get("category")

    try:
        occurrence = Occurrence.objects.create(author=author, description=description,
                                               point=f"POINT({latitude} {longitude})", category=category)

        # Validate if the category is a valid choice
        occurrence.full_clean()

        data = OccurrenceSerializer(occurrence).data
    except ValidationError:
        transaction.rollback()
        error_message = "Error creating occurrence: invalid category"
        return False, error_message, None
    except:
        transaction.rollback()
        error_message = "Error creating occurrence"
        return False, error_message, None

    transaction.commit()
    transaction.set_autocommit(True)
    return True, None, data


def update_occurrence(id, data):
    transaction.set_autocommit(False)

    status = data.get("status")

    occurrence = Occurrence.objects.filter(id=id)

    if not occurrence.exists():
        transaction.rollback()
        error_message = f"Occurrence with id {id} doesnt exist"
        return False, error_message, None

    try:
        occurrence.update(status=status)

        # Validate if the updated status is a valid choice
        Occurrence.objects.get(id=id).full_clean()

        occurrence_updated = Occurrence.objects.get(id=id)
        occurrence_updated.save()
        data = OccurrenceSerializer(occurrence_updated).data
    except:
        transaction.rollback()
        error_message = "Error updating occurrence: invalid status"
        return False, error_message, None

    transaction.commit()
    transaction.set_autocommit(True)
    return True, None, data
