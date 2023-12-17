import garth

from murkelhausen.config import config


def get_auth_token():
    email = config.garmin_connect.username
    password = config.garmin_connect.password

    garth.login(email, password)
    garth.save(config.garmin_connect.auth_token_path)
