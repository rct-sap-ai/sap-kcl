from auto_sap.classes.auto_code_api_classes import auto_code_api, trial_creator

api = auto_code_api(dev = True)
trial_manager = trial_creator(api, acronym = "API_TRIAL_EXAMPLE", title = "API Trial Example")

timepotins = [
    {"value": 0, "label": "Baseline"},
    {"value": 1, "label": "8 Weeks"},
    {"value": 2, "label": "6 Months"},
]

timepoint_responses = trial_manager.update_timepoints(timepotins)
time_var_response = trial_manager.update_timevar()
allocation_group_response = trial_manager.update_allocation_groups([
    {"value": 0, "label": "Control"},
    {"value": 1, "label": "Intervention"},
])


    #outcomes list is a list of dicts with keys: label, variable, variable_type, timepoints

outcome_variable_list = [
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
trial_manager.update_outcomes(outcome_variable_list)

outcome_vars = trial_manager.get_outcome_variables()
print("OUTCOME VARIABLES:")
print(outcome_vars)

print("\n\n***FINAL TRIAL DATA***")
trial_data = trial_manager.get_trial_details()
print(trial_data)

possible_methods = trial_manager.get_methods()
print("POSSIBLE METHODS:")
print(possible_methods)

trial_manager.add_analyses(
    analysis_list = [
          {
            "outcome_label": "Depression Score",
            "timepoint": "Baseline",
            "method": 1,
            "table": "baseline"
        },  {
            "outcome_label": "Anxiety Score",
            "timepoint": "Baseline",
            "method": 1,
            "table": "baseline"
        },
        {
            "outcome_label": "Depression Score",
            "timepoint": "8 Weeks",
            "method": 3,
            "covariates": [], # currently not handled
            "table": "main_analysis"
        },
                {
            "outcome_label": "Anxiety Score",
            "timepoint": "6 Months",
            "method": 3,
            "covariates": [], # currently not handled
            "table": "main_analysis"
        }
    ]
)


# #runs with bug as am not correctly getting timepoints from trial
