import json
from multiprocessing import Queue
from typing import Optional

from api_client import YandexWeatherAPI
from forecast_dataclasses.forecast_average import (AggregatedIndicators,
                                                   CityStatistic,
                                                   WeatherHoursDailyStat)
from forecast_dataclasses.forecast_response import (DailyForecast,
                                                    ForecastResponse,
                                                    HourlyForecast)
from services.logger import logger
from utils import CLEAR_WEATHER_SIGNS, RESULT_FILE_NAME, calc_avg


class DataFetchingTask:

    __slots__ = ('api_clent', )

    def __init__(self, api_client: YandexWeatherAPI) -> None:
        self.api_clent = api_client

    def fetch_forecast(self, city: str) -> ForecastResponse:
        response = self.api_clent.get_forecasting(city)
        return ForecastResponse(
            city=city,
            forecasts=[
                DailyForecast(**forecast) for forecast in
                response.get('forecasts', []) if forecast.get('hours')
            ]
        )


class DataCalculationTask:

    __slots__ = ('_forecasts', )

    STATISIC_UPPER_BOUND = 19
    STATISTIC_LOWER_BOUND = 9

    def __init__(self, city_forecasts: ForecastResponse) -> None:
        self._forecasts = city_forecasts

    def calculate_average_indicators(self, queue: Optional[Queue] = None) -> dict:
        avg_result = self.serialize_city_statistic(
            data=CityStatistic(
                city=self._forecasts.city,
                aggregated_indicators=self._avg_daily_calc()
            )
        )

        if queue:
            queue.put(avg_result)

        return avg_result

    def _avg_daily_calc(self) -> AggregatedIndicators:

        all_data = AggregatedIndicators()
        for daily_forecast in self._forecasts.forecasts:
            daily_stat = self._calc_daily_indicators(daily_forecast)
            all_data.weather_stat.append(daily_stat)

        all_data.avg_temp = calc_avg(
            [stat.daily_avg_temp for stat in all_data.weather_stat]
        )
        all_data.avg_rainless_hours = calc_avg(
            [stat.rainless_hours_count for stat in all_data.weather_stat]
        )

        return all_data

    def _calc_daily_indicators(self, daily_forecast: DailyForecast) -> WeatherHoursDailyStat:

        hour_forecast: HourlyForecast
        # Filter hours that included in statistics only
        daily_forecast.hours = [
            hour_forecast for hour_forecast in daily_forecast.hours if
            hour_forecast.hour >= self.STATISTIC_LOWER_BOUND
            and hour_forecast.hour <= self.STATISIC_UPPER_BOUND
        ]
        temperatures, rainless_hours_count = [], 0

        for hour_forecast in daily_forecast.hours:
            if hour_forecast.condition in CLEAR_WEATHER_SIGNS:
                rainless_hours_count += 1
            temperatures.append(hour_forecast.temp)
        return WeatherHoursDailyStat(
            date=daily_forecast.date,
            daily_avg_temp=calc_avg(temperatures),
            rainless_hours_count=rainless_hours_count
        )

    @staticmethod
    def serialize_city_statistic(data: CityStatistic):
        return {
            'city': data.city,
            'weather_stat': [
                {
                    'date': daily_stat.date,
                    'daily_avg_temo': daily_stat.daily_avg_temp,
                    'daily_rainless_hours': daily_stat.rainless_hours_count
                }
                for daily_stat in data.aggregated_indicators.weather_stat],
            'avg_temp': data.aggregated_indicators.avg_temp,
            'avg_rainless_hours': data.aggregated_indicators.avg_rainless_hours
        }


class DataAggregationTask:

    __slots__ = ()

    @staticmethod
    def save_results(to_save: list[dict]) -> None:
        with open(RESULT_FILE_NAME, 'w', encoding='utf-8') as file:
            json.dump(to_save, file, indent=4)
        logger.info(f'Saving results to {RESULT_FILE_NAME}')


class DataAnalyzingTask:

    __slots__ = ()

    @staticmethod
    def visit_advice() -> list:
        with open(RESULT_FILE_NAME, 'r') as file:
            data: list[dict] = json.load(file)

        max_rating = 0
        cities_to_visit = []

        # Not correct to use sort + lambda we need all cities that contain same stat
        for city_stat in data:
            rating = city_stat['avg_temp'] + city_stat['avg_rainless_hours']
            if rating > max_rating:
                cities_to_visit = [city_stat.get('city')]
                max_rating = rating
            elif rating == max_rating:
                cities_to_visit.append(city_stat.get('city'))

        return cities_to_visit
