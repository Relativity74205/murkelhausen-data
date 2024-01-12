from datetime import timedelta, datetime

from prefect import flow, serve
from prefect.client.schemas.schedules import IntervalSchedule

from murkelhausen.prefect.flow_data import data_main_flow
from murkelhausen.prefect.flow_beowulf_backup import beowulf_backup_flow

if __name__ == "__main__":
    main = data_main_flow.to_deployment(
        name="murkelhausen-data",
        schedule=IntervalSchedule(
            interval=timedelta(hours=1),
            anchor_date=datetime(2023, 12, 1, 0),
            timezone="Europe/Berlin",
        )
        # version=__version__,  # TODO add project version to murkelhausen-data from pyproject.toml
    )
    backup = beowulf_backup_flow.to_deployment(
        name="beowulf-backup",
        schedule=IntervalSchedule(
            interval=timedelta(days=1),
            anchor_date=datetime(2023, 12, 1, 0),
            timezone="Europe/Berlin",
        )
        # version=__version__,  # TODO add project version to murkelhausen-data from pyproject.toml
    )

    serve(main, backup)
