from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime

from dataclasses_avroschema import AvroModel
from garminconnect import Garmin


class EnhancedAvroModel(ABC, AvroModel):
    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def get_topic_name(self):
        pass


@dataclass
class HeartRateDailyStats(EnhancedAvroModel):
    measure_date: date
    resting_heart_rate: int
    min_heart_rate: int
    max_heart_rate: int
    last_seven_days_avg_resting_heart_rate: int

    @property
    def get_topic_name(self):
        return "garmin_heart_rate_daily_stats"


@dataclass
class HeartRate(EnhancedAvroModel):
    tstamp: datetime
    heart_rate: int

    @property
    def get_topic_name(self):
        return "garmin_heart_rates"


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
