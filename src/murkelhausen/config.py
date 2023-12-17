import importlib.resources
import tomllib
from logging import getLogger
from typing import Any, Callable, Literal, Type

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

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


class GarminConnect(BaseModel, validate_assignment=True):
    email: str
    password: str
    auth_token_path: str


class App(BaseModel):
    loglevel: loglevels
    data_path: str
    cities: list[City]
    confluent_broker_url: str
    confluent_schema_registry_url: str


class Settings(BaseSettings):
    app: App
    weather_owm: WeatherOWM
    weather_nmi: WeatherNMI
    garmin_connect: GarminConnect

    model_config = SettingsConfigDict(
        env_prefix="MURKELHAUSEN_", env_nested_delimiter="__"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            default_settings_fetcher(),
            file_secret_settings,
        )


def default_settings_fetcher() -> Callable[..., dict[str, Any]]:
    def inner(*_):
        with (importlib.resources.files("murkelhausen") / "default.toml").open(
            "rb"
        ) as f:
            return tomllib.load(f)

    return inner


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


config = Settings()
