from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from app.models import Occurrence, Status, Category


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)


class OccurrenceSerializer(GeoFeatureModelSerializer):
    author = serializers.SerializerMethodField("get_username")
    description = serializers.CharField(required=True)
    creation_date = serializers.DateTimeField()
    modified_date = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=Status.choices)
    category = serializers.ChoiceField(choices=Category.choices)

    def get_username(self, obj):
        return obj.author.user.username

    class Meta:
        model = Occurrence
        geo_field = "point"
        fields = ('id', 'author', 'description', 'creation_date', 'modified_date', 'status', 'category')
