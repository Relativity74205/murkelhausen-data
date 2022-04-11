from murkelhausen import __version__


def test_root(client):
    result = client.get("/")

    assert result.status_code == 200
    # f-strings were not used here, as the jinja templating would done havoc here
    assert result.text == '{"message":"' + __version__ + '"}'
