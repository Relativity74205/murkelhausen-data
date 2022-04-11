# murkelhausen stuff

## prefect

1. start prefect in docker `prefect server start`
2. start local prefect agent `supervisord`, setting supervisord up:
  - create `supervisord.conf` with `prefect agent local install >> supervisord.conf`
  - install `supervisor` in python virtualenv
  - 
3. create project `prefect create project 'murkelhausen'`
4. register flow `python src/murkelhausen/pipeline.py`