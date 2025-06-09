import dataclasses
import datetime
from typing import Any

import requests
from dateutil.tz import tzoffset
from django.conf import settings


@dataclasses.dataclass
class HttpResponse:
    data: dict[str, Any]
    status: int


def get_current_weather_data(city: str) -> HttpResponse:
    weather_api_key = settings.OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"

    response = requests.get(url)

    return HttpResponse(data=response.json(), status=response.status_code)


def get_forecast_data(city: str, date: str) -> HttpResponse:
    weather_api_key = settings.OPENWEATHER_API_KEY
    cnt = (
        datetime.datetime.strptime(date, "%d.%m.%Y") - datetime.datetime.today()
    ).days
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&cnt={cnt}&appid={weather_api_key}&units=metric"

    response = requests.get(url)

    return HttpResponse(data=response.json(), status=response.status_code)


def get_local_time(dt: int, timezone_: int) -> str:
    try:
        tz = tzoffset(datetime.UTC, timezone_)
        local_time = datetime.datetime.fromtimestamp(dt, tz).strftime("%H:%M")
    except Exception:
        return "Не удалось определить локальное время"

    return local_time
