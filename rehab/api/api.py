from ninja import Router,Schema
from ninja import File
from ninja.files import UploadedFile
import PyPDF2
from PIL import Image
import pytesseract
import os
from django.conf import settings
from pydantic import BaseModel
from datetime import datetime
from twilio.rest import Client
from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from django.http import JsonResponse
from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import google.generativeai as genai

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            UntypedToken(token)  # This will validate the token
            return token
        except InvalidToken:
            return JsonResponse({"error": "Invalid token"}, status=403)

auth = JWTAuth()
# router = Router(auth=auth)
router = Router(auth=None)

# Feature 4 : Routine Generation
class GoalSchema(Schema):
    goal: str

@router.post("/routine")
def routine_feature(request, data: GoalSchema):
    goal = data.goal
    query = f"generate me a 10 days plan for {goal} in json format also only give json dont give any else description also dont give starting json tags just give scratch json"
    response = talk_to_gemini(query)
    return {"routine": response}

# feature 3 : data collection
class SensorDataSchema(BaseModel):
    ecg: float
    temperature: float
    # oximeter: float
    # blood_pressure: float
sensor_data_storage = []  # Temporary in-memory storage

@router.post("/sensor-data/")
def receive_sensor_data(request, data: SensorDataSchema):
    # Add timestamp to the sensor data
    sensor_data = {
        "ecg": data.ecg,
        "temperature": data.temperature,
        # "oximeter": data.oximeter,
        # "blood_pressure": data.blood_pressure,
        "timestamp": datetime.now()
    }
    if(len(sensor_data_storage) > 10):
        sensor_data_storage.pop(0)

    sensor_data_storage.append(sensor_data)  # Simulate database storage
    
    return {"status": "success", "data": sensor_data}

@router.get("/sensor-data/")
def get_sensor_data(request):
    if sensor_data_storage:
        return sensor_data_storage[-1]  # Return the most recent sensor data
    return {"message": "No data available"}
# feature 3 end 


# Feature 1: File upload and summarization start
@router.post("/upload", tags=["files"],auth=None)
def upload_and_summarize(request, file: UploadedFile = File(...)):
    # Save file to a temporary location
    save_path = os.path.join(settings.MEDIA_ROOT, file.name)
    with open(save_path, "wb") as f:
        for chunk in file.chunks():
            f.write(chunk)

    # Extract text from the file
    text = extract_text(save_path)

    summary = summarize_text(text)

    return {"summary": summary}


def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.jpg') or file_path.endswith('.png'):
        return extract_text_from_image(file_path)
    else:
        return "Unsupported file format"


def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)  # Use PdfReader
        for page_num in range(len(reader.pages)):  # Use len(reader.pages)
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def extract_text_from_image(file_path):
    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)
    print(text)
    return text

def summarize_text(text):
    query = f"summarize this for me {text}"
    res = talk_to_gemini(query)
    return res

# Feature 1 end

# Feature 2: Doctor call start
class DoctorCallRequest(Schema):
    meeting_id: str

@router.post('/doctorCall', tags=["doctorCall"])
def doctorCall(request, data: DoctorCallRequest):
    meeting_id = data.meeting_id
    moderatorURL = f'https://meet.jit.si/{meeting_id}#config.prejoinPageEnabled=false&userInfo.displayName=Moderator';
    send_sms('+916284132301', f'Click this link to join the meeting as a moderator: {moderatorURL}')
    return {"message": "Doctor called successfully"}

def send_sms(to, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to
        )
        return message.sid
    except Exception as e:
        return str(e)
# Feature 2 end

def talk_to_gemini(query):
    # Call Gemini API
    genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(query)
    # print(response.text)
    return response.text

    
@router.get('/ping')
def index(request):
    return {"message": "pong"}


# Protected route
@router.get("/protected-route/", auth=auth)
def protected_route(request):
    return {"message": "This is a protected route. You are authenticated."}

# Schema for user registration
class RegisterSchema(Schema):
    username: str
    password: str
    email: str

# Register endpoint
@router.post("/register/",auth=None)
def register(request, data: RegisterSchema):
    # Check if the username already exists
    if User.objects.filter(username=data.username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)
    
    # Create a new user
    user = User.objects.create(
        username=data.username,
        password=make_password(data.password),  # Hash the password
        email=data.email
    )
    
    return JsonResponse({"message": "User registered successfully"}, status=201)


# JWT Setup
# Login endpoint to get JWT token

# Schema for login
class LoginSchema(Schema):
    username: str
    password: str

@router.post("/login/",auth=None)
def login(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

# Refresh token endpoint
@router.post("/token/refresh/")
def refresh_token(request, refresh: str):
    try:
        refresh_token = RefreshToken(refresh)
        access_token = refresh_token.access_token
        return {"access": str(access_token)}
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
