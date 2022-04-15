from datetime import timedelta

from prefect import Flow, task
import prefect
from prefect.schedules import IntervalSchedule
from prefect.tasks.secrets import PrefectSecret

from murkelhausen.weather import nmi, owm
from murkelhausen.util import backend
from murkelhausen import cfg

logger = prefect.context.get("logger")

schedule = IntervalSchedule(interval=timedelta(minutes=10))


@task
def test(secret):
    logger.info(f"test_task {secret=}")


with Flow("GetWeatherData", schedule=schedule) as flow:
    city = backend.get_city_object("Mülheim")
    nmi_data = nmi.query_compact(city, cfg.weather_nmi)
    backend.save_json("nmi_compact", nmi_data)
    foo_secret = PrefectSecret("foo")
    test(foo_secret)
    real_secret = PrefectSecret("murkelhausen-data__weather_owm__api_key")
    test(real_secret)
    real_secret = PrefectSecret("weather_owm__api_key")
    test(real_secret)
    real_secret = PrefectSecret("weather_owm_api_key")
    test(real_secret)
    # cfg.weather_owm.api_key = my_secret.run()
    owm_data = owm.query_weather(city, cfg.weather_owm)
    backend.save_json("owm_weather", owm_data)





flow.register(project_name="murkelhausen")
# flow.run()
