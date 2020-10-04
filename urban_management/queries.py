from app.models import Author
from app.models import Occurrence
from app.serializers import OccurrenceSerializer


def get_author_by_id(id):
    return Author.objects.get(user_id=id)


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
