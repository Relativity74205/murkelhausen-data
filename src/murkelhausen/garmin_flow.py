from datetime import date

from dateutil.relativedelta import relativedelta
from prefect import flow, task, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner

from murkelhausen import garmin


@flow(task_runner=ConcurrentTaskRunner())
def garmin_flow(measure_date: date = date.today() - relativedelta(days=1)):
    heart_rate_data(measure_date)


@task
def heart_rate_data(measure_date: date):
    logger = get_run_logger()
    garmin.get_heartrate_data(start_date=measure_date, logger=logger)


if __name__ == "__main__":
    garmin_flow()
