from django.urls import path
from main.views import *

urlpatterns = [
    path(
        "submit/",
        PredictiveMaintenanceCreateView.as_view(),
        name="submit-device-data",
    ),
    path("insights/", PredictiveMaintenanceListView.as_view(), name="device-insights"),
    path(
        "insights/<int:pk>/",
        PredictiveMaintenanceDetailView.as_view(),
        name="device-insight-detail",
    ),
    path("predict/",  PredictiveMaintenanceMLView.as_view(),  name="predict-device-failure"),

    # Payment URLs
    path("create-payment/", PaymentCreateView.as_view(), name="create-payment"),
    path("payment/success/", PaymentSuccessView.as_view(), name="payment-success"),

    path("payment-ipn/", PaymentIPNView.as_view(), name="payment-ipn"),
    path("payment-status/<str:tran_id>/", PaymentStatusView.as_view(), name="payment-status"),

]