from rest_framework import serializers
from .models import Media


class MediaSerializer(serializers.ModelSerializer):
    uploader = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Media
        fields = ['id', 'file', 'file_type', 'title', 'description', 'uploader', 'uploaded_at', 'tree', 'site', 'latitude', 'longitude', 'taken_at']
