from rest_framework import serializers
from .models import AttendCard, UserTable


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendCard
        fields = '__all__'


class UserTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserTable
        fields = '__all__'

