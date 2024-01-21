from datetime import date

from garminconnect import Garmin
from prefect import task, get_run_logger

from murkelhausen import garmin


@task(task_run_name="garmin_client", tags=["garmin"])
def get_garmin_client() -> Garmin:
    return garmin.get_garmin_client()


@task(task_run_name="garmin_heart_rate_data_{measure_date}", tags=["garmin"])
def heart_rate_data(measure_date: date, garmin_client: Garmin) -> int:
    logger = get_run_logger()
    logger.info(f"Starting task 'garmin heart rate data' for {measure_date}")
    return garmin.get_heartrate_data(
        measure_date=measure_date, garmin_client=garmin_client, logger=logger
    )


@task(task_run_name="garmin_steps_data_{measure_date}", tags=["garmin"])
def steps_data(measure_date: date, garmin_client: Garmin) -> int:
    logger = get_run_logger()
    logger.info(f"Starting task 'garmin steps data' for {measure_date}")
    return garmin.get_steps_data(
        measure_date=measure_date, garmin_client=garmin_client, logger=logger
    )


@task(task_run_name="garmin_steps_daily_data_{measure_date}", tags=["garmin"])
def steps_daily_data(measure_date: date, garmin_client: Garmin) -> int:
    logger = get_run_logger()
    logger.info(f"Starting task 'garmin steps daily data' for {measure_date}.")
    return garmin.get_daily_steps_data(
        measure_date=measure_date,
        garmin_client=garmin_client,
        logger=logger,
    )


@task(task_run_name="garmin_floors_data_{measure_date}", tags=["garmin"])
def floors_data(measure_date: date, garmin_client: Garmin) -> int:
    logger = get_run_logger()
    logger.info(f"Starting task 'garmin floors data' for {measure_date}")
    return garmin.get_floors_data(
        measure_date=measure_date, garmin_client=garmin_client, logger=logger
    )


@task(task_run_name="garmin_stress_data_{measure_date}", tags=["garmin"])
def stress_data(measure_date: date, garmin_client: Garmin) -> int:
    logger = get_run_logger()
    logger.info(f"Starting task 'garmin stress data' for {measure_date}")
    return garmin.get_stress_data(
        measure_date=measure_date, garmin_client=garmin_client, logger=logger
    )


@task(task_run_name="garmin_body_battery_data_{measure_date}", tags=["garmin"])
def body_battery_data(measure_date: date, garmin_client: Garmin) -> int:
    logger = get_run_logger()
    logger.info(f"Starting task 'garmin body battery data' for {measure_date}")
    return garmin.get_body_battery_data(
        measure_date=measure_date, garmin_client=garmin_client, logger=logger
    )


@task(task_run_name="garmin_sleep_data_{measure_date}", tags=["garmin"])
def sleep_data(measure_date: date, garmin_client: Garmin) -> int:
    logger = get_run_logger()
    logger.info(f"Starting task 'garmin sleep data' for {measure_date}")
    return garmin.get_sleep_data(
        measure_date=measure_date, garmin_client=garmin_client, logger=logger
    )
