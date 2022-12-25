import itertools
import os
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, Queue

from api_client import YandexWeatherAPI
from forecast_dataclasses.forecast_response import ForecastResponse
from services.logger import logger
from tasks import (DataAggregationTask, DataAnalyzingTask, DataCalculationTask,
                   DataFetchingTask)
from utils import CITIES

api_client = YandexWeatherAPI()
cpus = os.cpu_count()


def forecast_loading(*args):
    result = [
        DataFetchingTask(city, api_client).fetch_forecast() for city in args
    ]
    return result


def calculate_average_values(forecasts: list[ForecastResponse], queue: Queue):
    for forecast in forecasts:
        avg_data = DataCalculationTask(forecast).calculate_average_indicators()
        queue.put(avg_data)
    queue.put(None)


def save_aggregated_results(queue: Queue):
    to_save = []
    while msg := queue.get():
        logger.info(f'New message in queue {msg}')
        to_save.extend(msg)
    DataAggregationTask.save_results(to_save)


if __name__ == '__main__':
    q = Queue()

    max_workers = min(len(CITIES), os.cpu_count()) if cpus \
        else len(CITIES)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        results = pool.map(forecast_loading, CITIES.keys())

    results = list(itertools.chain.from_iterable(results))

    sender = Process(
        target=calculate_average_values,
        kwargs={'forecasts': results, 'queue': q}
    )
    consumer = Process(
        target=save_aggregated_results,
        kwargs={'queue': q}
    )
    sender.start()
    consumer.start()
    sender.join()
    consumer.join()

    cities = DataAnalyzingTask.visit_advice()
    print('Best cities to visit:', ','.join([city.title() for city in cities]))
