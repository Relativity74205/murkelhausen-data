from datetime import date, timedelta

import garth
from garminconnect import Garmin

from murkelhausen.config import config
from murkelhausen.garmin.functions import _get_heart_rates
from murkelhausen.persistance_layer import save_objects


def get_auth_token():
    email = config.garmin_connect.email
    password = config.garmin_connect.password

    garth.login(email, password)
    garth.save(config.garmin_connect.auth_token_path)


def get_garmin_client() -> Garmin:
    garmin = Garmin()
    try:
        garmin.login(config.garmin_connect.auth_token_path)
    except:
        get_auth_token()
        garmin.login(config.garmin_connect.auth_token_path)
    return garmin


def get_heartrate_data(
    *, start_date: date, end_date: date | None = None, logger
) -> None:
    garmin_client = get_garmin_client()
    if end_date is None:
        end_date = start_date

    logger.info(f"Getting heart rate data from {start_date} to {end_date}.")

    for count_dates in range((end_date - start_date).days + 1):
        measure_date = start_date + timedelta(days=count_dates)

        logger.info(f"Saving heart rate data for {measure_date}")
        heart_rates_daily, heart_rates = _get_heart_rates(garmin_client, measure_date)

        logger.info(f"Got {len(heart_rates)} heart rate data points. Saving.")
        save_objects((heart_rates_daily,), upsert=True)
        logger.info("Saved daily heart rate data.")
        save_objects(heart_rates)
        logger.info("Saved detailed heart rate data. Done.")
