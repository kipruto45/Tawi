from rest_framework import serializers
from .models import FollowUp, MonitoringReport
from media_app.serializers import MediaSerializer


class FollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUp
        fields = '__all__'


class MonitoringReportSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, read_only=True)
    reporter = serializers.StringRelatedField(read_only=True)
    survival_rate = serializers.SerializerMethodField()

    class Meta:
        model = MonitoringReport
        fields = '__all__'

    def get_survival_rate(self, obj):
        return obj.survival_rate


class MonitoringStatsSerializer(serializers.Serializer):
    total_reports = serializers.IntegerField()
    total_monitored_sites = serializers.IntegerField()
    avg_survival_rate = serializers.FloatField()
    monthly_trends = serializers.ListField()
    top_sites = serializers.ListField()
