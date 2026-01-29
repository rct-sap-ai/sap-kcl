# I want a file that loads sap_json from a txt file in SAPs and then uses methods from auto_code_api_classes and auto_code_classes
from pathlib import Path
import dotenv
dotenv.load_dotenv()
import os
import json

from auto_sap.classes.auto_code_classes import TimepointExtractor
from auto_sap.classes.chat_classes import OpenAIChat
from auto_sap.classes.auto_code_api_classes import TrialCreator, AutoCodeAPI


# Setting up chat bot and api connection
chat_bot = OpenAIChat(model_name = "gpt-5-nano")
auto_code_api = AutoCodeAPI(dev = False)

# Loading SAP content
saps_path = Path(os.getenv("SAPAI_SHARED_PATH")) / "SAPs"
sap_name = "ACTISSIST_sap_v0.1"

with open(f"{saps_path}/{sap_name}.json", 'r') as file:
    sap_json = json.load(file) 

print("\n \n sap_content keys are: \n", sap_json.keys())


# Step 1: Create trial_creator instance via auto_code_api using title and aconym
trial_title = sap_json.get("title", "")
trial_acronym = sap_json.get("trial_acronym", "")
if trial_title == "" or trial_acronym == "":
    raise ValueError("Trial title or acronym missing in SAP JSON")
else:
    print(f"\n \n Creating trial object for {trial_acronym}: {trial_title} \n")

trial_creator = TrialCreator(
    auto_code_api, 
    acronym = trial_acronym, 
    title = trial_title
)


#Step 2: Timepoints

print("\n \n Timepoint content extraction")
timepoint_content = sap_json.get("follow_up_timepoints", "") + "\n" + sap_json.get("primary_outcome_measures", "") + "\n" + sap_json.get("secondary_outcome_measures", "")

print(timepoint_content)

timepoint_extractor = TimepointExtractor(chat_bot = chat_bot)
timepoints_return = timepoint_extractor.extract_timepoints(timepoint_content)
timepoints_list = timepoints_return[0]
print("\n Extracted timepoints are: \n", timepoints_list)

def is_valid_timepoints(lst):
    # Check if it's a list
    if not isinstance(lst, list):
        return False
    
    # Check each item in the list
    for item in lst:
        # Must be a dictionary
        if not isinstance(item, dict):
            return False
        
        # Must have exactly the keys 'value' and 'label'
        if set(item.keys()) != {'value', 'label'}:
            return False
        
        # 'value' must be an integer
        if not isinstance(item['value'], int):
            return False
        
        # 'label' must be a string
        if not isinstance(item['label'], str):
            return False
    
    return True

print("\n Is the extracted timepoints list valid? \n")
print(is_valid_timepoints(timepoints_list))