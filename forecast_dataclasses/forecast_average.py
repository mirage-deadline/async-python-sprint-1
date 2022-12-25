from pydantic import BaseModel, Field, validator


class AvgTempDaily(BaseModel):
    date: str
    daily_avg_temp: float

    @validator('daily_avg_temp')
    def result_check(cls, v):
        return round(v, 2)


class RainlessHoursDaily(BaseModel):
    date: str
    rainless_hours_count: int


class AggregatedIndicators(BaseModel):
    temp_data: list[AvgTempDaily] = Field(
        [], description='Температура, среднее'
    )
    rainless_data: list[RainlessHoursDaily] = Field(
        [], description='Без осадков, часов'
    )
    avg_temp: float | None = None
    avg_rainless_hours: float | None = None

    @validator('avg_rainless_hours', 'avg_temp')
    def result_check(cls, v):
        return round(v, 2)


class CityStatistic(BaseModel):
    city: str
    aggregated_indicators: AggregatedIndicators
