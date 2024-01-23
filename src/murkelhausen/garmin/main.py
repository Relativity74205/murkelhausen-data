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


def _unix_timestamp_millis_to_europe_berlin_datetime(t: int | None) -> datetime | None:
    if t is None:
        return None

    return datetime.fromtimestamp(t / 1000, tz=pytz.UTC).astimezone(
        pytz.timezone("Europe/Berlin")
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
                tstamp=_unix_timestamp_millis_to_europe_berlin_datetime(d[0]),
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


def get_daily_steps_data(*, measure_date: date, garmin_client: Garmin, logger) -> int:
    """Returns the amount of daily steps data points saved."""
    logger.info(f"Getting daily steps data for {measure_date}.")
    data = garmin_client.get_daily_steps(start=measure_date, end=measure_date)
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
            tstamp=_unix_timestamp_millis_to_europe_berlin_datetime(entry[0]),
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
            tstamp=_unix_timestamp_millis_to_europe_berlin_datetime(entry[0]),
            body_battery_status=entry[1],
            body_battery_level=entry[2],
            body_battery_version=entry[3],
        )
        for entry in data_stress.get("bodyBatteryValuesArray", tuple())
    )
    logger.info(f"Got {len(body_battery)} body battery data points. Saving.")
    save_objects(body_battery, upsert=True)
    logger.info("Saved body battery data. Done.")

    data_body = garmin_client.get_body_battery(measure_date.isoformat())
    body_battery_daily = objects.BodyBatteryDaily(
        calendar_date=date.fromisoformat(data_body[0]["date"]),
        charged=data_body[0]["charged"],
        drained=data_body[0]["drained"],
        dynamic_feedback_event=data_body[0].get("bodyBatteryDynamicFeedbackEvent", {}),
        end_of_day_dynamic_feedback_event=data_body[0].get(
            "endOfDayBodyBatteryDynamicFeedbackEvent", {}
        ),
    )
    save_objects((body_battery_daily,), upsert=True)
    logger.info("Saved body battery daily data. Done.")

    body_battery_activity_events = tuple(
        objects.BodyBatteryActivityEvent(
            tstamp_start=_unaware_utc_string_to_europe_berlin_datetime(
                entry["eventStartTimeGmt"]
            ),
            event_type=entry["eventType"],
            duration_seconds=int(entry["durationInMilliseconds"] / 1000),
            body_battery_impact=entry["bodyBatteryImpact"],
            feedback_type=entry["feedbackType"],
            short_feedback=entry["shortFeedback"],
        )
        for entry in data_body[0].get("bodyBatteryActivityEvent", tuple())
    )
    save_objects(body_battery_activity_events, upsert=True)
    logger.info("Saved body battery activity events data. Done.")

    return len(body_battery)


def _get_sleep_data_daily(data_sleep: dict, logger):
    daily_sleep = data_sleep["dailySleepDTO"]
    sleep_daily = objects.SleepDaily(
        calendar_date=date.fromisoformat(daily_sleep["calendarDate"]),
        sleep_time_seconds=daily_sleep["sleepTimeSeconds"],
        nap_time_seconds=daily_sleep["napTimeSeconds"],
        sleep_start_tstamp=_unix_timestamp_millis_to_europe_berlin_datetime(
            daily_sleep["sleepStartTimestampGMT"]
        ),
        sleep_end_tstamp=_unix_timestamp_millis_to_europe_berlin_datetime(
            daily_sleep["sleepEndTimestampGMT"]
        ),
        unmeasurable_sleep_seconds=daily_sleep["unmeasurableSleepSeconds"],
        deep_sleep_seconds=daily_sleep["deepSleepSeconds"],
        light_sleep_seconds=daily_sleep["lightSleepSeconds"],
        rem_sleep_seconds=daily_sleep["remSleepSeconds"],
        awake_sleep_seconds=daily_sleep["awakeSleepSeconds"],
        average_sp_o_2_value=daily_sleep["averageSpO2Value"],
        lowest_sp_o_2_value=daily_sleep["lowestSpO2Value"],
        highest_sp_o_2_value=daily_sleep["highestSpO2Value"],
        average_sp_o_2_hrsleep=daily_sleep["averageSpO2HRSleep"],
        average_respiration_value=daily_sleep["averageRespirationValue"],
        lowest_respiration_value=daily_sleep["lowestRespirationValue"],
        highest_respiration_value=daily_sleep["highestRespirationValue"],
        awake_count=daily_sleep["awakeCount"],
        avg_sleep_stress=daily_sleep["avgSleepStress"],
        sleep_score_feedback=daily_sleep["sleepScoreFeedback"],
        sleep_score_insight=daily_sleep["sleepScoreInsight"],
        sleep_score_personalized_insight=daily_sleep["sleepScorePersonalizedInsight"],
        restless_moments_count=data_sleep["restlessMomentsCount"],
        avg_overnight_hrv=data_sleep["avgOvernightHrv"],
        hrv_status=data_sleep["hrvStatus"],
        body_battery_change=data_sleep["bodyBatteryChange"],
        resting_heart_rate=data_sleep["restingHeartRate"],
        sleep_scores=daily_sleep["sleepScores"],
    )
    save_objects((sleep_daily,), upsert=True)
    logger.info("Saved sleep daily events data. Done.")


def get_sleep_data(*, measure_date: date, garmin_client: Garmin, logger) -> int:
    """Returns the amount of sleep data points saved."""
    logger.info(f"Getting sleep data for {measure_date}.")

    data_sleep = garmin_client.get_sleep_data(measure_date.isoformat())
    _get_sleep_data_daily(data_sleep, logger)

    sleep_movements = tuple(
        objects.SleepMovement(
            tstamp_start=_unaware_utc_string_to_europe_berlin_datetime(
                entry["startGMT"]
            ),
            tstamp_end=_unaware_utc_string_to_europe_berlin_datetime(entry["endGMT"]),
            activity_level=entry["activityLevel"],
        )
        for entry in data_sleep["sleepMovement"]
    )
    save_objects(sleep_movements, upsert=True)
    logger.info(f"Saved sleep movements data ({len(sleep_movements)} rows). Done.")

    sleep_levels = tuple(
        objects.SleepLevels(
            tstamp_start=_unaware_utc_string_to_europe_berlin_datetime(
                entry["startGMT"]
            ),
            tstamp_end=_unaware_utc_string_to_europe_berlin_datetime(entry["endGMT"]),
            activity_level=int(entry["activityLevel"]),
        )
        for entry in data_sleep["sleepLevels"]
    )
    save_objects(sleep_levels, upsert=True)
    logger.info(f"Saved sleep levels data ({len(sleep_levels)} rows). Done.")

    sleep_restless_moments = tuple(
        objects.SleepRestlessMoments(
            tstamp=_unix_timestamp_millis_to_europe_berlin_datetime(entry["startGMT"]),
            value=int(entry["value"]),
        )
        for entry in data_sleep["sleepRestlessMoments"]
    )
    save_objects(sleep_restless_moments, upsert=True)
    logger.info(
        f"Saved sleep restless moments data ({len(sleep_restless_moments)} rows). Done."
    )

    sleep_spo2_data = tuple(
        objects.SleepSPO2Data(
            tstamp=_unaware_utc_string_to_europe_berlin_datetime(
                entry["epochTimestamp"]
            ),
            epoch_duration=entry["epochDuration"],
            spo2_value=entry["spo2Reading"],
            reading_confidence=entry["readingConfidence"],
        )
        for entry in data_sleep["wellnessEpochSPO2DataDTOList"]
    )
    save_objects(sleep_spo2_data, upsert=True)
    logger.info(f"Saved sleep spo2 data ({len(sleep_spo2_data)} rows). Done.")

    sleep_respiration_data = tuple(
        objects.SleepRespirationData(
            tstamp=_unix_timestamp_millis_to_europe_berlin_datetime(
                entry["startTimeGMT"]
            ),
            respiration_value=int(entry["respirationValue"]),
        )
        for entry in data_sleep["wellnessEpochRespirationDataDTOList"]
    )
    save_objects(sleep_respiration_data, upsert=True)
    logger.info(
        f"Saved sleep respiration data ({len(sleep_respiration_data)} rows). Done."
    )

    sleep_heart_rates = tuple(
        objects.SleepHeartRate(
            tstamp=_unix_timestamp_millis_to_europe_berlin_datetime(entry["startGMT"]),
            heart_rate=entry["value"],
        )
        for entry in data_sleep["sleepHeartRate"]
    )
    save_objects(sleep_heart_rates, upsert=True)
    logger.info(f"Saved sleep heart rate data ({len(sleep_heart_rates)} rows). Done.")

    sleep_stress_data = tuple(
        objects.SleepStress(
            tstamp=_unix_timestamp_millis_to_europe_berlin_datetime(entry["startGMT"]),
            stress_level=int(entry["value"]),
        )
        for entry in data_sleep["sleepStress"]
    )
    save_objects(sleep_stress_data, upsert=True)
    logger.info(f"Saved sleep stress data ({len(sleep_stress_data)} rows). Done.")

    sleep_body_battery_data = tuple(
        objects.SleepBodyBattery(
            tstamp=_unix_timestamp_millis_to_europe_berlin_datetime(entry["startGMT"]),
            body_battery_level=int(entry["value"]),
        )
        for entry in data_sleep["sleepBodyBattery"]
    )
    save_objects(sleep_body_battery_data, upsert=True)
    logger.info(
        f"Saved sleep body battery data ({len(sleep_body_battery_data)} rows). Done."
    )

    sleep_hrv_data = tuple(
        objects.SleepHRVData(
            tstamp=_unix_timestamp_millis_to_europe_berlin_datetime(entry["startGMT"]),
            hrv_value=int(entry["value"]),
        )
        for entry in data_sleep["hrvData"]
    )
    save_objects(sleep_hrv_data, upsert=True)
    logger.info(f"Saved sleep hrv data ({len(sleep_hrv_data)} rows). Done.")

    return (
        len(sleep_movements)
        + len(sleep_levels)
        + len(sleep_restless_moments)
        + len(sleep_spo2_data)
        + len(sleep_respiration_data)
        + len(sleep_heart_rates)
        + len(sleep_stress_data)
        + len(sleep_body_battery_data)
        + len(sleep_hrv_data)
    )
