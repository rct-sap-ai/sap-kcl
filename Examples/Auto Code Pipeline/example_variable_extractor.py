"""
Example: VariableExtractor — extract primary and secondary outcome variables from SAP content.

Demonstrates:
  1. Fetching SAP JSON from the API for a given trial.
  2. Using VariableExtractor.get_content() to pull the relevant SAP section
     for primary outcomes (primary_outcome=True) and secondary outcomes (False).
  3. Using VariableExtractor.extract() with primary_outcome=True/False to stamp
     the flag onto every extracted variable.
  4. Validating both sets of extracted variables.
  5. Combining primary and secondary variables into a single list ready for
     update_outcomes().

Prerequisites:
  - OPENAI_API_KEY and AUTOCODE_API_TOKEN_PROD (or _DEV) must be set as env vars.
"""

import dotenv
dotenv.load_dotenv()

from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator
from auto_sap.classes.auto_code_classes import VariableExtractor
from auto_sap.classes.chat_classes import OpenAIChat
import json

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

dev_flag = False
trial_id = 17 if dev_flag else 20

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

api = AutoCodeAPI(dev=dev_flag)
trial_creator = TrialCreator(api, trial_id=trial_id)
chat_bot = OpenAIChat()
variable_extractor = VariableExtractor(chat_bot=chat_bot)

# ---------------------------------------------------------------------------
# Step 1: Fetch SAP JSON and timepoints from the API
# ---------------------------------------------------------------------------

print("=" * 60)
print("STEP 1: Fetching SAP JSON and timepoints from API")
print("=" * 60)

sap = api.get_sap_json(trial_id=trial_id)
timepoints = trial_creator.get_timepoints()

print(f"Timepoints: {[tp['value'] for tp in timepoints]}")

# ---------------------------------------------------------------------------
# Step 2: Extract PRIMARY outcome variables
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("STEP 2: Extracting PRIMARY outcome variables")
print("=" * 60)

primary_content = variable_extractor.get_content(sap, primary_outcome=True)
print(f"Primary SAP content ({len(primary_content):,} chars):")
print(f"  {primary_content[:300]}...")

primary_variables, primary_error = variable_extractor.extract(
    sap_text=primary_content,
    timepoints=timepoints,
    primary_outcome=True,
)

if primary_error:
    print(f"\nError extracting primary variables: {primary_error}")
else:
    print(f"\nExtracted {len(primary_variables)} primary variable(s):")
    print(json.dumps(primary_variables, indent=2))

# ---------------------------------------------------------------------------
# Step 3: Extract SECONDARY outcome variables
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("STEP 3: Extracting SECONDARY outcome variables")
print("=" * 60)

secondary_content = variable_extractor.get_content(sap, primary_outcome=False)
print(f"Secondary SAP content ({len(secondary_content):,} chars):")
print(f"  {secondary_content[:300]}...")

secondary_variables, secondary_error = variable_extractor.extract(
    sap_text=secondary_content,
    timepoints=timepoints,
    primary_outcome=False,
)

if secondary_error:
    print(f"\nError extracting secondary variables: {secondary_error}")
else:
    print(f"\nExtracted {len(secondary_variables)} secondary variable(s):")
    print(json.dumps(secondary_variables, indent=2))

# ---------------------------------------------------------------------------
# Step 4: Validate both sets
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("STEP 4: Validation")
print("=" * 60)

for label, variables in [("Primary", primary_variables), ("Secondary", secondary_variables)]:
    errors, warnings = variable_extractor.validate(variables, timepoints_list=timepoints)
    print(f"\n{label} variables:")
    print(f"  Errors   ({len(errors)}): {errors or 'none'}")
    print(f"  Warnings ({len(warnings)}): {warnings or 'none'}")

