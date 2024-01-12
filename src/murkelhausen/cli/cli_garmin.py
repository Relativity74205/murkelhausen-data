from datetime import datetime, date
from logging import getLogger
from typing import Callable

import click
from dateutil.relativedelta import relativedelta

from murkelhausen import garmin

log = getLogger(__name__)


def _get_garmin_data(
    garmin_data_function: Callable, start_date: datetime, end_date: datetime | None
):
    garmin_client = garmin.get_garmin_client()

    start_date = start_date.date()
    if end_date is None:
        end_date = start_date
    else:
        end_date = end_date.date()

    log.info(
        f"Started {garmin_data_function.__name__} command for {start_date=} and {end_date=}."
    )
    for count_dates in range((end_date - start_date).days + 1):
        measure_date = start_date + relativedelta(days=count_dates)
        garmin_data_function(
            measure_date=measure_date, garmin_client=garmin_client, logger=log
        )


def garmin_arguments(function: Callable) -> Callable:
    function = click.argument(
        "start_date",
        type=click.DateTime(formats=["%Y-%m-%d"]),
        required=False,
        default=str(date.today()),
    )(function)
    function = click.argument(
        "end_date",
        type=click.DateTime(formats=["%Y-%m-%d"]),
        required=False,
    )(function)

    return function
