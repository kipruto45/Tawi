from rest_framework import serializers


class KeyValueSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.FloatField()


class DashboardSummarySerializer(serializers.Serializer):
    total_trees = serializers.IntegerField()
    alive = serializers.IntegerField()
    dead = serializers.IntegerField()
    avg_survival_rate = serializers.FloatField()
    total_sites = serializers.IntegerField()
    total_beneficiaries = serializers.IntegerField()
    monthly_trends = serializers.ListField()
    species_distribution = serializers.ListField()
    top_regions = serializers.ListField()


class MonthlyTrendSerializer(serializers.Serializer):
    month = serializers.CharField()
    count = serializers.IntegerField()


class SpeciesDistributionSerializer(serializers.Serializer):
    species = serializers.CharField()
    count = serializers.IntegerField()


class RegionPerformanceSerializer(serializers.Serializer):
    region = serializers.CharField()
    count = serializers.IntegerField()
