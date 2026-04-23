# focuswave_api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class FocusPredictionSerializer(serializers.Serializer):
    Focus_Time_min = serializers.FloatField(min_value=0)
    Break_Time_min = serializers.FloatField(min_value=0)
    Engagement_Level = serializers.FloatField(min_value=1, max_value=10)
    Distraction_Count = serializers.FloatField(min_value=0)
    Mood_Score = serializers.FloatField(min_value=1, max_value=10)
    Medication = serializers.IntegerField(min_value=0, max_value=1)
    Time_of_Day = serializers.ChoiceField(choices=['Morning', 'Afternoon', 'Evening'])
    Task_Type = serializers.ChoiceField(choices=['Creative', 'Routine', 'Analytical'])