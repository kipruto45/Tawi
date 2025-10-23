from rest_framework import serializers
from .models import QRCode


class QRCodeSerializer(serializers.ModelSerializer):
    tree = serializers.StringRelatedField(read_only=True)
    site = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = QRCode
        fields = '__all__'


class GenerateQRCodeSerializer(serializers.Serializer):
    tree_id = serializers.CharField(required=False)
    site_id = serializers.IntegerField(required=False)
    label = serializers.CharField(required=False)
