from pathlib import Path

import pytest

from forecast_dataclasses.forecast_average import CityStatistic
from forecast_dataclasses.forecast_response import ForecastResponse
from tasks import DataAggregationTask, DataAnalyzingTask, DataCalculationTask, DataFetchingTask


@pytest.mark.parametrize('city', ['BERLIN', 'MOSCOW'])
def test_fetch_forecast(api_client_obj, city):
    formatted_data = DataFetchingTask(api_client=api_client_obj, city=city).fetch_forecast()
    assert isinstance(formatted_data, ForecastResponse) == True
    assert formatted_data.city == city


def test_calculate_average_indicators(city_forecast: ForecastResponse):
    avg_result: CityStatistic = DataCalculationTask(city_forecast).calculate_average_indicators()
    assert len(avg_result) == 2
    assert avg_result[0].get('Среднее') == 15.41
    assert avg_result[1].get('Среднее') == 3.5


def test_data_aggregation(result_forecast):
    df = DataAggregationTask.save_results(result_forecast)
    assert len(df.columns) == 7
    assert df['Город/день'].fillna(method='ffill').unique().tolist() == ['MOSCOW', 'PARIS']
    assert Path('report.csv').exists()


def test_data_analyzing_advice():
    assert DataAnalyzingTask.visit_advice() == ['PARIS']
