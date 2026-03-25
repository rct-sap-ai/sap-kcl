from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator
from auto_sap.classes.chat_classes import OpenAIChat
from auto_sap.classes.sap_content_updater import SAPContentUpdater

# Set up connection to auto_code API.
# Only set dev=True if you have access to a local development server.
# The API class looks for an environment variable named AUTOCODE_API_TOKEN_DEV or AUTOCODE_API_TOKEN_PROD.
dev_flag = False
trial_id = 20 # use trial 17 for dev, trial 20 for prod
api = AutoCodeAPI(dev = dev_flag)

trial = api.get_(f"trial/{trial_id}/")


# Assumes the trial has already been created with timepoints, outcomes, and analyses.
# See example_auto_code_create_trial.py for how to set these up.
trial_manager = TrialCreator(api, trial_id = trial_id)

# --- LLM setup ---
# OpenAIChat uses the OPENAI_API_KEY environment variable automatically.
chat_bot = OpenAIChat()

# --- Instantiate the SAPContentUpdater ---
updater = SAPContentUpdater(trial_manager=trial_manager, chat_bot=chat_bot)

# Fetch the existing SAP JSON — field-specific methods update it in place.
sap = api.get_sap_json(trial_id=trial_manager.trial_id)

def _print_field(field: str, old: str, new: str):
    print(f"\n{'='*60}")
    print(f"[{field}]")
    print(f"  OLD: {old or '(empty)'}")
    print(f"  NEW: {new}")

# --- Update each content field individually ---
field = "follow_up_timepoints"
old = sap.get(field, "")
updater.update_follow_up_timepoints(sap)
_print_field(field, old, sap[field])

field = "primary_outcome_measures"
old = sap.get(field, "")
updater.update_primary_outcome_measures(sap)
_print_field(field, old, sap[field])

field = "secondary_outcome_measures"
old = sap.get(field, "")
updater.update_secondary_outcome_measures(sap)
_print_field(field, old, sap[field])

field = "analysis_methods"
old = sap.get(field, "")
updater.update_analysis_methods(sap)
_print_field(field, old, sap[field])

# --- Save the updated SAP back to the API ---

#trial_manager.add_sap_json(sap) 
