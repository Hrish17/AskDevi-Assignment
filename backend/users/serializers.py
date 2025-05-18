from rest_framework import serializers
from .models import UserBirthDetails, UserSession, ChatMessage


class BirthDetailSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    date_of_birth = serializers.DateField()
    time_of_birth = serializers.TimeField()
    place_of_birth = serializers.CharField(max_length=100)
    rashi_report = serializers.CharField(allow_blank=True, required=False)

    def create(self, validated_data):
        # Create new session and details without uniqueness check
        session = UserSession.objects.create()
        UserBirthDetails.objects.create(session=session, **validated_data)
        return session


class BirthDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBirthDetails
        fields = ['name', 'date_of_birth', 'time_of_birth',
                  'place_of_birth', 'rashi_report']

    def validate(self, attrs):
        return attrs


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['user_message', 'devi_response', 'timestamp']
