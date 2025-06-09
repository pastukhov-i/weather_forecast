import datetime
from typing import Any

from django.http import JsonResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from cast.exceptions import WeatherAPIRequestError
from cast.models import Forecast
from cast.serializers import CityAndDateQuerySerializer
from cast.serializers import CityQuerySerializer
from cast.serializers import CurrentWeatherResponseSerializer
from cast.serializers import ForecastModelSerializer
from cast.serializers import ForecastResponseSerializer
from cast.services import get_current_weather_data
from cast.services import get_forecast_data
from cast.services import get_local_time


class CurrentWeatherAPIView(APIView):
    """
    API для получения текущей погоды и местного времени в указанном городе
    """

    def get(self, request: Request) -> JsonResponse:
        query = CityQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        city = query.validated_data["city"]

        # Получаем данные о погоде
        weather_data = get_current_weather_data(city)
        if weather_data.status != status.HTTP_200_OK:
            return JsonResponse(
                data=weather_data.data,
                status=weather_data.status,
            )

        # Формируем ответ
        response_serializer = CurrentWeatherResponseSerializer(
            data={
                "temperature": weather_data.data["main"]["temp"],
                "local_time": get_local_time(
                    weather_data.data["dt"], weather_data.data["timezone"]
                ),
            }
        )
        response_serializer.is_valid(raise_exception=True)
        response_data = response_serializer.validated_data

        return JsonResponse(data=response_data, status=status.HTTP_200_OK)


class ForecastWeatherAPIView(APIView):
    def get(self, request: Request) -> JsonResponse:
        query = CityAndDateQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        city = query.validated_data["city"]
        date = query.validated_data["date"]

        try:
            forecast_obj = self._get_forecast_data_from_db(city, date)
            response_data = self._create_response_data_for_forecast(
                min_temp=forecast_obj.min_temperature,
                max_temp=forecast_obj.max_temperature,
            )
        except Forecast.DoesNotExist:
            try:
                forecast_info = self._get_forecast_data_from_api(city, date)
            except WeatherAPIRequestError as e:
                return JsonResponse(data=e.error, status=e.status)

            response_data = self._create_response_data_for_forecast(
                min_temp=forecast_info["main"]["temp_min"],
                max_temp=forecast_info["main"]["temp_max"],
            )

        return JsonResponse(data=response_data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> JsonResponse:
        new_forecast = ForecastModelSerializer(data=request.data)
        new_forecast.is_valid(raise_exception=True)
        forecast, _ = Forecast.objects.get_or_create(**new_forecast.validated_data)

        return JsonResponse(data=ForecastModelSerializer(forecast).data)

    @staticmethod
    def _get_forecast_data_from_db(city: str, date: str) -> Forecast:
        forecast = (
            Forecast.objects.filter(
                city=city, date=datetime.datetime.strptime(date, "%d.%m.%Y")
            )
            .order_by("-id")
            .first()
        )

        if not forecast:
            raise Forecast.DoesNotExist

        return forecast

    @staticmethod
    def _get_forecast_data_from_api(city: str, date: str) -> dict[str, Any]:
        forecast_data = get_forecast_data(city, date)
        if forecast_data.status != status.HTTP_200_OK:
            raise WeatherAPIRequestError(
                error=forecast_data.data,
                status=forecast_data.status,
            )

        last_forecast: dict[str, Any] = forecast_data.data["list"][-1]

        return last_forecast

    @staticmethod
    def _create_response_data_for_forecast(
        min_temp: float, max_temp: float
    ) -> dict[str, Any]:
        response_serializer = ForecastResponseSerializer(
            data={
                "min_temperature": min_temp,
                "max_temperature": max_temp,
            }
        )
        response_serializer.is_valid(raise_exception=True)
        response_data: dict[str, Any] = response_serializer.validated_data

        return response_data
