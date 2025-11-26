import traceback
import joblib

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main.models import *
from main.serializers import *

from .ml_model import predict_failure

model, FEATURE_COLUMNS = joblib.load("ml/device_health_model.pkl")
CLASS_NAMES = model.classes_  # ["Critical", "Healthy", "Needs Maintenance"] or similar

class PredictiveMaintenanceCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = PredictiveMaintenanceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PredictiveMaintenanceListView(APIView):
    def post(self, request):
        print("Received request data:", request.data)
        email = request.data.get("email", None)
        try:
            if email:
                queryset = PredictiveMaintenance.objects.filter(user_email=email)
            else:
                queryset = PredictiveMaintenance.objects.all()
            serializer = PredictiveMaintenanceSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PredictiveMaintenanceDetailView(APIView):
    def get(self, request, pk):
        try:
            instance = PredictiveMaintenance.objects.get(pk=pk)
            serializer = PredictiveMaintenanceSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PredictiveMaintenance.DoesNotExist:
            return Response(
                {"error": "Predictive Maintenance record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PredictiveMaintenanceMLView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # request.data is expected to include the 10 features
            result = predict_failure(request.data)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PredictDeviceHealth(APIView):
    def post(self, request):
        data = request.data

        # Only take ML-relevant features, fill missing with 0
        features = [data.get(col, 0) for col in FEATURE_COLUMNS]

        # Predict label
        prediction = model.predict([features])[0]

        # Predict probabilities
        probs = model.predict_proba([features])[0]  # array of probabilities
        prob_dict = dict(zip(CLASS_NAMES, [round(float(p), 2) for p in probs]))

        # Save record with prediction and confidence
        record = PredictiveMaintenance.objects.create(
            **data,
            ml_prediction=prediction,
            ml_confidence=prob_dict
        )

        return Response({
            "prediction": prediction,
            "confidence": prob_dict,
            "used_features": dict(zip(FEATURE_COLUMNS, features))
        })   