from datetime import date

from dateutil.relativedelta import relativedelta
from garminconnect import Garmin
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
    garmin_client = get_garmin_client()
    if start_date is None:
        start_date = date.today() - relativedelta(days=1)
    if end_date is None:
        end_date = date.today()

    for count_dates in range((end_date - start_date).days + 1):
        measure_date = start_date + relativedelta(days=count_dates)
        heart_rate_data(measure_date=measure_date, garmin_client=garmin_client)


@task
def get_garmin_client() -> Garmin:
    return garmin.get_garmin_client()


@task
def heart_rate_data(measure_date: date, garmin_client: Garmin) -> None:
    logger = get_run_logger()
    logger.info(f"Starting task 'garmin heart rate data' for {measure_date}")
    garmin.get_heartrate_data(
        measure_date=measure_date, garmin_client=garmin_client, logger=logger
    )


if __name__ == "__main__":
    garmin_flow()
