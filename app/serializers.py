from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from app.models import Occurrence, Status, Category


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)


class OccurrenceSerializer(GeoFeatureModelSerializer):
    author = serializers.SerializerMethodField("get_username")
    description = serializers.CharField(required=True)
    creation_date = serializers.DateTimeField(required=True)
    modified_date = serializers.DateTimeField(required=True)
    status = serializers.ChoiceField(required=True, choices=Status.choices)
    category = serializers.ChoiceField(required=True, choices=Category.choices)

    def get_username(self, obj):
        return obj.author.user.username

    class Meta:
        model = Occurrence
        geo_field = "point"
        fields = ('id', 'author', 'description', 'creation_date', 'modified_date', 'status', 'category')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class LoginResponseSerializer(serializers.Serializer):
    data = UserSerializer()
    token = serializers.CharField(required=True)


class AddOccurrenceSerializer(serializers.Serializer):
    description = serializers.CharField(required=True)
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    category = serializers.ChoiceField(required=True, choices=Category.choices)


class UpdateOccurrenceSerializer(serializers.Serializer):
    status = serializers.ChoiceField(required=True, choices=Status.choices)


class OccurrenceResponseSerializer(serializers.Serializer):
    data = OccurrenceSerializer()


class ErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(required=True)
