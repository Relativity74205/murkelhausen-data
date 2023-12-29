# murkelhausen stuff

## prefect local

1. start prefect in docker `prefect server start`
2. create project `prefect create project 'murkelhausen'`

## prefect raspberry

1. install project python virtual environment
2. start local prefect agent `supervisord`, setting supervisord up:
  - create `supervisord.conf` with `prefect agent local install >> supervisord.conf`
  - install `supervisor` in python virtualenv
  - 
3. (if new project) create project `prefect create project 'murkelhausen'`
4. register flow `python src/murkelhausen/pipeline.py` (from project python environment)


### Dev local

```bash
prefect run -p src/murkelhausen/pipeline.py
```

### TODO
- change path in supervisord.conf
- setup systemd for supervisord
    - http://supervisord.org/running.html#running-supervisord-automatically-on-startup
    - https://serverfault.com/questions/958625/error-when-adding-supervisord-to-run-via-systemd)


## Garmin Auth (Garth)

```python
import garth
from getpass import getpass

email = input("Enter email address: ")
password = getpass("Enter password: ")
# If there's MFA, you'll be prompted during the login
garth.login(email, password)

garth.save("~/.garth")
```


## Postgres DB

```sql
CREATE SCHEMA data;
CREATE USER murkelhausen_data WITH PASSWORD '';
ALTER SCHEMA data OWNER TO murkelhausen_data;
```


## Prefect

```sql
prefect work-pool create beowulf-local --type process
prefect worker start --pool beowulf-local
```
