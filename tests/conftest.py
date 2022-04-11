from base64 import b64encode

import pytest
from click.testing import CliRunner

from murkelhausen.config import default_toml_loader
from murkelhausen.util.logger import setup_logging

# reset any dev-configs that might have been picked up
default_toml_loader(None)
# and configure the logger, to get a more consistent behavior from it
setup_logging()


@pytest.fixture
def cli():
    from murkelhausen.cli import cli as aux_cli

    return lambda *args: CliRunner(mix_stderr=False).invoke(aux_cli.cli, args=args)


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from murkelhausen.app.app import app

    return TestClient(app)
