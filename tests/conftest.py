import json
import pytest

from api_client import YandexWeatherAPI
from forecast_dataclasses.forecast_response import ForecastResponse


@pytest.fixture()
def api_client_obj():
    return YandexWeatherAPI()


@pytest.fixture()
def city_forecast():
    with open('tests/full_forecast.json', 'r') as file:
        return ForecastResponse.parse_obj(json.load(file))


@pytest.fixture()
def result_forecast():
    return [
        {
            'city': 'MOSCOW', 
            'weather_stat': [
                {
                    'date': '26-05', 
                    'daily_avg_temo': 17.73, 
                    'daily_rainless_hours': 7
                }, 
                {
                    'date': '27-05', 
                    'daily_avg_temo': 13.09, 
                    'daily_rainless_hours': 0
                }
            ], 
            'avg_temp': 13.75, 
            'avg_rainless_hours': 2.0
        }, 
        {
            'city': 'PARIS', 
            'weather_stat': [
                {
                    'date': '26-05', 
                    'daily_avg_temo': 17.64, 
                    'daily_rainless_hours': 9
                }, 
                {
                    'date': '27-05', 
                    'daily_avg_temo': 17.36, 
                    'daily_rainless_hours': 11
                }
            ], 
            'avg_temp': 13.0, 
            'avg_rainless_hours': 7.75
        }
    ]
