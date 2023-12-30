from datetime import date

from dateutil.relativedelta import relativedelta
from prefect import flow, task, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner

from murkelhausen import garmin


@flow(task_runner=ConcurrentTaskRunner())
def garmin_flow(
    start_date: date | None = None,
    end_date: date | None = None,
):
    """
    Default start date is always yesterday and end date is today,
    except when custom dates are specified.
    """
    if start_date is None:
        start_date = date.today() - relativedelta(days=1)
    if end_date is None:
        end_date = date.today()
    heart_rate_data(start_date=start_date, end_date=end_date)


@task
def heart_rate_data(start_date: date, end_date: date):
    logger = get_run_logger()
    garmin.get_heartrate_data(start_date=start_date, end_date=end_date, logger=logger)


if __name__ == "__main__":
    garmin_flow()
