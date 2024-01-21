import typing
from collections import defaultdict
from datetime import date
from typing import Literal

from dateutil.relativedelta import relativedelta
from prefect import flow, get_run_logger
from prefect.runtime import flow_run
from prefect.task_runners import ConcurrentTaskRunner
from prefect.tasks import Task
from prefect.artifacts import create_table_artifact

from murkelhausen.prefect import tasks_garmin


TASK_NAMES = Literal[
    "heart_rate_data",
    "steps_data",
    "floors_data",
    "stress_data",
    "body_battery_data",
    "sleep_data",
]


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
def garmin_flow(
    start_date: date | None = None,
    end_date: date | None = None,
    task_to_run: TASK_NAMES | None = None,
):
    """
    Default start date is always yesterday and end date is today,
    except when custom dates are specified.
    """
    logger = get_run_logger()
    if task_to_run is not None:
        tasks: dict[str, Task] = {str(task_to_run): getattr(tasks_garmin, task_to_run)}
    else:
        tasks = {
            task_name: getattr(tasks_garmin, task_name)
            for task_name in typing.get_args(TASK_NAMES)
        }

    if start_date is None:
        start_date = date.today() - relativedelta(days=1)
    if end_date is None:
        end_date = date.today()

    logger.info(
        f"Starting garmin flow with {start_date=} and {end_date=}. Retrieving garmin client."
    )
    garmin_client = tasks_garmin.get_garmin_client()
    logger.info("Retrieving garmin client. Starting daily data task(s).")

    futures_daily = defaultdict(dict)
    for count_dates in range((end_date - start_date).days + 1):
        this_date = start_date + relativedelta(days=count_dates)
        for metric_name, task_callable in tasks.items():
            futures_daily[metric_name][this_date] = task_callable.submit(
                measure_date=this_date, garmin_client=garmin_client
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


if __name__ == "__main__":
    garmin_flow()
