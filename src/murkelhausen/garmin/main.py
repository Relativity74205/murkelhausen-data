import json
from datetime import date

import garth
from dateutil.relativedelta import relativedelta
from garminconnect import Garmin

from murkelhausen.config import config


def get_auth_token():
    email = config.garmin_connect.email
    password = config.garmin_connect.password

    garth.login(email, password)
    garth.save(config.garmin_connect.auth_token_path)


def get_garmin_client() -> Garmin:
    garmin = Garmin()
    try:
        garmin.login(config.garmin_connect.auth_token_path)
    except:
        get_auth_token()
        garmin.login(config.garmin_connect.auth_token_path)
    return garmin


today = date.today()

garmin = get_garmin_client()
# data = garmin.get_stats(today.isoformat())
# print(json.dumps(data, indent=4))
#
# data = garmin.get_steps_data(today.isoformat())
# print(json.dumps(data, indent=4))

data = garmin.get_heart_rates((today - relativedelta(days=14)).isoformat())
print(json.dumps(data, indent=4))
