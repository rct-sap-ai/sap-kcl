"""
Example: AnalysisExtractor — generate and validate analyses from SAP content.

Demonstrates:
  1. Fetching SAP JSON and trial data from the API for a given trial.
  2. Using AnalysisExtractor.get_content() to pull the relevant SAP sections.
  3. Using AnalysisExtractor.extract() to generate an analysis list with AI.
  4. Using AnalysisExtractor.validate() to check the generated list for errors/warnings.
  5. (Optional) Saving the generated analyses back to the trial via update_analyses().

Prerequisites:
  - The trial must already have timepoints, outcomes, and analyses configured.
    See example_auto_code_create_trial.py for how to set those up.
  - OPENAI_API_KEY and AUTOCODE_API_TOKEN_PROD (or _DEV) must be set as env vars.
"""

from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator
from auto_sap.classes.auto_code_classes import AnalysisExtractor
from auto_sap.classes.chat_classes import OpenAIChat
import json

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

dev_flag = False
trial_id = 17 if dev_flag else 20

save_to_api = False  # Set True to write generated analyses back to the trial

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

api = AutoCodeAPI(dev=dev_flag)
trial_creator = TrialCreator(api, trial_id=trial_id)
chat_bot = OpenAIChat()
analysis_extractor = AnalysisExtractor(chat_bot=chat_bot)

# ---------------------------------------------------------------------------
# Step 1: Fetch data from the API
# ---------------------------------------------------------------------------

print("=" * 60)
print("STEP 1: Fetching trial data from API")
print("=" * 60)

sap = api.get_sap_json(trial_id=trial_id)
print(f"SAP fields present: {[k for k, v in sap.items() if v]}")

methods = api.get_(endpoint="method")
print(f"Available methods: {[{'id': m['id'], 'slug': m.get('slug')} for m in methods]}")

validator_args = trial_creator.get_analysis_validator_args()
outcomes = validator_args["outcomes"]
allowed_method_ids = validator_args["allowed_method_ids"]
timepoints = trial_creator.get_timepoints()

print(f"Outcomes ({len(outcomes)}):")
for o in outcomes:
    print(f"  {o['variable']} ({o.get('variable_type', '?')}) — timepoints: {o.get('timepoints', [])}")

print(f"Timepoints: {[tp['value'] for tp in timepoints]}")
print(f"Allowed method IDs: {allowed_method_ids}")

# ---------------------------------------------------------------------------
# Step 2: Pull the relevant SAP sections for analysis extraction
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("STEP 2: Extracting relevant SAP content")
print("=" * 60)

sap_text = analysis_extractor.get_content(sap)
print(f"SAP text length: {len(sap_text):,} chars")
print(f"Preview:\n{sap_text[:400]}...")

# ---------------------------------------------------------------------------
# Step 3: Generate analyses with AI
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("STEP 3: Generating analyses with AI")
print("=" * 60)

analysis_list, error_message = analysis_extractor.extract(
    sap_text=sap_text,
    outcomes=outcomes,
    timepoints=timepoints,
    methods=methods,
)

if error_message:
    print(f"\nAI error: {error_message}")
else:
    print(f"\nGenerated {len(analysis_list)} analyses:")
    for a in analysis_list:
        print(f"  outcome={a['outcome_variable']:<20} method={a['method']:<5} "
              f"timepoints={a['timepoints']}  covariates={a['covariates']}")

# ---------------------------------------------------------------------------
# Step 4: Validate the generated list
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("STEP 4: Validating generated analyses")
print("=" * 60)

errors, warnings = analysis_extractor.validate(
    analysis_list=analysis_list,
    outcomes=outcomes,
    allowed_method_ids=allowed_method_ids,
)

if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors:
        print(f"  [ERROR] {e}")
else:
    print("No errors.")

if warnings:
    print(f"\nWarnings ({len(warnings)}):")
    for w in warnings:
        print(f"  [WARN] {w}")
else:
    print("No warnings.")

# ---------------------------------------------------------------------------
# Step 5: (Optional) Save analyses back to the API
# ---------------------------------------------------------------------------

if save_to_api:
    print("\n" + "=" * 60)
    print("STEP 5: Saving analyses to API")
    print("=" * 60)

    if errors:
        print("Skipping save — validation errors must be resolved first.")
    else:
        response = trial_creator.update_analyses(analysis_list)
        print(f"Update response: {response}")
else:
    print("\nSave skipped (save_to_api=False). Set save_to_api=True to write back to the trial.")
