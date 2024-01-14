import json

import pytz
from datetime import date, datetime, timezone

from garminconnect import Garmin

from murkelhausen.config import config
from murkelhausen.garmin.auth import get_auth_token

from murkelhausen.garmin import objects
from murkelhausen.persistance_layer import save_objects


def get_garmin_client() -> Garmin:
    garmin = Garmin()
    try:
        garmin.login(config.garmin_connect.auth_token_path)
    except FileNotFoundError:
        get_auth_token()
        garmin.login(config.garmin_connect.auth_token_path)
    return garmin


def _unaware_utc_string_to_europe_berlin_datetime(s: str) -> datetime:
    return (
        datetime.fromisoformat(s)
        .replace(tzinfo=timezone.utc)
        .astimezone(pytz.timezone("Europe/Berlin"))
    )


def get_heartrate_data(*, measure_date: date, garmin_client: Garmin, logger) -> int:
    """Returns the amount of heart rate data points saved."""
    logger.info(f"Getting heart rate data for {measure_date}.")
    data = garmin_client.get_heart_rates(measure_date)
    heart_rates_daily = objects.HeartRateDailyStats(
        measure_date=measure_date,
        resting_heart_rate=data["restingHeartRate"],
        min_heart_rate=data["minHeartRate"],
        max_heart_rate=data["maxHeartRate"],
        last_seven_days_avg_resting_heart_rate=data["lastSevenDaysAvgRestingHeartRate"],
    )
    if data["heartRateValues"] is not None:
        heart_rates = tuple(
            objects.HeartRate(
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
        objects.Steps(
            tstamp_start=_unaware_utc_string_to_europe_berlin_datetime(d["startGMT"]),
            tstamp_end=_unaware_utc_string_to_europe_berlin_datetime(d["endGMT"]),
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


def get_daily_steps_data(
    *, start_date: date, end_date: date, garmin_client: Garmin, logger
) -> int:
    """Returns the amount of daily steps data points saved."""
    logger.info(f"Getting daily steps data for {start_date=} and {end_date=}.")
    data = garmin_client.get_daily_steps(start=start_date, end=end_date)
    steps = tuple(
        objects.StepsDaily(
            calendar_date=date.fromisoformat(d["calendarDate"]),
            total_steps=d["totalSteps"],
            total_distance=d["totalDistance"],
            step_goal=d["stepGoal"],
        )
        for d in data
    )
    logger.info(f"Got {len(steps)} daily steps data points. Saving.")
    save_objects(steps, upsert=True)
    logger.info("Saved daily steps data. Done.")

    return len(steps)


def get_floors_data(*, measure_date: date, garmin_client: Garmin, logger) -> int:
    """Returns the amount of floors data points saved."""
    logger.info(f"Getting floors data for {measure_date}.")
    data = garmin_client.get_floors(measure_date)
    floors = tuple(
        objects.Floors(
            tstamp_start=_unaware_utc_string_to_europe_berlin_datetime(entry[0]),
            tstamp_end=_unaware_utc_string_to_europe_berlin_datetime(entry[1]),
            floorsAscended=entry[2],
            floorsDescended=entry[3],
        )
        for entry in data["floorValuesArray"]
    )
    logger.info(f"Got {len(floors)} floors data points. Saving.")
    save_objects(floors, upsert=True)
    logger.info("Saved floors data. Done.")

    return len(floors)


def get_stress_data(*, measure_date: date, garmin_client: Garmin, logger) -> int:
    """Returns the amount of stress battery data points saved."""
    logger.info(f"Getting stress data for {measure_date}.")
    data = garmin_client.get_stress_data(measure_date.isoformat())
    stress = tuple(
        objects.Stress(
            tstamp=datetime.fromtimestamp(entry[0] / 1000),
            stress_level=entry[1],
        )
        for entry in data["stressValuesArray"]
    )
    stress_daily = objects.StressDaily(
        calendar_date=date.fromisoformat(data["calendarDate"]),
        max_stress_level=data["maxStressLevel"],
        avg_stress_level=data["avgStressLevel"],
        stress_chart_value_offset=data["stressChartValueOffset"],
        stress_chart_y_axis_origin=data["stressChartYAxisOrigin"],
    )
    logger.info(f"Got {len(stress)} stress data points. Saving.")
    save_objects(stress, upsert=True)
    logger.info("Saving daily stress data.")
    save_objects((stress_daily,), upsert=True)
    logger.info("Saved stress data. Done.")

    return len(stress)


def get_body_battery_data(*, measure_date: date, garmin_client: Garmin, logger) -> int:
    """Returns the amount of body battery data points saved."""
    logger.info(f"Getting body battery data for {measure_date}.")
    # get_stress_data route gets better detailed information than get_body_battery_data
    data_stress = garmin_client.get_stress_data(measure_date.isoformat())
    body_battery = tuple(
        objects.BodyBattery(
            tstamp=datetime.fromtimestamp(entry[0] / 1000),
            body_battery_status=entry[1],
            body_battery_level=entry[2],
            body_battery_version=entry[3],
        )
        for entry in data_stress["bodyBatteryValuesArray"]
    )
    logger.info(f"Got {len(body_battery)} body battery data points. Saving.")
    save_objects(body_battery, upsert=True)
    logger.info("Saved body battery data. Done.")

    data_body = garmin_client.get_body_battery(measure_date.isoformat())
    body_battery_daily = objects.BodyBatteryDaily(
        calendar_date=date.fromisoformat(data_body[0]["calendarDate"]),
        charged=data_body[0]["charged"],
        drained=data_body[0]["drained"],
    )
    save_objects((body_battery_daily,), upsert=True)
    logger.info("Saved body battery daily data. Done.")

    # TODO: bodyBatteryDynamicFeedbackEvent
    # TODO: bodyBatteryActivityEvent
    # TODO: endOfDayBodyBatteryDynamicFeedbackEvent

    return len(body_battery)
