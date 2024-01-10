from datetime import date

from dateutil.relativedelta import relativedelta
from garminconnect import Garmin
from prefect import flow, task, get_run_logger
from prefect.runtime import flow_run
from prefect.task_runners import ConcurrentTaskRunner
from prefect.artifacts import create_table_artifact

from murkelhausen import garmin


def _generate_flowrun_name():
    """Generates a flow run name based on the parameters of the flow run."""
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
    task_runner=ConcurrentTaskRunner(),  # TODO test DaskRunner (https://prefecthq.github.io/prefect-dask/)
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
    logger.info("Finished retrieving garmin client.")

    logger.info("Starting heart rate data task(s).")

    heart_rate_data_futures = {}
    for count_dates in range((end_date - start_date).days + 1):
        measure_date = start_date + relativedelta(days=count_dates)
        heart_rate_data_futures[measure_date] = heart_rate_data.submit(
            measure_date=measure_date, garmin_client=garmin_client
        )
    heart_rate_data_points = {
        measure_date.isoformat(): future.result()
        for measure_date, future in heart_rate_data_futures.items()
    }
    logger.info("Finished heart rate data task(s).")

    logger.info("Creating garmin report. Foo!")
    garmin_report = [
        {"metric": "heart_rate_data_points"} | heart_rate_data_points,
        {"metric": "foo", "2024-01-09": 1, "2024-01-10": 2},
    ]
    logger.info("{garmin_report}")

    create_table_artifact(
        key="garmin-report",
        table=garmin_report,
        description="Downloaded garmin data",
    )
    logger.info("Created garmin report.")


@task(task_run_name="garmin_client")
def get_garmin_client() -> Garmin:
    return garmin.get_garmin_client()


@task(task_run_name="garmin_heart_rate_data_{measure_date}")
def heart_rate_data(measure_date: date, garmin_client: Garmin) -> int:
    logger = get_run_logger()
    logger.info(f"Starting task 'garmin heart rate data' for {measure_date}")
    return garmin.get_heartrate_data(
        measure_date=measure_date, garmin_client=garmin_client, logger=logger
    )


if __name__ == "__main__":
    garmin_flow()
