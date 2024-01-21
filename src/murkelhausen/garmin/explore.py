import json

from murkelhausen.garmin.main import get_garmin_client

garmin_client = get_garmin_client()


d = garmin_client.get_sleep_data("2024-01-20")
print(json.dumps(d, indent=4))
with open("sleep.json", "w") as f:
    json.dump(d, f, indent=4)


# print(json.dumps(garmin_client.get_activity_types(), indent=4))
# get_sleep_data
# get_spo2_data
# get_respiration_data
# get_hrv_data
# get_user_summary
# get_stats
# get_stats_and_body

# get_activities_fordate
