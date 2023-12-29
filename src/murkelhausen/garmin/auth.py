import garth

from murkelhausen.config import config


def get_auth_token():
    email = config.garmin_connect.email
    password = config.garmin_connect.password.get_secret_value()

    garth.login(email, password)
    garth.save(config.garmin_connect.auth_token_path)
