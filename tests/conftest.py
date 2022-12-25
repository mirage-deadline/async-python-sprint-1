import json
from multiprocessing import Queue
import pytest

from api_client import YandexWeatherAPI
from forecast_dataclasses.forecast_average import CityStatistic
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
            'Город/день': 'MOSCOW', 
            'Погода': 'Температура, среднее', 
            '26-05': 17.73, 
            '27-05': 13.09, 
            '28-05': 12.18, 
            '29-05': 12.0, 
            'Среднее': 13.75
        }, 
        {
            'Погода': 'Без осадков, часов', 
            '26-05': 7, 
            '27-05': 0, 
            '28-05': 0, 
            '29-05': 1, 
            'Среднее': 2.0
        }, 
        {
            'Город/день': 'PARIS', 
            'Погода': 'Температура, среднее', 
            '26-05': 17.64, 
            '27-05': 17.36, 
            '28-05': 17.0, 
            '29-05': 0.0, 
            'Среднее': 13.0
        }, 
        {
            'Погода': 'Без осадков, часов', 
            '26-05': 9, 
            '27-05': 11, 
            '28-05': 11, 
            '29-05': 0, 
            'Среднее': 7.75
        }]
