import requests
from prefect import task

from murkelhausen.config import Deconz


@task
def get_sensor_data(deconz_settings: Deconz, api_key: str) -> dict:
    url = f"{deconz_settings.base_url}{api_key}{deconz_settings.sensor_route}"
    r = requests.get(url)

    if r.status_code == 200:
        return_dict: dict = r.json()
        return return_dict
    else:
        raise RuntimeError(
            f"Query to deconz api failed with non 200 status code"
            f"status_code: {r.status_code} "
            f"response_text: {r.text}."
        )
