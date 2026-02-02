from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator
import json
import zipfile
import io
import os

#set up connection to auto_code API. Only set dev = True if you have access to a local development server.
# The API class looks for an environment variable named AUTOCODE_API_TOKEN_DEV or AUTOCODE_API_TOKEN_PROD. This can be passed using the 'token' argument if preferred.

dev_flag = False
api = AutoCodeAPI(dev = dev_flag)

# Inputs:
aconym = "API_TRIAL_EXAMPLE"
title = "API Trial Example"


design_variables = [
    {'design_parameter': "allocation", 'variable':"treatment_group", 'label': "Treatment Group"},
    #{'design_parameter': "centre", 'variable':"site", 'label': "Site"}, uncomment for multicentre example
]

allocation_groups = [
    {"value": 0, "label": "Control"},
    {"value": 1, "label": "Intervention"},
]

time_var = {'variable': 'timepoint', 'label': 'Timepoint', 'variable_type': 'Categorical'}
timepoint_value_labels = [
    {"value": 0, "label": "Baseline"},
    {"value": 1, "label": "8 Weeks"},
    {"value": 2, "label": "6 Months"},
]
outcomes = [
    {
        "label": "Depression Score",
        "variable_type": "Continuous",
        "variable": "depression",
        "timepoints": ["Baseline", "8 Weeks", "6 Months"]
    },
    {
        "label": "Anxiety Score",
        "variable_type": "Continuous",
        "variable": "anxiety",
        "timepoints": ["Baseline", "6 Months"]
    },
]

# The possible methods are pre-defined in the auto_code API. To get a list of posible methods and their IDs use the get_methods() function.
possible_methods = api.get_methods()
print("POSSIBLE METHODS:")
print(json.dumps(possible_methods, indent=4))

descriptive_method_id = 1
if dev_flag:
    descriptive_method_id = 1  # In DEV, the IDs may differ
linear_model_method_id = 2
if dev_flag:
    linear_model_method_id = 3  # In DEV, the IDs may differ

analysis_list = [
          {
            "outcome_variable": "depression",
            "timepoint": 0,
            "method": descriptive_method_id,
            "table": "baseline"
        },  {
            "outcome_variable": "anxiety",
            "timepoint": 0,
            "method": descriptive_method_id,
            "table": "baseline"
        },
        {
            "outcome_variable": "depression",
            "timepoint": 1,
            "method": linear_model_method_id,
            "table": "main_analysis"
        },
                {
            "outcome_variable": "anxiety",
            "timepoint": 2,
            "method": linear_model_method_id,
            "table": "main_analysis"
        }
    ]

# Creating the trial 
trial_manager = TrialCreator(api, acronym = aconym, title = title)

# Sending data
time_var_response = trial_manager.update_timevar(variable_data = time_var, value_labels = timepoint_value_labels)
allocation_groups_response = trial_manager.update_allocation_groups(allocation_group_list = allocation_groups)
trial_manager.update_design_variables(design_variables)
trial_manager.update_outcomes(outcomes)
trial_manager.add_analyses(analysis_list)
report_response = trial_manager.create_main_analysis_report()
print(report_response)
code_response = trial_manager.get_code_for_main_analysis()

extract_path = 'Generated Code/Eg1/'
os.makedirs(extract_path, exist_ok=True)

with zipfile.ZipFile(io.BytesIO(code_response)) as zip_ref:
    zip_ref.extractall(extract_path)

print(f"Files extracted to: {extract_path}")




