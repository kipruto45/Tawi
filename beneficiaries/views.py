from rest_framework import viewsets, permissions
from .models import Beneficiary
from .serializers import BeneficiarySerializer

class BeneficiaryViewSet(viewsets.ModelViewSet):
    queryset = Beneficiary.objects.all()
    serializer_class = BeneficiarySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

from .models import PlantingSite
from .serializers import PlantingSiteSerializer

class PlantingSiteViewSet(viewsets.ModelViewSet):
    queryset = PlantingSite.objects.all()
    serializer_class = PlantingSiteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

