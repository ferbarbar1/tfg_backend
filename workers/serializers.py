from rest_framework import serializers
from .models import Schedule, Inform, Resource
from authentication.models import CustomUser
from authentication.serializers import CustomUserSerializer


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"


class InformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inform
        fields = "__all__"


class ResourceSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Resource
        fields = "__all__"

    def to_representation(self, instance):
        # En el modo de lectura, usa el CustomUserSerializer
        self.fields["author"] = CustomUserSerializer()
        return super(ResourceSerializer, self).to_representation(instance)
