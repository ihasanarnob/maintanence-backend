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

]
