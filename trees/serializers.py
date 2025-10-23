from rest_framework import serializers
from .models import Tree, TreeUpdate, TreeSpecies
from media_app.serializers import MediaSerializer


class TreeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeUpdate
        fields = '__all__'


class TreeBulkCreateSerializer(serializers.Serializer):
    trees = serializers.ListField(child=serializers.DictField())

    def create(self, validated_data):
        created = []
        for item in validated_data['trees']:
            t = Tree.objects.create(**item)
            created.append(t)
        return created

class TreeSerializer(serializers.ModelSerializer):
    updates = TreeUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = Tree
        fields = '__all__'


class TreeSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeSpecies
        fields = '__all__'


class TreeSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeSpecies
        fields = '__all__'
