from django.urls import path

from cast.views import CurrentWeatherAPIView
from cast.views import ForecastWeatherAPIView

urlpatterns = [
    path("current/", CurrentWeatherAPIView.as_view()),
    path("forecast/", ForecastWeatherAPIView.as_view()),
]
