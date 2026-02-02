"""
Examples/example_auto_code_pipline.py

Stage 1 sandbox runner for SAPAI / AutoCode pipeline:
- Loads a pre-extracted SAP JSON from {SAPAI_SHARED_PATH}/SAPs/{sap_name}.json
- Creates a TrialCreator object using AutoCodeAPI
- Extracts timepoints using TimepointExtractor + OpenAIChat
- Validates deterministically:
    - list of dicts
    - keys are exactly {'value','label'}
    - value is int
    - label is non-empty str
    - value is UNIQUE (canonical identifier)

Assumptions:
- SAPAI_SHARED_PATH is set in your environment or .env
- auto_sap imports resolve in your environment
"""

from pathlib import Path
import os
import json

import dotenv
dotenv.load_dotenv()

from auto_sap.classes.auto_code_classes import TimepointExtractor
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
    print("\nValidation:")
    if errors:
        print("❌ invalid timepoints")
        for e in errors:
            print(" -", e)
        raise ValueError("Timepoints validation failed; see errors above.")
    else:
        print("✅ timepoints valid")

    print("\nDone (Stage 1 complete).")


if __name__ == "__main__":
    main()
