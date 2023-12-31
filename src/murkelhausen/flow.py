from datetime import date, timedelta, datetime

from prefect import flow, get_run_logger, task
from prefect.client.schemas.schedules import IntervalSchedule

from murkelhausen.config import config
from murkelhausen.garmin_flow import garmin_flow
from murkelhausen.prefect_secret_block import MurkelHausenSecrets
from murkelhausen.util.logger import setup_logging

setup_logging()


@task
def get_secrets():
    logger = get_run_logger()
    logger.info("Getting secrets.")
    murkelhausen_secrets_block = MurkelHausenSecrets.load(
        config.app.prefect_secret_block_name
    )
    config.database.password = (
        murkelhausen_secrets_block.database_password.get_secret_value()
    )
    config.garmin_connect.password = (
        murkelhausen_secrets_block.garmin_password.get_secret_value()
    )
    logger.info("Finished getting secrets.")


@flow
def main_flow(
    start_date: date | None = None,
    end_date: date | None = None,
):
    get_secrets()
    logger = get_run_logger()
    logger.info("Starting Garmin main flow.")
    garmin_flow(start_date=start_date, end_date=end_date)
    logger.info("Finished Garmin main flow.")


if __name__ == "__main__":
    # replace with flow.from_source https://docs.prefect.io/latest/getting-started/quickstart/#step-4-make-your-code-schedulable
    main_flow.serve(
        name="murkelhausen_flow",
        schedule=IntervalSchedule(
            interval=timedelta(hours=1),
            anchor_date=datetime(2023, 12, 1, 0),
            timezone="Europe/Berlin",
        )
        # version=__version__,  # TODO add version to murkelhausen-data
    )
