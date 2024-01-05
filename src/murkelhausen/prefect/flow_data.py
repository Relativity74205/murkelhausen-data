from datetime import date, timedelta, datetime

from prefect import flow, get_run_logger, task
from prefect.client.schemas.schedules import IntervalSchedule

from murkelhausen.config import config
from murkelhausen.prefect.subflow_garmin import garmin_flow
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


@flow(flow_run_name=_generate_flowrun_name)
def data_main_flow(start_date: date | None = None, end_date: date | None = None):
    logger = get_run_logger()
    logger.info("Getting secrets.")
    get_secrets()
    logger.info("Finished getting secrets.")
    logger.info(f"Starting Garmin main flow with {start_date=} and {end_date=}.")
    garmin_flow(start_date=start_date, end_date=end_date)
    logger.info(f"Finished Garmin main flow with {start_date=} and {end_date=}.")


if __name__ == "__main__":
    data_main_flow.serve(
        name="murkelhausen_flow",
        schedule=IntervalSchedule(
            interval=timedelta(hours=1),
            anchor_date=datetime(2023, 12, 1, 0),
            timezone="Europe/Berlin",
        )
        # version=__version__,  # TODO add version to murkelhausen-data
    )
