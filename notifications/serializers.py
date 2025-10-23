from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField(read_only=True)
    recipient = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'


class SendNotificationSerializer(serializers.Serializer):
    recipient_id = serializers.IntegerField()
    verb = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    url = serializers.CharField(allow_blank=True, required=False)
    level = serializers.ChoiceField(choices=[('info','Info'),('warning','Warning'),('critical','Critical')], default='info')