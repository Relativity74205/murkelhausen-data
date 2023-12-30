from prefect import flow


if __name__ == "__main__":
    flow.from_source(
        source="git@github.com:Relativity74205/murkelhausen-data.git",
        entrypoint="src/murkelhausen/flow.py:main_flow",
    ).serve(
        name="murkelhausen_flow",
        cron="0 2 * * *",
        # version=__version__,  # TODO add version to murkelhausen-data
    )
