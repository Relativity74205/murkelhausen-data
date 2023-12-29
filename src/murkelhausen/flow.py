from datetime import date

from dateutil.relativedelta import relativedelta
from prefect import flow

from murkelhausen.garmin_flow import garmin_flow
from murkelhausen.util.logger import setup_logging

setup_logging()


@flow
def main_flow(measure_date: date = date.today() - relativedelta(days=1)):
    """
    Default measure date is always yesterday (which timezone?), except when a measure_date is specified.
    """
    garmin_flow(measure_date=measure_date)


if __name__ == "__main__":
    # replace with flow.from_source https://docs.prefect.io/latest/getting-started/quickstart/#step-4-make-your-code-schedulable
    main_flow.serve(
        name="murkelhausen_flow",
        cron="0 2 * * *",  # add to config; check for timezone
        # version=__version__,  # TODO add version to murkelhausen-data
    )
