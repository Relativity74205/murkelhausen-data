from datetime import date, datetime
from typing import Literal

from prefect import flow, get_run_logger, task

from murkelhausen.config import config
from murkelhausen.prefect import subflow_garmin
from murkelhausen.prefect.prefect_secret_block import MurkelHausenSecrets
from murkelhausen.util.logger import setup_logging

setup_logging()


def _generate_flowrun_name():
    now = datetime.now()
    return f"murkelhausen-data-main_{now.year}-{now.month}-{now.day}-{now.hour}"


@task
def get_secrets():
    murkelhausen_secrets_block = MurkelHausenSecrets.load(
        config.app.prefect_secret_block_name
    )
    config.database.password = (
        murkelhausen_secrets_block.database_password.get_secret_value()
    )
    config.garmin_connect.password = (
        murkelhausen_secrets_block.garmin_password.get_secret_value()
    )


@flow(
    flow_run_name=_generate_flowrun_name,
    retries=3,
    retry_delay_seconds=60,
    description="Main flow.",
)
def data_main_flow(
    start_date: date | None = None,
    end_date: date | None = None,
    task_to_run: subflow_garmin.TASK_NAMES | None = None,
):
    logger = get_run_logger()
    logger.info("Getting secrets.")
    get_secrets()
    logger.info("Finished getting secrets.")
    logger.info(
        f"Starting Garmin main flow with {start_date=} and {end_date=} and {task_to_run=}."
    )
    subflow_garmin.garmin_flow(
        start_date=start_date, end_date=end_date, task_to_run=task_to_run
    )
    logger.info(f"Finished Garmin main flow with {start_date=} and {end_date=}.")


if __name__ == "__main__":
    data_main_flow()
