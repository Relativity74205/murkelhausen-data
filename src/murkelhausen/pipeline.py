from datetime import timedelta
from logging import getLogger

from prefect import Flow
from prefect.schedules import IntervalSchedule

from murkelhausen.weather import nmi, owm
from murkelhausen.util import backend
from murkelhausen import cfg

log = getLogger(__name__)

schedule = IntervalSchedule(interval=timedelta(minutes=10))

with Flow("GetWeatherData", schedule=schedule) as flow:
    city = backend.get_city_object("Mülheim")
    nmi_data = nmi.query_compact(city, cfg.weather_nmi)
    backend.save_json("nmi_compact", nmi_data)
    # my_secret = PrefectSecret("WEATHEROWM_APIKEY")
    # cfg.weather_owm.api_key = my_secret.run()
    owm_data = owm.query_weather(city, cfg.weather_owm)
    backend.save_json("owm_weather", owm_data)

# flow.register(project_name="murkelhausen")
flow.run()
