"""
prefect deployment build ./backup.py:beowulf -n backup_beowulf -q beowulf --cron "0 2 * * *"
"""
from datetime import datetime, date
from pathlib import Path
from dateutil import relativedelta

import docker
from prefect import flow, task, get_run_logger
from prefect_shell import ShellOperation
from prefect.task_runners import ConcurrentTaskRunner

POSTGRES_BACKUP_PATH = "/home/arkadius/backup/postgres"
POSTGRES_PATH = "/home/arkadius/postgres"
POSTGRES_DATABASES = ("murkelhausen_datastore", "superset", "murkelhausen_app")
POSTGRES_BACKUP_LAST_COUNT = 5


def get_months_between_dates(date1, date2) -> int:
    r = relativedelta.relativedelta(date1, date2)
    months = (r.years * 12) + r.months
    return months


@task(task_run_name="cleanup_backup_files_{database_name}")
def cleanup_backup_files(database_name: str):
    logger = get_run_logger()
    files = [
        ele
        for ele in Path(POSTGRES_BACKUP_PATH).glob(f"*{database_name}.dump")
        if ele.is_file()
    ]
    files_with_dates = [
        (
            file,
            datetime.strptime(file.stem.split("__")[0], "%Y-%m-%dT%H_%M_%S"),
        )
        for file in files
    ]

    files_with_dates.sort(key=lambda x: x[1], reverse=True)

    files_to_delete = [
        file
        for i, (file, file_date) in enumerate(files_with_dates)
        if not (
            # keep the last x files
            i < POSTGRES_BACKUP_LAST_COUNT
            # all files from beginning of the month shall be kept
            or file_date.day == 1
            # all files from sunday shall be kept, however only for the last x months
            or file_date.weekday() == 6
            and get_months_between_dates(datetime.today(), file_date) <= 3
        )
    ]
    logger.info(f"{files_to_delete=}")
    for file in files_to_delete:
        file.unlink()

        logger.info(f"Deleted {file}.")


@task
def backup_kafka():
    """
    https://docs.confluent.io/platform/current/kafka-rest/api.html

    broker:
    curl http://localhost:8082/v3/clusters | jq
    curl http://localhost:8082/v3/clusters/3x4LP0wLSdm1jZGXUxfYZw/brokers/1/configs | jq

    schema registry:
    curl http://localhost:8081/subjects | jq
    curl http://localhost:8081/subjects/power_data_v2-value/versions/1 | jq

    """
    pass


@task
def backup_mosquitto():
    pass


@task
def backup_zigbee2mqtt():
    pass


@task
def monitor_docker_processes():
    DOCKER_PROCESSES_SHOULD = (
        "murkelhausen",
        "postgres",
        "portainer",
        "zigbee2mqtt",
        "mqtt",
        "superset_worker",
        "superset_worker_beat",
        "superset_app",
        "superset_cache",
        "control-center",
        "connect",
        "rest-proxy",
        "schema-registry",
        "broker",
        "zookeeper",
    )

    logger = get_run_logger()
    client = docker.from_env()
    containers = client.containers.list()

    all_healthy = True
    for container in containers:
        logger.info(f"Running processes: {container.name=}: {container.status=}")
        if container.name == "superset-init":
            continue

        # container.attrs["State"]["Health"]["Status"] != "healthy"
        if "running" in container.status:
            continue
        else:
            all_healthy = False
            logger.error(
                f"container{container.name} has bad state: {container.status}."
            )

    missing_processes = []
    for process in DOCKER_PROCESSES_SHOULD:
        if not any(process in container.name for container in containers):
            logger.error(f"Missing process: {process}")
            missing_processes.append(process)
        else:
            logger.info(f"Found process: {process}")

    if not all_healthy:
        raise RuntimeError(f"At least one of the processes is not 'running'.")

    if missing_processes:
        raise RuntimeError(f"Missing processes: {missing_processes}")


@task(task_run_name="backup_postgres_globals_{backup_datetime}")
def backup_postgres_globals(backup_datetime: datetime):
    cmd = f"docker-compose -f {POSTGRES_PATH}/docker-compose.yml exec -T postgres pg_dumpall --globals-only -U postgres > {POSTGRES_BACKUP_PATH}/{backup_datetime}__globals.sql"
    ShellOperation(
        name="backup_postgres_globals",
        commands=[cmd],
        return_all=False,
    )


@task(task_run_name="backup_postgres_{database_name}_{backup_datetime}")
def backup_postgres(database_name: str, backup_datetime: datetime):
    cmd = f"docker-compose -f {POSTGRES_PATH}/docker-compose.yml exec -T postgres pg_dump -F c -U postgres {database_name} > {POSTGRES_BACKUP_PATH}/{backup_datetime}__{database_name}.sql"
    ShellOperation(
        name=f"backup_postgres_{database_name}",
        commands=[cmd],
        return_all=False,
    )


@flow(
    name="beowulf-backup-flow",
    flow_run_name=f"beowulf_backup_{date.today().isoformat()}",
    task_runner=ConcurrentTaskRunner(),
)
def beowulf_backup_flow():
    backup_datetime = datetime.now().strftime("%Y-%m-%dT%H_%M_%S")
    logger = get_run_logger()
    backup_postgres_globals(backup_datetime)
    logger.info("Performed backup of postgres globals.")
    for database_name in POSTGRES_DATABASES:
        backup_postgres(database_name=database_name, backup_datetime=backup_datetime)
        logger.info(f"Performed backup of postgres database {database_name}.")
    cleanup_backup_files("globals")
    logger.info("Cleaned old globals database backups.")
    for database_name in POSTGRES_DATABASES:
        cleanup_backup_files(database_name)
        logger.info(f"Cleaned old {database_name} database backups.")
    logger.info("Cleaned old database backups.")
    # backup_kafka.submit()
    # backup_mosquitto.submit()
    # backup_zigbee2mqtt.submit()
    # monitor_docker_processes.submit()
    # TODO backup PORTAINER
    # TODO monitor backups for pi-holes, unifi
    # TODO update pi-hole lists


if __name__ == "__main__":
    beowulf_backup_flow()
