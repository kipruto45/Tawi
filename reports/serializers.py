from rest_framework import serializers
from .models import GeneratedReport


class GeneratedReportSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GeneratedReport
        fields = '__all__'


class CreateReportSerializer(serializers.Serializer):
    name = serializers.CharField()
    report_type = serializers.ChoiceField(choices=[('summary','Summary'),('partner','Partner'),('public','Public')])
    period_start = serializers.DateField(required=False)
    period_end = serializers.DateField(required=False)
    filters = serializers.JSONField(required=False)
