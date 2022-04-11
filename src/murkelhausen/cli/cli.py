from logging import getLogger

import click

from murkelhausen import __version__, cfg
from murkelhausen.config import cli_loader, City
from murkelhausen.util import logger, backend
from murkelhausen.util.backend import save_json
from murkelhausen.weather import owm, nmi

log = getLogger(__name__)


@click.group(invoke_without_command=True)
@click.option(
    "-c",
    "--cli_config",
    help="Config can be overridden with this option. The config parameters have to be "
    "passed according to the following syntax: "
    "'-c app__loglevel=ERROR'.",
)
@click.option(
    "-v", "--version", is_flag=True, help="Print murkelhausen' version number and exit."
)
@click.pass_context
def cli(ctx, version: bool, cli_config: str):
    """Command line interface for murkelhausen.

    Enter one of the subcommands to execute them, or run their respective --help
    to read about their usage.
    """
    if cli_config:
        cli_loader(cli_config)

    if version:
        click.echo(f"murkelhausen {__version__}")
        exit(0)
    elif ctx.invoked_subcommand is None:
        cli(["--help"])
    logger.setup_logging()


@cli.command()
@click.option("-p", "--port", default=5000, type=int, help="Set the port to serve on.")
@click.option("-h", "--host", default="localhost", help="Set the address to serve on.")
def serve(port, host):
    """Starts a server that serves the murkelhausen app code.

    Notes:
     * uvicorn will overwrite our logging config if we do not specify it as
       something falsey - do not delete that setting, since everything will
       still work, but we won't see any logs.
    """
    import uvicorn

    try:
        uvicorn.run(
            "murkelhausen.app:app",
            port=port,
            host=host,
            log_config=None,  # do not touch
            log_level=cfg.app.loglevel.lower(),
            reload=cfg.app.app_reload,
        )
    except:
        log.critical("Could not start server, aborting...", exc_info=True)
        raise


@cli.command("query-owm")
@click.argument("city_name")
def query_owm(city_name: str):
    """Queries the API of OpenWeatherMap for the given city name."""
    city: City = backend.get_city_object(city_name)
    owm_data: dict = owm.query_one_call_api(city, cfg.weather_owm)
    save_json(f"weather_owm_{city.name}", owm_data)
    return owm_data


@cli.command("query-nmi")
@click.argument("city_name")
def query_nmi(city_name: str):
    """Queries the API of the NMI for the given city name."""
    city = backend.get_city_object(city_name)
    nmi_data = nmi.query_locationforecast(city, cfg.weather_nmi)

    save_json(f"weather_nmi_{city.name}", nmi_data)
