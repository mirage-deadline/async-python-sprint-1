import pandas as pd

from api_client import YandexWeatherAPI
from forecast_dataclasses.forecast_average import (AggregatedIndicators,
                                                   AvgTempDaily, CityStatistic,
                                                   RainlessHoursDaily)
from forecast_dataclasses.forecast_response import (DailyForecast,
                                                    ForecastResponse,
                                                    HourlyForecast)
from services.logger import logger
from utils import CLEAR_WEATHER_SIGNS, calc_avg


class DataFetchingTask:

    __slots__ = ('city', 'api_clent')

    def __init__(self, city: str, api_client: YandexWeatherAPI) -> None:
        self.city = city
        self.api_clent = api_client

    def fetch_forecast(self) -> ForecastResponse:
        response = self.api_clent.get_forecasting(self.city)
        return ForecastResponse(
            city=self.city,
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

    def calculate_average_indicators(self) -> list[dict]:
        return self.serialize_city_statistic(
            data=CityStatistic(
                city=self._forecasts.city,
                aggregated_indicators=self._avg_daily_calc()
            )
        )

    def _avg_daily_calc(self) -> AggregatedIndicators:

        daily_data = AggregatedIndicators()
        total_rainliess_avg, total_temp_avg = [], []
        for daily_forecast in self._forecasts.forecasts:
            for attr, res in zip(
                ('temp_data', 'rainless_data'),
                self._calc_daily_indicators(daily_forecast)
            ):
                if attr == 'temp_data':
                    total_temp_avg.append(res.daily_avg_temp)
                else:
                    total_rainliess_avg.append(res.rainless_hours_count)
                getattr(daily_data, attr).append(res)

        daily_data.avg_rainless_hours = calc_avg(total_rainliess_avg)
        daily_data.avg_temp = calc_avg(total_temp_avg)
        return daily_data

    def _calc_daily_indicators(self, daily_forecast: DailyForecast):

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
        return \
            AvgTempDaily(
                date=daily_forecast.date,
                daily_avg_temp=calc_avg(temperatures)
            ),\
            RainlessHoursDaily(
                date=daily_forecast.date,
                rainless_hours_count=rainless_hours_count
            )

    @staticmethod
    def serialize_city_statistic(data: CityStatistic):
        return [
            {
                'Город/день': data.city,
                'Погода': 'Температура, среднее',
                **{avg_temp_daily_obj.date: avg_temp_daily_obj.daily_avg_temp
                    for avg_temp_daily_obj in data.aggregated_indicators.temp_data},
                'Среднее': data.aggregated_indicators.avg_temp
            },
            {
                'Погода': 'Без осадков, часов',
                **{avg_rainless_daily_obj.date: avg_rainless_daily_obj.rainless_hours_count
                    for avg_rainless_daily_obj in data.aggregated_indicators.rainless_data},
                'Среднее': data.aggregated_indicators.avg_rainless_hours
            }
        ]


class DataAggregationTask:

    __slots__ = ()

    @staticmethod
    def save_results(to_save: list[dict], file_name: str = 'report.csv') -> pd.DataFrame:
        df = pd.DataFrame(to_save)
        df.to_csv(file_name, index=False)
        logger.info(f'Saving results to {file_name}')
        return df


class DataAnalyzingTask:

    __slots__ = ()

    @staticmethod
    def visit_advice() -> list[str]:
        df = pd.read_csv('report.csv')
        df['Город/день'] = df['Город/день'].fillna(method='ffill')
        df = df.groupby(
            by=['Город/день']).agg({'Среднее': 'sum'})\
            .rename(columns={'Среднее': 'Рейтинг'}).reset_index()
        df['rank'] = df['Рейтинг'].rank(ascending=False).astype('int')
        visit_cities = df[df['rank'] == df['rank'].min()]['Город/день'].unique()
        return visit_cities
