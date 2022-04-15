"""Config parser module.

This module cascades through the different ways in which configuration
parameters for the clv application can be set. They follow the
standard priority of

 - default parameters (src/clv/resources/default.ini)
 - config file parameters (user.ini in top project path)
 - environment variable parameters
 - command line parameters

Parameters set through a method lower down the priority chain will
overwrite settings from higher up.

Command line parameters need to start with the section which they
will belong to, and have the key name follow after a double-
underscore, e.g. "app__loglevel", and
environment variables need to additionally start with CLV and
a single underscore before that, e.g. CLV_APP__LOGLEVEL.
"""
from logging import getLogger
from pathlib import Path
from typing import Literal, Any, MutableMapping
import importlib.resources

from pydantic import BaseSettings, BaseModel, validator
import toml

log = getLogger(__name__)

loglevels = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class City(BaseModel, validate_assignment=True):
    name: str
    gps_lat: float
    gps_lon: float


class WeatherOWM(BaseModel, validate_assignment=True):
    url_weather: str
    url_onecall: str
    units: Literal["metric", "imperial", "standard"]
    api_key: str


class WeatherNMI(BaseModel, validate_assignment=True):
    url_compact: str
    url_complete: str


class S3(BaseModel, validate_assignment=True):
    bucket: str
    aws_access_key_id: str
    aws_secret_access_key: str


class App(BaseModel):
    loglevel: loglevels
    data_path: str
    cities: list[City]

    @validator("cities")
    def check_cities(cls, cities):
        city_names = [city.name for city in cities]
        if len(set(city_names)) != len(city_names):
            raise ValueError("Found non unique city names.")

        return cities


class Settings(BaseSettings):
    app: App
    weather_owm: WeatherOWM
    weather_nmi: WeatherNMI
    s3: S3

    class Config:
        validate_assignment = True

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return env_settings, default_toml_loader


def default_toml_loader(settings: BaseSettings) -> MutableMapping[str, Any]:
    """Loads default variables from src/murkelhausen/default.toml to config"""
    try:
        with importlib.resources.path("murkelhausen", "default.toml") as default_config:
            with default_config.open() as f:
                return toml.load(f)
    except FileNotFoundError:
        log.error(
            f"Default config expected at src/murkelhausen/default.toml, but not found."
        )
        raise RuntimeError("Config not found, aborting!")


# def prefect_secrets_loader(*_) -> MutableMapping[str, Any]:
#     logger = prefect.context.get("logger")
#     d = defaultdict(dict)
#     prefect_secrets = prefect.context.get("secrets", {})
#     logger.info(prefect_secrets)
#     logger.info(list(prefect.context.keys()))
#     for secret_key, secret_value in prefect_secrets.items():
#         app_name, config_section, config_attribute = secret_key.split("__")
#         if app_name == "murkelhausen-data":
#             d[config_section][config_attribute] = secret_value
#     logger.info(d)
#
#     return d


def user_toml_loader(settings: BaseSettings):
    """Loads user-specified variables from user.toml to config.

    user.ini has to be placed in the top project path and follows the syntax
    of the default.toml (located in src/murkelhausen/resources/default.toml).
    user.toml must not be committed to git and is included in .gitignore.
    """
    user_config = Path(__file__).parent.parent.parent / "user.toml"
    try:
        with open(user_config) as f:
            return toml.load(f)
    except FileNotFoundError:
        log.info(f"User config expected at '{user_config}', but not found.")
        return {}


def cli_loader(config_string: str):
    """Loads user-specified variables provided with the CLI tool.

    The `config_string` can be provided with the -c/--cli_config option. The individual parameters
    need to start with the section which they will belong to, and have the key name follow
    after a double-underscore. Multiple parameters have to be separated by a comma (','), e.g.
    `app__loglevel=ERROR,app__fluentd_port=9881`.

    Raises:
        ValueError in case a format error is found in the provided string.
    """
    config_settings = config_string.split(",")

    for setting in config_settings:
        if setting.count("__") == 0:
            raise ValueError(
                f"Error in the cli_config option."
                f"Split character '__' between section and key is missing in {setting}."
            )
        elif setting.count("__") > 1:
            raise ValueError(
                f"Error in the cli_config option."
                f"More than one split character '__' found in {setting}. This is invalid."
            )
        if setting.count("=") == 0:
            raise ValueError(
                f"Error in the cli_config option."
                f"Assignment character '=' between key and value is missing in {setting}."
            )
        elif setting.count("=") > 1:
            raise ValueError(
                f"Error in the cli_config option."
                f"More than one Assignment character '=' found in {setting}. This is invalid."
            )

        section = setting.split("=")[0].split("__")[0]
        key = setting.split("=")[0].split("__")[1]
        env_val = setting.split("=")[1]
        setattr(getattr(config, section), key, env_val)


config = Settings()
