import logging
from datetime import date, datetime

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


class Steps(Base):
    __tablename__ = "steps"

    tstamp_start: Mapped[datetime] = mapped_column(
        primary_key=True
    )  # TODO timezone is off
    tstamp_end: Mapped[datetime]  # TODO timezone is off
    steps: Mapped[int | None]
    pushes: Mapped[int | None]
    primaryActivityLevel: Mapped[str | None]
    activityLevelConstant: Mapped[bool | None]


class StepsDaily(Base):
    """
    [{
        "calendarDate": "2024-01-13",
        "totalSteps": 12513,
        "totalDistance": 10408,
        "stepGoal": 9060
    }]
    """

    __tablename__ = "steps_daily"

    calendar_date: Mapped[date] = mapped_column(primary_key=True)
    total_steps: Mapped[int | None]
    total_distance: Mapped[int | None]
    step_goal: Mapped[int | None]


class Floors(Base):
    __tablename__ = "floors"

    tstamp_start: Mapped[datetime] = mapped_column(
        primary_key=True
    )  # TODO timezone is off
    tstamp_end: Mapped[datetime]  # TODO timezone is off
    floorsAscended: Mapped[int | None]
    floorsDescended: Mapped[int | None]
