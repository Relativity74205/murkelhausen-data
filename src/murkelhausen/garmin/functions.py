import logging
from datetime import date, datetime

from garminconnect import Garmin
from sqlalchemy.orm import Mapped, mapped_column

from murkelhausen.persistance_layer.postgres import Base

log = logging.getLogger(__name__)


class HeartRateDailyStats(Base):
    __tablename__ = "heart_rate_daily"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    measure_date: Mapped[date]
    resting_heart_rate: Mapped[int]
    min_heart_rate: Mapped[int]
    max_heart_rate: Mapped[int]
    last_seven_days_avg_resting_heart_rate: Mapped[int]


class HeartRate(Base):
    __tablename__ = "heart_rate"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    tstamp: Mapped[datetime]
    heart_rate: Mapped[int] = mapped_column(nullable=True)


def get_heart_rates(
    garmin: Garmin, measure_date: date
) -> tuple[HeartRateDailyStats, tuple[HeartRate, ...]]:
    data = garmin.get_heart_rates(measure_date)
    # log.debug(f"{data=}")
    heart_rates_daily = HeartRateDailyStats(
        measure_date=measure_date,
        resting_heart_rate=data["restingHeartRate"],
        min_heart_rate=data["minHeartRate"],
        max_heart_rate=data["maxHeartRate"],
        last_seven_days_avg_resting_heart_rate=data["lastSevenDaysAvgRestingHeartRate"],
    )
    heart_rates = tuple(
        HeartRate(
            tstamp=datetime.fromtimestamp(d[0] / 1000),
            heart_rate=d[1],
        )
        for d in data["heartRateValues"]
    )
    return heart_rates_daily, heart_rates
