from pathlib import Path

import pytest

from forecast_dataclasses.forecast_average import CityStatistic
from forecast_dataclasses.forecast_response import ForecastResponse
from tasks import DataAggregationTask, DataAnalyzingTask, DataCalculationTask, DataFetchingTask
from utils import RESULT_FILE_NAME


@pytest.mark.parametrize('city', ['BERLIN', 'MOSCOW'])
def test_fetch_forecast(api_client_obj, city):
    formatted_data = DataFetchingTask(api_client=api_client_obj).fetch_forecast(city=city)
    assert isinstance(formatted_data, ForecastResponse) == True
    assert formatted_data.city == city


def test_calculate_average_indicators(city_forecast: ForecastResponse):
    avg_result: CityStatistic = DataCalculationTask(city_forecast).calculate_average_indicators()
    assert avg_result.get('avg_temp') == 15.41
    assert avg_result.get('avg_rainless_hours') == 3.5


def test_data_aggregation(result_forecast):
    DataAggregationTask.save_results(result_forecast)
    assert Path(RESULT_FILE_NAME).exists()


def test_data_analyzing_advice():
    assert DataAnalyzingTask.visit_advice() == ['PARIS']
