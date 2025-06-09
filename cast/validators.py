import datetime

from rest_framework import serializers


def validate_date_string(value: str) -> None:
    try:
        datetime.datetime.strptime(value, "%d.%m.%Y")
    except ValueError:
        raise serializers.ValidationError(
            "Invalid date format. Correct format is: DD.MM.YYYY"
        )


def validate_date_not_in_past(value: str) -> None:
    if datetime.datetime.strptime(value, "%d.%m.%Y") < datetime.datetime.today():
        raise serializers.ValidationError("Date cannot be in the past")


def validate_date_is_less_than_10_days_away(value: str) -> None:
    if datetime.datetime.strptime(
        value, "%d.%m.%Y"
    ) - datetime.datetime.today() > datetime.timedelta(days=10):
        raise serializers.ValidationError(
            "The date cannot be more than 10 days in the future from the current one"
        )
