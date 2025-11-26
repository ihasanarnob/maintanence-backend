import traceback
import joblib
import time
import json
import requests

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main.models import *
from main.serializers import *

# -----------------------------
# Helpers
# -----------------------------
def _get_sslcommerz_base():
    return "https://sandbox.sslcommerz.com" if getattr(settings, "SSLCOMMERZ_IS_SANDBOX", True) else "https://securepay.sslcommerz.com"

def _safe_parse_json_string(s):
    """Return dict if s is JSON string, else {}"""
    if not s:
        return {}
    if isinstance(s, dict):
        return s
    try:
        return json.loads(s)
    except Exception:
        return {}
    
 # -----------------------------
# Create Payment - session creation
# -----------------------------
@method_decorator(csrf_exempt, name="dispatch")
class PaymentCreateView(APIView):
    """
    POST /api/create-payment/
    Expects JSON body with fields: amount, customer_name, customer_email, customer_phone, form_data (dict), product_name, product_category
    Returns GatewayPageURL and tran_id on success.
    """   

    def post(self, request, *args, **kwargs):
        try:
            data = request.data or {}

            base_url = _get_sslcommerz_base()
            tran_id = f"TXN{int(time.time())}"

            payment_data = {
                "store_id": settings.SSLCOMMERZ_STORE_ID,
                "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
                "total_amount": data.get("amount", 1000),
                "currency": "BDT",
                "tran_id": tran_id,
                # Backend callback endpoints (must be reachable by SSLCommerz)
                "success_url": "http://127.0.0.1:8000/api/payment/success/",
                "fail_url": "http://127.0.0.1:8000/api/payment/fail/",
                "cancel_url": "http://127.0.0.1:8000/api/payment/cancel/",
                "cus_name": data.get("customer_name", "Customer"),
                "cus_email": data.get("customer_email", ""),
                "cus_phone": data.get("customer_phone", ""),
                "cus_add1": data.get("cus_add1", "N/A"),
                "cus_city": data.get("cus_city", "N/A"),
                "cus_country": data.get("cus_country", "Bangladesh"),
                "shipping_method": "NO",
                "product_name": data.get("product_name", "Service"),
                "product_category": data.get("product_category", "General"),
                "product_profile": "general",
                # store form data (JSONField in model will accept dict)
                "value_a": json.dumps(data.get("form_data", {})),
            }

            # Force json response & accept header to avoid HTML error pages
            resp = requests.post(
                f"{base_url}/gwprocess/v4/api.php?format=json",
                data=payment_data,
                headers={"Accept": "application/json"},
                timeout=15,
            )

            # Debug print (remove in prod)
            print("SSLCommerz create raw response:", resp.text)

            # Safely parse JSON (requests will raise if invalid)
            try:
                payment_response = resp.json()
            except Exception as e:
                print("Failed to parse create-payment response as JSON:", str(e))
                return Response(
                    {"status": "FAILED", "message": "Invalid response from payment gateway", "raw": resp.text},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            if payment_response.get("status") == "SUCCESS":
                # Save transaction (form_data saved as dict if JSONField)
                PaymentTransaction.objects.create(
                    tran_id=tran_id,
                    amount=data.get("amount", 1000),
                    customer_email=data.get("customer_email"),
                    customer_phone=data.get("customer_phone"),
                    product_name=data.get("product_name"),
                    status="PENDING",
                    form_data=data.get("form_data", {}),
                )

                return Response(
                    {
                        "status": "SUCCESS",
                        "GatewayPageURL": payment_response.get("GatewayPageURL"),
                        "tran_id": tran_id,
                    }
                )

            return Response(
                {"status": "FAILED", "message": payment_response.get("failedreason", "Session creation failed")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -----------------------------
# Payment Success - validation + redirect
# -----------------------------
@method_decorator(csrf_exempt, name="dispatch")
class PaymentSuccessView(APIView):
    """
    Endpoint: /api/payment/success/
    SSLCommerz will call this (GET or POST). After validating the payment, this view will redirect the user to frontend.
    """

    def get(self, request, *args, **kwargs):
        return self._handle(request.GET)

    def post(self, request, *args, **kwargs):
        # SSLCommerz may POST data; frontend might POST as well (we treat the same)
        # request.data is a QueryDict or dict-like; convert to plain dict for easier access
        data = request.data if isinstance(request.data, dict) else dict(request.data)
        return self._handle(data)

    def _handle(self, data):
        try:
            # data may be QueryDict-like (from GET) or dict (from POST)
            tran_id = data.get("tran_id")
            val_id = data.get("val_id")

            print("PaymentSuccess callback data:", dict(data))

            if not tran_id or not val_id:
                # If missing params, return 400 so gateway knows
                return Response({"status": "FAILED", "message": "Missing tran_id or val_id"}, status=400)

            base_url = _get_sslcommerz_base()

            validation_params = {
                "store_id": settings.SSLCOMMERZ_STORE_ID,
                "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
                "val_id": val_id,
                "format": "json",
            }

            validation_resp = requests.get(
                f"{base_url}/validator/api/validationserverAPI.php",
                params=validation_params,
                timeout=15,
            )

            print("SSLCommerz validation raw:", validation_resp.text)

            try:
                validation = validation_resp.json()
            except Exception as e:
                print("Validation response is not JSON:", str(e))
                return Response(
                    {"status": "FAILED", "message": "Invalid validation response from gateway", "raw": validation_resp.text},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            if validation.get("status") == "VALID":
                # mark transaction success and create predictive record from saved form_data
                transaction = PaymentTransaction.objects.get(tran_id=tran_id)
                transaction.status = "SUCCESS"
                transaction.bank_tran_id = validation.get("bank_tran_id")

                # safe form_data handling (JSONField -> dict)
                raw_form_data = transaction.form_data
                if isinstance(raw_form_data, dict):
                    form_data = raw_form_data
                else:
                    try:
                        form_data = json.loads(raw_form_data or "{}")
                    except Exception:
                        form_data = {}

                # ensure user email is present
                if "user_email" not in form_data and transaction.customer_email:
                    form_data["user_email"] = transaction.customer_email

                # create predictive maintenance record
                if form_data:
                    serializer = PredictiveMaintenanceSerializer(data=form_data)
                    if serializer.is_valid():
                        pm_record = serializer.save()
                        # attach to transaction if model has FK field 'predictive_maintenance'
                        try:
                            transaction.predictive_maintenance = pm_record
                        except Exception:
                            # If model doesn't have this FK, ignore silently
                            pass

                transaction.save()

                # Redirect the user's browser back to frontend success page with tran_id
                frontend_success_url = f"http://localhost:3000/payment/success?tran_id={tran_id}"
                return HttpResponseRedirect(frontend_success_url)

            # validation failed
            PaymentTransaction.objects.filter(tran_id=tran_id).update(status="FAILED")
            frontend_fail_url = f"http://localhost:3000/payment/fail?tran_id={tran_id}"
            return HttpResponseRedirect(frontend_fail_url)

        except PaymentTransaction.DoesNotExist:
            traceback.print_exc()
            return Response({"error": "Transaction not found"}, status=404)
        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)

# -----------------------------
# IPN (Instant Payment Notification)
# -----------------------------
@method_decorator(csrf_exempt, name="dispatch")
class PaymentIPNView(APIView):
    """
    Endpoint: /api/payment-ipn/
    SSLCommerz IPN will POST here. We validate similarly to success flow but do not redirect (IPN is server-to-server).
    """

    def post(self, request, *args, **kwargs):
        try:
            data = request.POST.dict() if hasattr(request, "POST") else dict(request.data or {})
            tran_id = data.get("tran_id")
            val_id = data.get("val_id")

            print("IPN received:", data)

            if not tran_id or not val_id:
                return Response({"status": "IGNORED"})

            base_url = _get_sslcommerz_base()

            validation_params = {
                "store_id": settings.SSLCOMMERZ_STORE_ID,
                "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
                "val_id": val_id,
                "format": "json",
            }

            validation_resp = requests.get(
                f"{base_url}/validator/api/validationserverAPI.php",
                params=validation_params,
                timeout=15,
            )

            print("IPN validation raw:", validation_resp.text)

            try:
                result = validation_resp.json()
            except Exception:
                return Response({"status": "ERROR", "message": "Invalid validation response"}, status=502)

            if result.get("status") == "VALID":
                PaymentTransaction.objects.filter(tran_id=tran_id).update(
                    status="SUCCESS", bank_tran_id=result.get("bank_tran_id")
                )

            return Response({"status": "OK"})

        except Exception:
            traceback.print_exc()
            return Response({"status": "ERROR"}, status=500)

# -----------------------------
# Get transaction status
# -----------------------------
class PaymentStatusView(APIView):
    """
    GET /api/payment-status/<tran_id>/
    """

    def get(self, request, tran_id):
        try:
            tx = PaymentTransaction.objects.get(tran_id=tran_id)
            return Response(
                {
                    "tran_id": tx.tran_id,
                    "status": tx.status,
                    "amount": tx.amount,
                    "created_at": tx.created_at,
                }
            )
        except PaymentTransaction.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=404)



# .....................
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