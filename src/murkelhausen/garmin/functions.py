from datetime import date, datetime

from garminconnect import Garmin
from sqlalchemy.orm import Mapped, mapped_column

from murkelhausen.persistance_layer.postgres import Base


def get_heart_rates(
    garmin: Garmin, measure_date: date
) -> tuple[HeartRateDailyStats, tuple[HeartRate, ...]]:
    data = garmin.get_heart_rates(measure_date)
    daily_stats = HeartRateDailyStats(
        measure_date=measure_date,
        resting_heart_rate=data["restingHeartRate"],
        min_heart_rate=data["minHeartRate"],
        max_heart_rate=data["maxHeartRate"],
        last_seven_days_avg_resting_heart_rate=data["sevenDayAvgRestingHeartRate"],
    )
    heart_rates = tuple(
        HeartRate(
            tstamp=datetime.fromtimestamp(d[0]),
            heart_rate=d[1],
        )
        for d in data["heartRateValues"]
    )
    return daily_stats, heart_rates
