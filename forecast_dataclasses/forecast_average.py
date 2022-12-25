from pydantic import BaseModel, validator


class WeatherHoursDailyStat(BaseModel):
    date: str
    daily_avg_temp: float
    rainless_hours_count: int


class AggregatedIndicators(BaseModel):
    weather_stat: list[WeatherHoursDailyStat] = []
    avg_temp: float | None = None
    avg_rainless_hours: float | None = None


class CityStatistic(BaseModel):
    city: str
    aggregated_indicators: AggregatedIndicators
