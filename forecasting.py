from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, Queue

from api_client import YandexWeatherAPI
from forecast_dataclasses.forecast_response import ForecastResponse
from services.logger import logger
from tasks import (DataAggregationTask, DataAnalyzingTask, DataCalculationTask,
                   DataFetchingTask)
from utils import CITIES

api_client = YandexWeatherAPI()


def calculate_average_values(forecasts: list[ForecastResponse], queue: Queue):

    processes = []
    for forecast in forecasts:
        # The pool looks better, but the readme says that you need to use different
        # method to init processes/threads
        process = Process(
            target=DataCalculationTask(forecast).calculate_average_indicators,
            kwargs={'queue': queue}
        )
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    queue.put(None)


def save_aggregated_results(queue: Queue):
    to_save = []
    while msg := queue.get():
        logger.info(f'New message in queue {msg}')
        to_save.append(msg)

    DataAggregationTask.save_results(to_save)


if __name__ == '__main__':
    q = Queue()

    with ThreadPoolExecutor() as pool:
        results = pool.map(
            DataFetchingTask(api_client).fetch_forecast,
            CITIES.keys()
        )

    forecast_responses = list(results)

    calculate_average_values(forecasts=forecast_responses, queue=q)
    save_aggregated_results(q)

    logger.info('\nBest cities to visit: %s' % ','.join(DataAnalyzingTask.visit_advice()))
