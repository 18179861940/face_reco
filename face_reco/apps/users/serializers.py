from rest_framework import serializers
from .models import AttendCard


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendCard
        fields = '__all__'
