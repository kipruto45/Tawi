from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .services.dashboard_service import get_dashboard_summary
from .serializers import (
    DashboardSummarySerializer,
    MonthlyTrendSerializer,
    SpeciesDistributionSerializer,
    RegionPerformanceSerializer,
)


class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = f"dashboard_summary_{request.user.id}"
        data = cache.get(cache_key)
        if data is None:
            data = get_dashboard_summary(user=request.user)
            cache.set(cache_key, data, 60 * 5)  # cache 5 minutes

        serializer = DashboardSummarySerializer(data)
        return Response({'status': 'success', 'data': serializer.data})


class DashboardTrendsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_dashboard_summary(user=request.user).get('monthly_trends', [])
        serializer = MonthlyTrendSerializer(data, many=True)
        return Response({'status': 'success', 'data': serializer.data})


class DashboardSpeciesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_dashboard_summary(user=request.user).get('species_distribution', [])
        serializer = SpeciesDistributionSerializer(data, many=True)
        return Response({'status': 'success', 'data': serializer.data})


class DashboardRegionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_dashboard_summary(user=request.user).get('top_regions', [])[:5]
        serializer = RegionPerformanceSerializer(data, many=True)
        return Response({'status': 'success', 'data': serializer.data})
