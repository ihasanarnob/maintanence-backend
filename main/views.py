import traceback

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main.models import *
from main.serializers import *


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
