from datetime import date
from logging import getLogger

import click

from murkelhausen import __version__
from murkelhausen.garmin.main import get_garmin_client, get_heartrate_data
from murkelhausen.util import logger
from murkelhausen import persistance_layer

log = getLogger(__name__)

garmin_client = get_garmin_client()


@click.group(invoke_without_command=True)
@click.option(
    "-v", "--version", is_flag=True, help="Print murkelhausen' version number and exit."
)
@click.pass_context
def cli(ctx, version: bool):
    """Command line interface for murkelhausen.

    Enter one of the subcommands to execute them, or run their respective --help
    to read about their usage.
    """

    if version:
        click.echo(f"murkelhausen {__version__}")
        exit(0)
    elif ctx.invoked_subcommand is None:
        cli(["--help"])
    logger.setup_logging()


@cli.command("query-owm")
@click.argument("city_name")
def query_owm(city_name: str):
    """Queries the API of OpenWeatherMap for the given city name."""
    # city: City = backend.get_city_object(city_name)
    # owm_data: dict = owm.query_one_call_api(city, config.weather_owm)


@cli.command("query-nmi")
@click.argument("city_name")
def query_nmi(city_name: str):
    """Queries the API of the NMI for the given city name."""
    # city = backend.get_city_object(city_name)
    # nmi_data = nmi.query_locationforecast(city, config.weather_nmi)


@cli.group
def db():
    ...


@db.command("create")
def create_db():
    persistance_layer.create_tables()


@cli.group
def garmin():
    ...


@garmin.command("get-heart-rates")
def get_heart_rates_command():
    get_heartrate_data(start_date=date.today(), logger=log)
