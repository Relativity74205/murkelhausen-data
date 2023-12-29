from datetime import date

from prefect import flow, task, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner

from murkelhausen import garmin

INITIAL_DATE = date(2023, 12, 1)


@flow(task_runner=ConcurrentTaskRunner())
def garmin_flow(data_date: date = date.today()):
    heart_rate_data(data_date)


@task
def heart_rate_data(data_date: date):
    logger = get_run_logger()
    garmin.get_heartrate_data(data_date, logger=logger)


if __name__ == "__main__":
    garmin_flow()
