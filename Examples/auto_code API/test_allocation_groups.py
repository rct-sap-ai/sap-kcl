from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator
from auto_sap.classes.auto_code_classes import TimepointExtractor, VariableExtractor, AnalysisExtractor
from auto_sap.classes.chat_classes import OpenAIChat


dev_flag = True
run_design_vars = True
api = AutoCodeAPI(dev=dev_flag)

trials = api.get_(endpoint="trial")

trial_id = 17 if dev_flag else 20

trial_manager = TrialCreator(api, trial_id=trial_id)

allocation_groups = trial_manager.get_allocation_groups()
print("Current allocation groups retrieved successfully.")
print("Allocation groups are:")
for ag in allocation_groups:
    print(ag)

new_allocation_groups = [
    {"value": 0, "label": "Control"},
    {"value": 1, "label": "Intervention"}
]

update_response = trial_manager.update_allocation_groups(new_allocation_groups)
print("Update response for allocation groups:")
print(update_response)

print("Retrieving allocation groups after update...")
allocation_groups_after_update = trial_manager.get_allocation_groups()
print("Allocation groups after update:")        
for ag in allocation_groups_after_update:
    print(ag)
