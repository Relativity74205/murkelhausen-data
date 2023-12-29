import logging
from datetime import date, datetime

from garminconnect import Garmin
from sqlalchemy.orm import Mapped, mapped_column

from murkelhausen.persistance_layer.postgres import Base

log = logging.getLogger(__name__)


class HeartRateDailyStats(Base):
    __tablename__ = "heart_rate_daily"

    measure_date: Mapped[date] = mapped_column(primary_key=True)
    resting_heart_rate: Mapped[int | None]
    min_heart_rate: Mapped[int | None]
    max_heart_rate: Mapped[int | None]
    last_seven_days_avg_resting_heart_rate: Mapped[int | None]


class HeartRate(Base):
    __tablename__ = "heart_rate"

    tstamp: Mapped[datetime] = mapped_column(primary_key=True)
    heart_rate: Mapped[int] = mapped_column(nullable=True)


def _get_heart_rates(
    garmin: Garmin, measure_date: date
) -> tuple[HeartRateDailyStats, tuple[HeartRate, ...]]:
    data = garmin.get_heart_rates(measure_date)
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

    return heart_rates_daily, heart_rates
