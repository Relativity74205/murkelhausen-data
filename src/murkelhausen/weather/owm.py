"""
https://openweathermap.org/api/one-call-api
"""
import requests
from prefect import task

from murkelhausen.config import WeatherOWM, City


@task
def query_one_call_api(city: City, owm_settings: WeatherOWM) -> dict:
    return _query_owm(
        owm_settings.url_onecall, city, owm_settings.api_key, owm_settings.units
    )


@task
def query_weather(city: City, owm_settings: WeatherOWM) -> dict:
    return _query_owm(
        owm_settings.url_weather, city, owm_settings.api_key, owm_settings.units
    )


def _query_owm(url: str, city: City, api_key: str, units: str) -> dict:
    query_params: dict = {
        "lat": city.gps_lat,
        "lon": city.gps_lon,
        "appid": api_key,
        "units": units,
    }
    r = requests.get(url, params=query_params)

    if r.status_code == 200:
        return_dict: dict = r.json()
        return return_dict
    else:
        raise RuntimeError(
            f"Query to openweatherapi one call api returned non 200 status code for city {city.name}: "
            f"status_code: {r.status_code}"
            f"response_text: {r.text}"
        )


def get_weather_map(layer: str, owm_settings: WeatherOWM):
    """
    https://openweathermap.org/api/weathermaps
    https://github.com/google/maps-for-work-samples/blob/master/samples/maps/OpenWeatherMapLayer/OpenWeatherMapLayer.pdf
    """
    pass


def query_air_pollution():
    """
    https://openweathermap.org/api/air-pollution
    """
    pass
