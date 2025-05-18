from django.urls import path
from .views import RegisterView, UpdateBirthDetailsView, ChatHistoryView, ChatAPIView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('update-birth-details/<uuid:session_id>/',
         UpdateBirthDetailsView.as_view(), name='update-birthdetails'),
    path('chat-history/<uuid:session_id>/',
         ChatHistoryView.as_view(), name='chat-history'),
    path("chat/<uuid:session_id>/", ChatAPIView.as_view(), name="chat"),
]
