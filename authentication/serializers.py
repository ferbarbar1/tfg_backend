from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser, Owner, Client, Worker


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "password", "first_name", "last_name", "email"]

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user


class OwnerSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Owner
        fields = ["id", "user"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = CustomUser.objects.create_user(**user_data)
        owner = Owner.objects.create(user=user, **validated_data)
        return owner

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user")
        user = instance.user

        # Actualiza los campos del usuario
        user.username = user_data.get("username", user.username)
        user.password = user_data.get("password", user.password)
        user.first_name = user_data.get("first_name", user.first_name)
        user.last_name = user_data.get("last_name", user.last_name)
        user.email = user_data.get("email", user.email)
        user.save()

        return instance


class WorkerSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Worker
        fields = ["id", "user", "salary", "specialty"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = CustomUser.objects.create_user(**user_data)
        worker = Worker.objects.create(user=user, **validated_data)
        return worker

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user")
        user = instance.user

        # Actualiza los campos del usuario
        user.username = user_data.get("username", user.username)
        user.password = user_data.get("password", user.password)
        user.first_name = user_data.get("first_name", user.first_name)
        user.last_name = user_data.get("last_name", user.last_name)
        user.email = user_data.get("email", user.email)
        user.save()

        # Actualiza los campos del trabajador
        instance.salary = validated_data.get("salary", instance.salary)
        instance.specialty = validated_data.get("specialty", instance.specialty)
        instance.save()

        return instance


class ClientSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Client
        fields = ["id", "user", "subscription_plan"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = CustomUser.objects.create_user(**user_data)
        client = Client.objects.create(user=user, **validated_data)
        return client

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user")
        user = instance.user

        # Actualiza los campos del usuario
        user.username = user_data.get("username", user.username)
        user.password = user_data.get("password", user.password)
        user.first_name = user_data.get("first_name", user.first_name)
        user.last_name = user_data.get("last_name", user.last_name)
        user.email = user_data.get("email", user.email)
        user.save()

        # Actualiza los campos del cliente
        instance.subscription_plan = validated_data.get(
            "subscription_plan", instance.subscription_plan
        )
        instance.save()

        return instance
