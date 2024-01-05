from datetime import timedelta

import prefect
from prefect import Flow
from prefect.schedules import IntervalSchedule
from prefect.tasks.secrets import PrefectSecret

from murkelhausen import config
from murkelhausen.home import deconz
from murkelhausen.util import backend
from murkelhausen.weather import nmi, owm

logger = prefect.context.get("logger")

schedule = IntervalSchedule(interval=timedelta(minutes=10))


def set_run_name(flow, old_state, new_state):
    if new_state.is_running():
        client = prefect.Client()
        name = f"{flow.name}-{prefect.context.date}"
        client.set_flow_run_name(prefect.context.flow_run_id, name)


with Flow("GetWeatherData", schedule=schedule, state_handlers=[set_run_name]) as flow:
    weather_owm__api_key = PrefectSecret("murkelhausendata__weather_owm__api_key")
    deconz__api_key = PrefectSecret("murkelhausendata__deconz__api_key")
    sensor_data = deconz.get_sensor_data(cfg.deconz, deconz__api_key)
    backend.save_json("deconz", sensor_data)

    city = backend.get_city_object("Mülheim")
    nmi_data = nmi.query_compact(city, cfg.weather_nmi)
    backend.save_json("nmi_compact", nmi_data)
    owm_data = owm.query_weather(city, cfg.weather_owm, weather_owm__api_key)
    backend.save_json("owm_weather", owm_data)


flow.register(project_name="murkelhausen")
# flow.run()
