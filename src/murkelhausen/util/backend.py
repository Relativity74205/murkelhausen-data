from murkelhausen.config import City, config


def get_city_object(city_name: str) -> City:
    """Retrieves the City object from the config for the given city name.

    Raises ValueError in case the city was not found in the config.
    """
    cities = [city for city in config.app.cities if city.name == city_name]
    if len(cities) == 1:
        return cities[0]
    else:
        raise ValueError(f"{city_name=} not found in config.")


# @task(task_run_name="save_{base_name}_data")
# def save_json(base_name: str, data: dict):
#     now = datetime.now().isoformat(timespec="seconds")
#     base_path = Path(__file__).parent.parent.parent.parent / cfg.app.data_path
#
#     full_filename = base_path / f"{base_name}_{now}.json"
#     print(full_filename)
#     with open(full_filename, "w") as f:
#         json.dump(data, f, indent=4, ensure_ascii=False)
