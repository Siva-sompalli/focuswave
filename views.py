# focuswave_api/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import os
from django.conf import settings

print("=== Initializing FocusWave API Views ===")

# Define the base directory for ML files
BASE_DIR = settings.BASE_DIR
ML_MODELS_DIR = os.path.join(BASE_DIR, 'focuswave_api', 'ml_models')

print(f"BASE_DIR: {BASE_DIR}")
print(f"ML Models Directory: {ML_MODELS_DIR}")

# Check if directory exists
if os.path.exists(ML_MODELS_DIR):
    print(f"✓ ML models directory exists")
    files = os.listdir(ML_MODELS_DIR)
    print(f"Files in ml_models: {files}")
else:
    print(f"✗ ML models directory NOT FOUND: {ML_MODELS_DIR}")

# --- Global Model and Vectorizer Variables ---
FOCUS_MODEL = None
EMOTION_MODEL = None
VECTORIZER = None

# --- Model Loading Function ---
def load_ml_models():
    global FOCUS_MODEL, EMOTION_MODEL, VECTORIZER
    
    print("=== Loading ML Models ===")
    
    # Try to load focus model (XGBoost or Random Forest)
    focus_model_loaded = False
    
    # Try XGBoost first
    try:
        focus_model_path = os.path.join(ML_MODELS_DIR, "XGBoost.joblib")
        print(f"Trying to load XGBoost model from: {focus_model_path}")
        
        if os.path.exists(focus_model_path):
            FOCUS_MODEL = joblib.load(focus_model_path)
            print("✓ XGBoost focus model loaded successfully")
            focus_model_loaded = True
    except Exception as e:
        print(f"✗ Failed to load XGBoost model: {e}")
    
    # If XGBoost fails, try Random Forest
    if not focus_model_loaded:
        try:
            focus_model_path = os.path.join(ML_MODELS_DIR, "RF.joblib")
            print(f"Trying to load Random Forest model from: {focus_model_path}")
            
            if os.path.exists(focus_model_path):
                FOCUS_MODEL = joblib.load(focus_model_path)
                print("✓ Random Forest focus model loaded successfully")
                focus_model_loaded = True
        except Exception as e:
            print(f"✗ Failed to load Random Forest model: {e}")
    
    if not focus_model_loaded:
        print("✗ No focus model could be loaded")
        FOCUS_MODEL = None

    # Emotion Model Loading
    try:
        train_data_path = os.path.join(ML_MODELS_DIR, 'train.txt')
        print(f"Loading emotion training data from: {train_data_path}")
        
        if not os.path.exists(train_data_path):
            raise FileNotFoundError(f"Training data not found at: {train_data_path}")

        # Preprocess data
        def preprocess_data(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.readlines()
            preprocessed_data = [sample.strip().lower() for sample in data]
            return preprocessed_data

        # Load and prepare training data
        train_data = preprocess_data(train_data_path)
        X_train = [sample.split(';')[0] for sample in train_data]
        y_train = [sample.split(';')[1] for sample in train_data]

        print(f"Loaded {len(X_train)} training samples")

        # Fit vectorizer and train model
        VECTORIZER = TfidfVectorizer()
        X_train_vectorized = VECTORIZER.fit_transform(X_train)
        
        EMOTION_MODEL = RandomForestClassifier(n_estimators=100, random_state=42)
        EMOTION_MODEL.fit(X_train_vectorized, y_train)
        
        print("✓ Emotion model trained successfully")
        
    except Exception as e:
        print(f"✗ ERROR loading/training emotion model: {e}")
        EMOTION_MODEL = None
        VECTORIZER = None

    print("=== Model Loading Complete ===")

# Load models when Django starts
load_ml_models()

# -------------------------------
# 🩺 Health Check
# -------------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Check if ML models are loaded properly."""
    models_status = {
        'focus_model_loaded': FOCUS_MODEL is not None,
        'emotion_model_loaded': EMOTION_MODEL is not None,
        'vectorizer_loaded': VECTORIZER is not None
    }
    
    return Response({
        'status': 'Service is running',
        'models_loaded': models_status,
        'ml_models_directory': ML_MODELS_DIR
    }, status=status.HTTP_200_OK)

# -------------------------------
# 🔐 Authentication Views
# -------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Handles user login."""
    print("Login endpoint called")
    
    # Import here to avoid circular imports
    from django.contrib.auth import authenticate, login
    from .serializers import LoginSerializer
    
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    username = serializer.validated_data.get('email')
    password = serializer.validated_data.get('password')
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return Response({
            'message': 'Login successful.', 
            'token': 'fake-token-for-now'
        }, status=status.HTTP_200_OK)
    return Response({
        'error': 'Invalid Credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Handles user registration."""
    print("Register endpoint called")
    
    # Import here to avoid circular imports
    from .serializers import RegisterSerializer
    
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'User registered successfully. Please log in.'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -------------------------------
# 🔮 Focus Prediction View
# -------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def focus_predict(request):
    """Predicts Next Cycle Delay using FocusWave model."""
    print("Focus predict endpoint called")
    
    # Import here to avoid circular imports
    from .serializers import FocusPredictionSerializer
    
    # Check if model is loaded
    if FOCUS_MODEL is None:
        return Response({
            'error': 'Focus prediction model is not available. Please check server logs.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    serializer = FocusPredictionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data

    # Encoding features
    time_map = {'Morning': 0, 'Afternoon': 1, 'Evening': 2}
    task_map = {'Creative': 0, 'Routine': 1, 'Analytical': 2}

    time_encoded = time_map.get(data['Time_of_Day'], 1)
    task_encoded = task_map.get(data['Task_Type'], 1)
    mood_score = data['Mood_Score']

    # Prepare features array
    features = np.array([[
        data['Focus_Time_min'], 
        data['Break_Time_min'], 
        data['Engagement_Level'],
        data['Distraction_Count'], 
        mood_score, 
        data['Medication'],
        time_encoded, 
        task_encoded
    ]])

    try:
        predicted_delay = FOCUS_MODEL.predict(features)[0]
        predicted_delay = round(predicted_delay, 2)
    except Exception as e:
        return Response({
            'error': f'Model prediction failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Suggestion Logic
    if predicted_delay < 2:
        suggestion = "Excellent focus — take a brief 2-min stretch break."
    elif 2 <= predicted_delay < 8:
        suggestion = "Normal focus pattern — ready for next session soon."
    elif 8 <= predicted_delay <= 10:
        if mood_score <= 4:
            suggestion = "Low mood detected — take a longer 8–10 min recovery break."
        else:
            suggestion = "Slight fatigue — short relaxation recommended."
    else:
        suggestion = "High fatigue level — take extended rest or light task before resuming."

    return Response({
        'Predicted_Next_Cycle_Delay_min': predicted_delay,
        'FocusWave_Suggestion': suggestion,
        'input_data': data
    }, status=status.HTTP_200_OK)

# -------------------------------
# 💬 Emotion Prediction View
# -------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def emotion_predict(request):
    """Predicts emotion from user text."""
    print("Emotion predict endpoint called")
    user_input = request.data.get('text')
    
    if not user_input:
        return Response({
            'error': 'No text provided for emotion analysis.'
        }, status=status.HTTP_400_BAD_REQUEST)

    if EMOTION_MODEL is None or VECTORIZER is None:
        return Response({
            'error': 'Emotion analysis service is temporarily unavailable.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        text_vectorized = VECTORIZER.transform([user_input.lower()])
        predicted_emotion = EMOTION_MODEL.predict(text_vectorized)[0]
        
        return Response({
            'user_input': user_input,
            'predicted_emotion': predicted_emotion
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': f'Emotion prediction failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -------------------------------
# 🔧 Utility Views
# -------------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def test_endpoint(request):
    """Simple test endpoint to verify URL routing."""
    return Response({
        'message': 'FocusWave API is working!',
        'endpoint': 'test_endpoint'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def reload_models(request):
    """Force reload ML models (admin utility)."""
    print("Reloading models...")
    load_ml_models()
    
    models_status = {
        'focus_model_loaded': FOCUS_MODEL is not None,
        'emotion_model_loaded': EMOTION_MODEL is not None,
        'vectorizer_loaded': VECTORIZER is not None
    }
    
    return Response({
        'message': 'ML models reload initiated',
        'models_loaded': models_status
    }, status=status.HTTP_200_OK)