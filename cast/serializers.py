import datetime
from typing import Any

from rest_framework import serializers

from cast.models import Forecast
from cast.validators import validate_date_is_less_than_10_days_away
from cast.validators import validate_date_not_in_past
from cast.validators import validate_date_string


class CityQuerySerializer(serializers.Serializer):
    city = serializers.CharField(max_length=100, required=True)


class CityAndDateQuerySerializer(CityQuerySerializer):
    date = serializers.CharField(
        required=True,
        validators=[
            validate_date_string,
            validate_date_not_in_past,
            validate_date_is_less_than_10_days_away,
        ],
    )


class CurrentWeatherResponseSerializer(serializers.Serializer):
    temperature = serializers.FloatField()
    local_time = serializers.CharField()


class ForecastResponseSerializer(serializers.Serializer):
    min_temperature = serializers.FloatField()
    max_temperature = serializers.FloatField()


class ForecastModelSerializer(serializers.ModelSerializer):
    date = serializers.CharField(
        validators=[
            validate_date_string,
            validate_date_not_in_past,
            validate_date_is_less_than_10_days_away,
        ]
    )

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        date_field = data.get("date")
        output = super().to_internal_value(data)
        output["date"] = datetime.datetime.strptime(date_field, "%d.%m.%Y")
        return output

    def to_representation(self, instance: Forecast) -> dict[str, Any]:
        date = instance.date
        output = super().to_representation(instance)
        output["date"] = date.strftime("%d.%m.%Y")
        return output

    class Meta:
        model = Forecast
        fields = "__all__"

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["min_temperature"] > attrs["max_temperature"]:
            raise serializers.ValidationError("Min temp cannot be more than max temp")

        return attrs
