from rest_framework import serializers
from .models import Beneficiary

class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = '__all__'

from .models import PlantingSite

class PlantingSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantingSite
        fields = '__all__'
