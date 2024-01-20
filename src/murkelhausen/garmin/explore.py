import json

from murkelhausen.garmin.main import get_garmin_client

garmin_client = get_garmin_client()


# sleep heart Rate + ... + ...
d = garmin_client.get_heart_rates("2024-01-12")
print(json.dumps(d, indent=4))
with open("heat_rates.json", "w") as f:
    json.dump(d, f, indent=4)

# get_spo2_data
# get_respiration_data


# get_user_summary
# get_stats
# get_stats_and_body

# print(json.dumps(garmin_client.get_rhr_day("2024-01-12"), indent=4))
# {
#     "userProfileId": 117879743,
#     "statisticsStartDate": "2024-01-12",
#     "statisticsEndDate": "2024-01-12",
#     "allMetrics": {
#         "metricsMap": {
#             "WELLNESS_RESTING_HEART_RATE": [
#                 {
#                     "value": 49.0,
#                     "calendarDate": "2024-01-12"
#                 }
#             ]
#         }
#     },
#     "groupedMetrics": null
# }


# get_hrv_data

# print(json.dumps(garmin_client.get_training_readiness("2024-01-12"), indent=4))

# print(json.dumps(garmin_client.get_device_settings(), indent=4))


# get_activities_fordate

#
