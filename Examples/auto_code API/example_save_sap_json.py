from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator
import json
from datetime import datetime

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#set up connection to auto_code API. Only set dev = True if you have access to a local development server.
# The API class looks for an environment variable named AUTOCODE_API_TOKEN_DEV or AUTOCODE_API_TOKEN_PROD. This can be passed using the 'token' argument if preferred.

dev_flag = False
api = AutoCodeAPI(dev = dev_flag)

trials_list = api.get_("trial/")
print("Existing trials in the API:")
print(json.dumps(trials_list, indent=4))

# Inputs:
acronym = "API_TRIAL_EXAMPLE"
title = "API Trial Example"

trial_creator = TrialCreator(api, acronym, title)

sap_json = {
    "acronym": acronym,
    "title": title,
    "another field": "example value",
    "date_time_created": now
}

trial_creator.add_sap_json(sap_json)

retrieved_sap_json = trial_creator.get_sap_json()
print("Retrieved SAP JSON from API:")
print(json.dumps(retrieved_sap_json, indent=4))