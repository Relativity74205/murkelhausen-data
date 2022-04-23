# murkelhausen stuff

## prefect

1. start prefect in docker `prefect server start`
2. start local prefect agent `supervisord`, setting supervisord up:
  - create `supervisord.conf` with `prefect agent local install >> supervisord.conf`
  - install `supervisor` in python virtualenv
  - 
3. create project `prefect create project 'murkelhausen'`
4. register flow `python src/murkelhausen/pipeline.py`


TODO:
- change path in supervisord.conf
- setup systemd for supervisord
    - http://supervisord.org/running.html#running-supervisord-automatically-on-startup
    - https://serverfault.com/questions/958625/error-when-adding-supervisord-to-run-via-systemd)

## ConBee II

http://192.168.1.28/pwa/

###

### install

- https://phoscon.de/en/conbee2/install
- https://github.com/dresden-elektronik/deconz-rest-plugin#headless-support-for-linux

### Rest API

- https://dresden-elektronik.github.io/deconz-rest-doc/getting_started/#acquire-an-api-key
- 192.168.1.28/api
- API key: see onepassword


### Phoscon App

- https://phoscon.de/en/app/doc

### Forum Posts

- https://forum.fhem.de/index.php?topic=117470.0

