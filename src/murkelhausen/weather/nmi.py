"""
https://api.met.no/weatherapi/
https://www.yr.no/en/details/table/2-6553027/Germany/North%20Rhine-Westphalia/D%C3%BCsseldorf%20District/M%C3%BClheim
"""
from logging import getLogger

import requests
from prefect import task

from murkelhausen.config import WeatherNMI, City

log = getLogger(__name__)


@task
def query_compact(city: City, nmi_settings: WeatherNMI) -> dict:
    return _query_locationforecast(nmi_settings.url_compact, city)


@task
def query_complete(city: City, nmi_settings: WeatherNMI) -> dict:
    return _query_locationforecast(nmi_settings.url_complete, city)


def _query_locationforecast(url: str, city: City) -> dict:
    query_params: dict = {
        "lat": city.gps_lat,
        "lon": city.gps_lon,
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64)"}
    r = requests.get(url, params=query_params, headers=headers)
    log.debug(f"Following URL is used for querying NMI API: {r.url}.")

    if r.status_code == 200:
        return_dict: dict = r.json()
        return return_dict
    else:
        raise RuntimeError(
            f"Query to norwegian meteorological institute one call api returned non 200 status code for city {city.name}: "
            f"status_code: {r.status_code} "
            f"response_text: {r.text}."
        )
