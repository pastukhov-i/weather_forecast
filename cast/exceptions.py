from typing import Any


class WeatherAPIRequestError(Exception):
    def __init__(self, error: dict[str, Any], status: int):
        super().__init__()
        self.error = error
        self.status = status
