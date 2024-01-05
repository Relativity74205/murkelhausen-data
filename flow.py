from datetime import timedelta, datetime

from prefect import flow, serve
from prefect.client.schemas.schedules import IntervalSchedule


if __name__ == "__main__":
    main = flow.from_source(
        source="git@github.com:Relativity74205/murkelhausen-data.git",
        entrypoint="src/murkelhausen/download.py:main_flow",
    ).to_deployment(
        name="murkelhausen_flow",
        schedule=IntervalSchedule(
            interval=timedelta(hours=1),
            anchor_date=datetime(2023, 12, 1, 0),
            timezone="Europe/Berlin",
        )
        # version=__version__,  # TODO add project version to murkelhausen-data from pyproject.toml
    )
    backup = flow.from_source(
        source="git@github.com:Relativity74205/murkelhausen-data.git",
        entrypoint="src/murkelhausen/backup.py:backup_flow",
    ).to_deployment(
        name="backup_flow",
        schedule=IntervalSchedule(
            interval=timedelta(days=1),
            anchor_date=datetime(2023, 12, 1, 0),
            timezone="Europe/Berlin",
        )
        # version=__version__,  # TODO add project version to murkelhausen-data from pyproject.toml
    )

    serve(main, backup)
