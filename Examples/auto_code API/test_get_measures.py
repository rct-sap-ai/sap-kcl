from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator
from auto_sap.classes.auto_code_classes import TimepointExtractor, VariableExtractor, AnalysisExtractor
from auto_sap.classes.chat_classes import OpenAIChat
import json


#set up connection to auto_code API. Only set dev = True if you have access to a local development server.
# The API class looks for an environment variable named AUTOCODE_API_TOKEN_DEV or AUTOCODE_API_TOKEN_PROD. This can be passed using the 'token' argument if preferred.
try_update = False

dev_flag = False
trial_id = 17 if dev_flag else 20
api = AutoCodeAPI(dev = dev_flag)

trial = api.get_(f"trial/{trial_id}/")

print(trial)

trial_creator = TrialCreator(api, trial_id = trial_id)
measures = trial_creator.get_outcome_variables()
print(f"Measures for trial {trial_id}:", json.dumps(measures, indent=1))

print("Extracting measure fields...")
extracted = trial_creator.extract_measure_fields(measures = measures)
for row in extracted:
    print(row)

timepoints = trial_creator.get_timepoints()

chat_bot = OpenAIChat(model_name="gpt-5-nano")
variable_extractor = VariableExtractor(chat_bot=chat_bot)
errors, warnings = variable_extractor.validate(extracted, timepoints_list = timepoints)

print("Errors:", errors)
print("Warnings:", warnings)    

if try_update:
    print("Attempting to update measures with extracted data...")
    update_response = trial_creator.update_outcomes(extracted)
    print("Update response:", update_response)