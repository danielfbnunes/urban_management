from django.contrib.auth.models import User

from app.models import Author
from app.models import Occurrence
from app.serializers import OccurrenceSerializer


def get_author_by_id(id):
    return Author.objects.get(user_id=id)


def get_user_by_id(id):
    return User.objects.get(id=id)


def add_occurrence(author, data):
    description = data.get("description")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    try:
        occurrence = Occurrence.objects.create(author=author, description=description,
                                               point=f"POINT({latitude} {longitude})")

        data = OccurrenceSerializer(occurrence).data
    except:
        error_message = "Error creating occurrence"
        return False, error_message, None
    return True, None, data


def update_occurrence(id, data):
    status = data.get("status")

    occurrence = Occurrence.objects.filter(id=id)

    if not occurrence.exists():
        error_message = f"Occurrence with id {id} doesnt exist"
        return False, error_message, None

    try:
        occurrence.update(status=status)

        # Validate if the updated status is a valid choice
        Occurrence.objects.get(id=id).full_clean()

        occurrence_updated = Occurrence.objects.get(id=id)
        data = OccurrenceSerializer(occurrence_updated).data
    except:
        error_message = "Error updating occurrence: invalid status"
        return False, error_message, None
    return True, None, data
