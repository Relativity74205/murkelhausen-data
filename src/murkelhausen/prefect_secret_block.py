from pydantic.v1 import SecretStr
from prefect.blocks.core import Block

from murkelhausen.config import config


class MurkelHausenSecrets(Block):
    garmin_password: SecretStr
    database_password: SecretStr


def create_prefect_secrets_block():
    secrets = MurkelHausenSecrets(
        garmin_password=config.garmin_connect.password.get_secret_value(),
        database_password=config.database.password.get_secret_value(),
    )
    secrets.save(config.app.prefect_secret_block_name, overwrite=True)
