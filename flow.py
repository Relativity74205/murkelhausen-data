from datetime import timedelta, datetime

from prefect import flow
from prefect.client.schemas.schedules import IntervalSchedule

if __name__ == "__main__":
    flow.from_source(
        source="git@github.com:Relativity74205/murkelhausen-data.git",
        entrypoint="src/murkelhausen/flow.py:main_flow",
    ).serve(
        name="murkelhausen_flow",
        schedule=IntervalSchedule(
            interval=timedelta(hours=1),
            anchor_date=datetime(2023, 12, 1, 0),
            timezone="Europe/Berlin",
        )
        # version=__version__,  # TODO add version to murkelhausen-data
    )
