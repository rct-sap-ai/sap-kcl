"""
Examples/example_auto_code_pipline.py

Stage 1 + Stage 2 sandbox runner for SAPAI / AutoCode pipeline:
- Loads a pre-extracted SAP JSON from {SAPAI_SHARED_PATH}/SAPs/{sap_name}.json
- Creates a TrialCreator object using AutoCodeAPI
- Stage 1: Extracts timepoints using TimepointExtractor + OpenAIChat
- Stage 1: Validates deterministically:
    - list of dicts
    - keys are exactly {'value','label'}
    - value is int
    - label is non-empty str
    - value is UNIQUE (canonical identifier)
- Stage 2: Extracts variables using VariableExtractor + OpenAIChat
- Stage 2: Validates deterministically:
    - list of dicts
    - keys are exactly {'variable','label','variable_type','timepoints'}
    - variable is non-empty str, unique, <= 28 chars (error)
    - label is non-empty str, warn if > 80 chars
    - variable_type is in allowed enum (error)
    - timepoints is list[int] and each is in extracted timepoint values (error)

Assumptions:
- SAPAI_SHARED_PATH is set in your environment or .env
- auto_sap imports resolve in your environment
- auto_sap.classes.auto_code_classes contains TimepointExtractor and VariableExtractor
"""

from pathlib import Path
import os
import json

import dotenv
dotenv.load_dotenv()

from auto_sap.classes.auto_code_classes import TimepointExtractor, VariableExtractor
from auto_sap.classes.chat_classes import OpenAIChat
from auto_sap.classes.auto_code_api_classes import TrialCreator, AutoCodeAPI


def validate_timepoints(timepoints) -> list[str]:
    """
    Deterministic validator for extracted timepoints.

    Expected schema (per timepoint):
      {"value": int, "label": str}

    Additional invariant:
      - 'value' must be UNIQUE across the list (used as canonical identifier)

    Returns:
      List of error strings. Empty list => valid.
    """
    errors = []

    if not isinstance(timepoints, list):
        return ["timepoints is not a list"]

    seen_values = set()

    for i, item in enumerate(timepoints):
        if not isinstance(item, dict):
            errors.append(f"item {i} is not a dict")
            continue

        expected_keys = {"value", "label"}
        keys = set(item.keys())

        if keys != expected_keys:
            errors.append(f"item {i} has keys {keys} (expected exactly {expected_keys})")
            continue

        # value checks
        v = item.get("value", None)
        if not isinstance(v, int):
            errors.append(f"item {i} value must be int (got {type(v).__name__})")
        else:
            if v in seen_values:
                errors.append(f"duplicate timepoint value: {v} (item {i})")
            else:
                seen_values.add(v)

        # label checks
        lab = item.get("label", None)
        if not isinstance(lab, str) or not lab.strip():
            errors.append(f"item {i} label must be a non-empty string")

    return errors


def validate_variables(variables, valid_timepoint_values: set[int]) -> tuple[list[str], list[str]]:
    """
    Deterministic validator for variables.

    Expected schema (per variable):
      {
        "variable": <str, <=28 chars>,
        "label": <str>,
        "variable_type": <str>,
        "timepoints": <list[int]>
      }

    Constraints:
      - variable must be unique, non-empty, <= 28 chars (error)
      - label should be <= 80 chars (warning if longer)
      - variable_type must be in allowed enum (error)
      - timepoints must be list[int] and all values must exist in timepoints (error)

    Returns:
      (errors, warnings)
    """
    errors = []
    warnings = []

    if not isinstance(variables, list):
        return (["variables is not a list"], warnings)

    seen_vars = set()

    allowed_types = {
        "Continuous", "Binary", "Count", "Categorical", "TimeToEvent"
    }

    for i, item in enumerate(variables):
        if not isinstance(item, dict):
            errors.append(f"variable item {i} is not a dict")
            continue

        expected_keys = {"variable", "label", "variable_type", "timepoints"}
        keys = set(item.keys())
        if keys != expected_keys:
            errors.append(f"variable item {i} has keys {keys} (expected exactly {expected_keys})")
            continue

        var = item.get("variable")
        lab = item.get("label")
        vtype = item.get("variable_type")
        tps = item.get("timepoints")

        # variable
        if not isinstance(var, str) or not var.strip():
            errors.append(f"variable item {i} variable must be a non-empty string")
        else:
            if len(var) > 28:
                errors.append(f"variable item {i} variable '{var}' exceeds 28 chars")
            if var in seen_vars:
                errors.append(f"duplicate variable name '{var}' (item {i})")
            seen_vars.add(var)

        # label
        if not isinstance(lab, str) or not lab.strip():
            errors.append(f"variable item {i} label must be a non-empty string")
        else:
            if len(lab) > 80:
                warnings.append(f"variable item {i} label is >80 chars (may harm table output): '{lab[:80]}…'")

        # variable_type
        if not isinstance(vtype, str) or vtype not in allowed_types:
            errors.append(
                f"variable item {i} variable_type must be one of {sorted(allowed_types)} (got {vtype})"
            )

        # timepoints
        if not isinstance(tps, list) or not all(isinstance(x, int) for x in tps):
            errors.append(f"variable item {i} timepoints must be a list[int]")
        else:
            missing = [x for x in tps if x not in valid_timepoint_values]
            if missing:
                errors.append(f"variable item {i} references missing timepoints: {missing}")

    return (errors, warnings)


def main():
    # ----------------------------
    # Setup chat + API
    # ----------------------------
    chat_bot = OpenAIChat(model_name="gpt-5-nano")
    auto_code_api = AutoCodeAPI(dev=False)

    # ----------------------------
    # Load SAP JSON
    # ----------------------------
    shared_path = os.getenv("SAPAI_SHARED_PATH")
    if not shared_path:
        raise EnvironmentError("SAPAI_SHARED_PATH is not set. Add it to your .env or environment.")

    saps_path = Path(shared_path) / "SAPs"
    sap_name = "ACTISSIST_sap_v0.1"
    sap_file = saps_path / f"{sap_name}.json"

    if not sap_file.exists():
        raise FileNotFoundError(f"Could not find SAP JSON at: {sap_file}")

    with open(sap_file, "r", encoding="utf-8") as file:
        sap_json = json.load(file)

    print("\n\nsap_json keys are:\n", list(sap_json.keys()))

    # ----------------------------
    # Step 1: Create trial object
    # ----------------------------
    trial_title = (sap_json.get("title", "") or "").strip()
    trial_acronym = (sap_json.get("trial_acronym", "") or "").strip()

    if not trial_title or not trial_acronym:
        raise ValueError("Trial title or acronym missing in SAP JSON")
    else:
        print(f"\n\nCreating trial object for {trial_acronym}: {trial_title}\n")

    trial_creator = TrialCreator(
        auto_code_api,
        acronym=trial_acronym,
        title=trial_title
    )

    # ----------------------------
    # Step 2: Timepoints extraction
    # ----------------------------
    print("\n\nTimepoint content extraction")

    timepoint_content = (
        (sap_json.get("follow_up_timepoints", "") or "")
        + "\n"
        + (sap_json.get("primary_outcome_measures", "") or "")
        + "\n"
        + (sap_json.get("secondary_outcome_measures", "") or "")
    ).strip()

    if not timepoint_content:
        raise ValueError(
            "No timepoint content found. Expected at least one of: "
            "follow_up_timepoints, primary_outcome_measures, secondary_outcome_measures."
        )

    print("\n--- timepoint_content (start) ---\n")
    print(timepoint_content)
    print("\n--- timepoint_content (end) ---\n")

    timepoint_extractor = TimepointExtractor(chat_bot=chat_bot)

    timepoints_return = timepoint_extractor.extract_timepoints(timepoint_content)

    # Robust unpacking: extractor may return list, or tuple/list where [0] is list
    if isinstance(timepoints_return, (list, tuple)) and len(timepoints_return) > 0 and isinstance(timepoints_return[0], list):
        timepoints_list = timepoints_return[0]
    elif isinstance(timepoints_return, list):
        timepoints_list = timepoints_return
    else:
        raise TypeError(
            f"Unexpected return type from extract_timepoints: {type(timepoints_return)}; "
            f"value: {repr(timepoints_return)[:500]}"
        )

    print("\nExtracted timepoints are:\n", timepoints_list)

    # ----------------------------
    # Validate timepoints
    # ----------------------------
    errors = validate_timepoints(timepoints_list)
    print("\nTimepoint validation:")
    if errors:
        print("❌ invalid timepoints")
        for e in errors:
            print(" -", e)
        raise ValueError("Timepoints validation failed; see errors above.")
    else:
        print("✅ timepoints valid")

    # ----------------------------
    # Step 3: Variables extraction
    # ----------------------------
    print("\n\nVariable content extraction")

    # Adjust these keys to match your SAP JSON fields (add/remove as needed)
    variable_content = (
        (sap_json.get("primary_outcome_measures", "") or "")
        + "\n"
        + (sap_json.get("secondary_outcome_measures", "") or "")
        + "\n"
        + (sap_json.get("other_variables", "") or "")
    ).strip()

    if not variable_content:
        print("⚠️ No variable content found in SAP JSON fields (primary/secondary/other_variables). Skipping Stage 2.")
        print("\nDone (Stage 1 complete).")
        return

    print("\n--- variable_content (start) ---\n")
    print(variable_content)
    print("\n--- variable_content (end) ---\n")

    variable_extractor = VariableExtractor(chat_bot=chat_bot)

    variables_return = variable_extractor.extract_variables(variable_content)

    # Robust unpacking: extractor may return list, or tuple/list where [0] is list
    if isinstance(variables_return, (list, tuple)) and len(variables_return) > 0 and isinstance(variables_return[0], list):
        variables_list = variables_return[0]
    elif isinstance(variables_return, list):
        variables_list = variables_return
    else:
        raise TypeError(
            f"Unexpected return type from extract_variables: {type(variables_return)}; "
            f"value: {repr(variables_return)[:500]}"
        )

    print("\nExtracted variables are:\n", variables_list)

    valid_timepoint_values = {tp["value"] for tp in timepoints_list}
    var_errors, var_warnings = validate_variables(variables_list, valid_timepoint_values)

    print("\nVariable validation:")
    for w in var_warnings:
        print("⚠️", w)

    if var_errors:
        print("❌ invalid variables")
        for e in var_errors:
            print(" -", e)
        raise ValueError("Variables validation failed; see errors above.")
    else:
        print("✅ variables valid")

    print("\nDone (Stage 1 + Stage 2 complete).")


if __name__ == "__main__":
    main()
