from datetime import date

from dateutil.relativedelta import relativedelta
from garminconnect import Garmin
from prefect import flow, task, get_run_logger
from prefect.runtime import flow_run
from prefect.task_runners import ConcurrentTaskRunner

from murkelhausen import garmin


def _generate_flowrun_name():
    parameters = flow_run.parameters
    start_date = parameters["start_date"]
    end_date = parameters["end_date"]
    flowrun_name = "garmin-flow"
    if start_date is not None:
        flowrun_name += f"_{start_date}"
    if end_date is not None:
        flowrun_name += f"_{end_date}"
    if start_date is None and end_date is None:
        flowrun_name += "_default"
    return flowrun_name


@flow(
    task_runner=ConcurrentTaskRunner(),
    flow_run_name=_generate_flowrun_name,
)
def garmin_flow(start_date: date | None = None, end_date: date | None = None):
    """
    Default start date is always yesterday and end date is today,
    except when custom dates are specified.
    """
    logger = get_run_logger()
    if start_date is None:
        start_date = date.today() - relativedelta(days=1)
    if end_date is None:
        end_date = date.today()

    logger.info(
        f"Starting garmin flow with {start_date=} and {end_date=}. Retrieving garmin client."
    )
    garmin_client = get_garmin_client()
    logger.info(f"Finished retrieving garmin client.")

    logger.info(f"Starting heart rate data task(s).")
    for count_dates in range((end_date - start_date).days + 1):
        measure_date = start_date + relativedelta(days=count_dates)
        heart_rate_data.submit(measure_date=measure_date, garmin_client=garmin_client)


@task(task_run_name="garmin_client")
def get_garmin_client() -> Garmin:
    return garmin.get_garmin_client()


@task(task_run_name="garmin_heart_rate_data_{measure_date}")
def heart_rate_data(measure_date: date, garmin_client: Garmin) -> None:
    logger = get_run_logger()
    logger.info(f"Starting task 'garmin heart rate data' for {measure_date}")
    garmin.get_heartrate_data(
        measure_date=measure_date, garmin_client=garmin_client, logger=logger
    )


if __name__ == "__main__":
    garmin_flow()
