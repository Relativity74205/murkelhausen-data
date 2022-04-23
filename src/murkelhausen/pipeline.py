from datetime import timedelta

from prefect import Flow
import prefect
from prefect.schedules import IntervalSchedule
from prefect.tasks.secrets import PrefectSecret

from murkelhausen.home import deconz
from murkelhausen.weather import nmi, owm
from murkelhausen.util import backend
from murkelhausen import cfg

logger = prefect.context.get("logger")

schedule = IntervalSchedule(interval=timedelta(minutes=10))


with Flow("GetWeatherData", schedule=schedule) as flow:
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
