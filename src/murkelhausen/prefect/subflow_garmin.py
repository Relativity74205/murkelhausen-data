from collections import defaultdict
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

    logger.info("Starting daily data task(s).")

    futures_daily = defaultdict(dict)
    for count_dates in range((end_date - start_date).days + 1):
        measure_date = start_date + relativedelta(days=count_dates)
        futures_daily["heart_rate_data_points"][measure_date] = heart_rate_data.submit(
            measure_date=measure_date, garmin_client=garmin_client
        )
        futures_daily["steps_data_points"][measure_date] = steps_data.submit(
            measure_date=measure_date, garmin_client=garmin_client
        )
        futures_daily["floors_data_points"][measure_date] = floors_data.submit(
            measure_date=measure_date, garmin_client=garmin_client
        )

    logger.info("Finished starting daily data task(s).")

    logger.info("Starting to collect daily task results.")
    daily_data_points = {}
    for metric, futures_daily in futures_daily.items():
        daily_data_points[metric] = {
            measure_date.isoformat(): future.result()
            for measure_date, future in futures_daily.items()
        }
    garmin_daily_report = [
        {"metric": metric} | metric_results
        for metric, metric_results in daily_data_points.items()
    ]

    logger.info("Finished collecting daily task results.")

    create_table_artifact(
        key="garmin-daily-report",
        table=garmin_daily_report,
        description="Downloaded garmin daily data.",
    )
    logger.info("Created garmin report for daily data.")

    logger.info("Starting date range data task(s).")
    futures_date_range = {}
    futures_date_range["steps_daily_data_points"] = steps_daily_data.submit(
        start_date=start_date, end_date=end_date, garmin_client=garmin_client
    )
    logger.info("Finished starting date range data task(s).")

    logger.info("Starting to collect date range task results.")
    date_range_data_points = {}
    for metric, date_range_future in futures_date_range.items():
        date_range_data_points[metric] = date_range_future.result()

    garmin_date_range_report = [
        {"metric": metric, "new entries": metric_results}
        for metric, metric_results in date_range_data_points.items()
    ]

    logger.info("Finished collecting daily task results.")

    create_table_artifact(
        key="garmin-date-range-report",
        table=garmin_date_range_report,
        description="Downloaded garmin date range data.",
    )
    logger.info("Created garmin report for daily data.")


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


@task(task_run_name="garmin_steps_data_{measure_date}")
def steps_data(measure_date: date, garmin_client: Garmin) -> int:
    logger = get_run_logger()
    logger.info(f"Starting task 'garmin steps data' for {measure_date}")
    return garmin.get_steps_data(
        measure_date=measure_date, garmin_client=garmin_client, logger=logger
    )


@task(task_run_name="garmin_steps_daily_data_{start_date}_{end_date}")
def steps_daily_data(start_date: date, end_date: date, garmin_client: Garmin) -> int:
    logger = get_run_logger()
    logger.info(
        f"Starting task 'garmin steps daily data' for {steps_data=} and {end_date=}."
    )
    return garmin.get_daily_steps_data(
        start_date=start_date,
        end_date=end_date,
        garmin_client=garmin_client,
        logger=logger,
    )


@task(task_run_name="garmin_floors_data_{measure_date}")
def floors_data(measure_date: date, garmin_client: Garmin) -> int:
    logger = get_run_logger()
    logger.info(f"Starting task 'garmin floors data' for {measure_date}")
    return garmin.get_floors_data(
        measure_date=measure_date, garmin_client=garmin_client, logger=logger
    )


if __name__ == "__main__":
    garmin_flow()
