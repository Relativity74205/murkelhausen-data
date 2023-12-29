from prefect import flow, task

from murkelhausen.garmin_flow import garmin_flow
from murkelhausen.util.logger import setup_logging

setup_logging()


@flow
def main_flow():
    garmin_flow()


if __name__ == "__main__":
    # replace with flow.from_source https://docs.prefect.io/latest/getting-started/quickstart/#step-4-make-your-code-schedulable
    # main_flow.deploy(
    #     name="murkelhausen_flow",
    #     work_pool_name="my-managed-pool",  # TODO
    #     cron="0 1 * * *",
    # )
    main_flow.serve(
        name="murkelhausen_flow",
        cron="0 2 * * *",
        # version=__version__,  # TODO add version to murkelhausen-data
    )
