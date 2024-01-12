import json
from datetime import date, datetime

from garminconnect import Garmin

from murkelhausen.config import config
from murkelhausen.garmin.auth import get_auth_token

from murkelhausen.garmin.objects import HeartRateDailyStats, HeartRate, Steps, Floors
from murkelhausen.persistance_layer import save_objects


def get_garmin_client() -> Garmin:
    garmin = Garmin()
    try:
        garmin.login(config.garmin_connect.auth_token_path)
    except FileNotFoundError:
        get_auth_token()
        garmin.login(config.garmin_connect.auth_token_path)
    return garmin


def get_heartrate_data(*, measure_date: date, garmin_client: Garmin, logger) -> int:
    """Returns the amount of heart rate data points saved."""
    logger.info(f"Getting heart rate data for {measure_date}.")
    data = garmin_client.get_heart_rates(measure_date)
    heart_rates_daily = HeartRateDailyStats(
        measure_date=measure_date,
        resting_heart_rate=data["restingHeartRate"],
        min_heart_rate=data["minHeartRate"],
        max_heart_rate=data["maxHeartRate"],
        last_seven_days_avg_resting_heart_rate=data["lastSevenDaysAvgRestingHeartRate"],
    )
    if data["heartRateValues"] is not None:
        heart_rates = tuple(
            HeartRate(
                tstamp=datetime.fromtimestamp(d[0] / 1000),
                heart_rate=d[1],
            )
            for d in data["heartRateValues"]
        )
    else:
        heart_rates = tuple()

    logger.info(f"Got {len(heart_rates)} heart rate data points. Saving.")
    save_objects((heart_rates_daily,), upsert=True)
    logger.info("Saved daily heart rate data.")
    save_objects(heart_rates, upsert=True)
    logger.info("Saved detailed heart rate data. Done.")

    return len(heart_rates)


def get_steps_data(*, measure_date: date, garmin_client: Garmin, logger) -> int:
    """Returns the amount of steps data points saved."""
    logger.info(f"Getting steps data for {measure_date}.")
    data = garmin_client.get_steps_data(measure_date)
    steps = tuple(
        Steps(
            startGMT=datetime.fromisoformat(d["startGMT"]),
            endGMT=datetime.fromisoformat(d["endGMT"]),
            steps=d["steps"],
            pushes=d["pushes"],
            primaryActivityLevel=d["primaryActivityLevel"],
            activityLevelConstant=d["activityLevelConstant"],
        )
        for d in data
    )
    logger.info(f"Got {len(steps)} steps data points. Saving.")
    save_objects(steps, upsert=True)
    logger.info("Saved steps data. Done.")

    return len(steps)


def get_floors_data(*, measure_date: date, garmin_client: Garmin, logger) -> int:
    """Returns the amount of floors data points saved."""
    logger.info(f"Getting floors data for {measure_date}.")
    data = garmin_client.get_floors(measure_date)
    floors = tuple(
        Floors(
            startGMT=datetime.fromisoformat(entry[0]),
            endGMT=datetime.fromisoformat(entry[1]),
            floorsAscended=entry[2],
            floorsDescended=entry[3],
        )
        for entry in data["floorValuesArray"]
    )
    logger.info(f"Got {len(floors)} floors data points. Saving.")
    save_objects(floors, upsert=True)
    logger.info("Saved floors data. Done.")

    return len(floors)
