from pydantic import BaseModel, validator


class HourlyForecast(BaseModel):
    hour: int
    temp: int
    condition: str


class DailyForecast(BaseModel):
    date: str
    hours: list[HourlyForecast]

    @validator('date')
    def change_date_format(cls, v):
        date_arr = v.split('-')
        return '%s-%s' % (date_arr[-1], date_arr[-2])


class ForecastResponse(BaseModel):
    city: str
    forecasts: list[DailyForecast]
