# murkelhausen stuff

## prefect local

1. start prefect in docker `prefect server start`
2. create project `prefect create project 'murkelhausen'`


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


## Beowulf Setup


### Setup systemd

```bash
sudo ln -s /home/arkadius/murkelhausen-data/murkelhausen-data.service /etc/systemd/system/murkelhausen-data.service
sudo systemctl daemon-reload
sudo systemctl enable murkelhausen-data
sudo systemctl start murkelhausen-data
```

### Changes to systemd files (also flow.py?)

```bash
sudo systemctl daemon-reload
sudo systemctl restart murkelhausen-data
```

### Systemd Status

```bash
sudo systemctl status murkelhausen-data
```

#### systemd Logs
```bash
journalctl -u murkelhausen-data.service --follow
```