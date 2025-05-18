import os
import base64
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from huggingface_hub import InferenceClient
from .models import UserBirthDetails, UserSession, ChatMessage
from .serializers import (
    BirthDetailSerializer,
    BirthDetailUpdateSerializer,
    ChatMessageSerializer
)
from .rag import retrieve_chunks, build_prompt

# Helper to fetch Rashi report from AstrologyAPI


def fetch_rashi_report(data):
    url = "https://json.astrologyapi.com/v1/astro_details/"
    user_id = os.environ.get("ASTROLOGYAPI_USERID")
    api_key = os.environ.get("ASTROLOGYAPI_KEY")
    if not user_id or not api_key:
        return ""
    auth = base64.b64encode(f"{user_id}:{api_key}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
        "Accept-Language": "en"
    }
    resp = requests.post(url, json=data, headers=headers)
    if resp.status_code == 200:
        return resp.text  # or parse JSON if needed
    return ""


class RegisterView(APIView):
    def post(self, request):
        # Validate input via serializer
        serializer = BirthDetailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        # Build astrologyapi payload
        birth_data = {
            "day": data["date_of_birth"].day,
            "month": data["date_of_birth"].month,
            "year": data["date_of_birth"].year,
            "hour": data["time_of_birth"].hour,
            "min": data["time_of_birth"].minute,
            "lat": 19.132,  "lon": 72.342,  "tzone": 5.5
        }
        # Fetch and store rashi_report
        data["rashi_report"] = fetch_rashi_report(birth_data)

        # Create session + birth details
        session = serializer.create(data)
        return Response({"session_id": str(session.session_id)}, status=status.HTTP_201_CREATED)


class UpdateBirthDetailsView(APIView):
    def put(self, request, session_id):
        # Fetch session & details
        try:
            session = UserSession.objects.get(session_id=session_id)
            bd = session.birth_details
        except UserSession.DoesNotExist:
            return Response({"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND)
        except UserBirthDetails.DoesNotExist:
            return Response({"error": "Birth details not found for this session."}, status=status.HTTP_404_NOT_FOUND)

        # Validate incoming fields
        serializer = BirthDetailUpdateSerializer(
            bd, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        valid = serializer.validated_data
        # If core fields changed, recompute Rashi
        if any(f in valid for f in ("date_of_birth", "time_of_birth", "place_of_birth")):
            dob = valid.get("date_of_birth", bd.date_of_birth)
            tob = valid.get("time_of_birth", bd.time_of_birth)
            # astro payload
            astro = {
                "day": dob.day, "month": dob.month, "year": dob.year,
                "hour": tob.hour, "min": tob.minute,
                "lat": 19.132, "lon": 72.342, "tzone": 5.5
            }
            bd.rashi_report = fetch_rashi_report(astro)

        # Save updates
        serializer.save()
        return Response({"message": "Birth details updated successfully."}, status=status.HTTP_200_OK)


class ChatHistoryView(APIView):
    def get(self, request, session_id):
        # Fetch session
        try:
            session = UserSession.objects.get(session_id=session_id)
        except UserSession.DoesNotExist:
            return Response({"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize last 10 messages (oldest→newest)
        msgs = ChatMessage.objects.filter(
            session=session).order_by('timestamp')[:10]
        serializer = ChatMessageSerializer(msgs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatAPIView(APIView):
    def post(self, request, session_id):
        message = request.data.get("message")
        if not message:
            return Response(
                {"error": "'message' is required in request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch session & birth
        try:
            session = UserSession.objects.get(session_id=session_id)
            bd = session.birth_details
        except UserSession.DoesNotExist:
            return Response({"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        # RAG retrieval & prompt
        chunks = retrieve_chunks(message, k=3)
        prompt = build_prompt(message, bd, chunks)

        # HF inference via Novita router
        try:
            hf_key = os.environ["HUGGINGFACE_API_KEY"]
            client = InferenceClient(provider="novita", api_key=hf_key)
            comp = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3-0324",
                messages=[
                    {"role": "system", "content": "You are Devi, a wise astrologer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=110,   # ~80 words
                temperature=0.7
            )
            answer = comp.choices[0].message.content.strip()
        except KeyError:
            return Response({"error": "HUGGINGFACE_API_KEY not set."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as ex:
            return Response({"error": f"LLM call failed: {ex}"}, status=status.HTTP_502_BAD_GATEWAY)

        # Save & prune chat history
        ChatMessage.objects.create(
            session=session, user_message=message, devi_response=answer)
        all_msgs = ChatMessage.objects.filter(
            session=session).order_by('timestamp')
        if all_msgs.count() > 10:
            all_msgs[: all_msgs.count() - 10].delete()

        return Response({"answer": answer}, status=status.HTTP_200_OK)
