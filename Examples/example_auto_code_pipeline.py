"""
Example staged AutoCode pipeline (Stage 1: Timepoints)

- Loads a pre-extracted SAP JSON from the shared SAPs folder
- Extracts timepoints using TimepointExtractor + OpenAIChat
- Validates the extracted timepoints with actionable error messages

Assumptions:
- You have SAPAI_SHARED_PATH set in your environment (or .env)
- The file {SAPAI_SHARED_PATH}/SAPs/{sap_name}.json exists
- auto_sap package imports resolve in your environment
"""

from pathlib import Path
import os
import json
import re

import dotenv
dotenv.load_dotenv()

from auto_sap.classes.auto_code_classes import TimepointExtractor
from auto_sap.classes.chat_classes import OpenAIChat
from auto_sap.classes.auto_code_api_classes import TrialCreator, AutoCodeAPI


# ----------------------------
# Helpers
# ----------------------------

def canonicalize_timepoint_id(label: str, value: int | None = None) -> str:
    """
    Create a stable, machine-safe id for a timepoint.
    Preference:
      1) if value is provided: week{value}
      2) else: slugify label
    """
    if value is not None:
        return f"week{value}"

    # slugify label
    s = label.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "timepoint"


def ensure_timepoint_ids(timepoints: list[dict]) -> list[dict]:
    """
    Ensure each timepoint dict has an 'id' field.
    Does not change existing ids.
    """
    used = set()
    out = []
    for tp in timepoints:
        tp2 = dict(tp)

        label = tp2.get("label", "")
        value = tp2.get("value", None)

        if "id" not in tp2 or not isinstance(tp2["id"], str) or not tp2["id"].strip():
            tp2["id"] = canonicalize_timepoint_id(label=str(label), value=value if isinstance(value, int) else None)

        # de-duplicate ids deterministically
        base = tp2["id"]
        new_id = base
        k = 2
        while new_id in used:
            new_id = f"{base}_{k}"
            k += 1
        tp2["id"] = new_id
        used.add(new_id)

        out.append(tp2)

    return out


def validate_timepoints(timepoints) -> list[str]:
    """
    Deterministic validator for extracted timepoints.
    Accepts either:
      - {"value": int, "label": str}
      - {"id": str, "value": int, "label": str}

    Returns a list of human-readable error strings (empty means valid).
    """
    errors = []

    if not isinstance(timepoints, list):
        return ["timepoints is not a list"]

    seen_ids = set()
    for i, item in enumerate(timepoints):
        if not isinstance(item, dict):
            errors.append(f"item {i} is not a dict")
            continue

        allowed_keys_2 = {"value", "label"}
        allowed_keys_3 = {"id", "value", "label"}
        keys = set(item.keys())

        if keys not in (allowed_keys_2, allowed_keys_3):
            errors.append(
                f"item {i} has keys {keys} (expected {allowed_keys_2} or {allowed_keys_3})"
            )
            continue

        # value
        if "value" not in item or not isinstance(item["value"], int):
            errors.append(f"item {i} value must be int")

        # label
        if "label" not in item or not isinstance(item["label"], str) or not item["label"].strip():
            errors.append(f"item {i} label must be non-empty string")

        # optional id
        if "id" in item:
            if not isinstance(item["id"], str) or not item["id"].strip():
                errors.append(f"item {i} id must be non-empty string")
            elif item["id"] in seen_ids:
                errors.append(f"duplicate timepoint id: {item['id']}")
            else:
                seen_ids.add(item["id"])

    return errors


# ----------------------------
# Main
# ----------------------------

def main():
    # Setting up chat bot and api connection
    chat_bot = OpenAIChat(model_name="gpt-5-nano")
    auto_code_api = AutoCodeAPI(dev=False)

    # Loading SAP content
    shared_path = os.getenv("SAPAI_SHARED_PATH")
    if not shared_path:
        raise EnvironmentError(
            "SAPAI_SHARED_PATH is not set. Add it to your .env or environment."
        )

    saps_path = Path(shared_path) / "SAPs"
    sap_name = "ACTISSIST_sap_v0.1"
    sap_file = saps_path / f"{sap_name}.json"

    if not sap_file.exists():
        raise FileNotFoundError(f"Could not find SAP JSON at: {sap_file}")

    with open(sap_file, "r", encoding="utf-8") as f:
        sap_json = json.load(f)

    print("\n\nsap_json keys are:\n", list(sap_json.keys()))

    # Step 1: Create trial_creator instance via auto_code_api using title and acronym
    trial_title = sap_json.get("title", "") or ""
    trial_acronym = sap_json.get("trial_acronym", "") or ""

    if not trial_title.strip() or not trial_acronym.strip():
        raise ValueError("Trial title or acronym missing in SAP JSON")
    else:
        print(f"\n\nCreating trial object for {trial_acronym}: {trial_title}\n")

    trial_creator = TrialCreator(
        auto_code_api,
        acronym=trial_acronym,
        title=trial_title
    )

    # Step 2: Timepoints (extract from relevant fields)
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

    # Many extractors return tuples/lists; keep this robust
    timepoints_return = timepoint_extractor.extract_timepoints(timepoint_content)

    # Expect first element to be list of dicts; fall back if direct list returned
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

    # Add stable IDs (internal), without breaking legacy schema
    timepoints_list = ensure_timepoint_ids(timepoints_list)

    print("\nTimepoints with ensured IDs:\n", timepoints_list)

    # Validate
    errors = validate_timepoints(timepoints_list)
    print("\nValidation:")
    if errors:
        print("❌ invalid timepoints")
        for e in errors:
            print(" -", e)
        raise ValueError("Timepoints validation failed; see errors above.")
    else:
        print("✅ timepoints valid")

    # NOTE: trial_creator usage for sending timepoints to API would go here,
    # once we confirm whether AutoCodeAPI expects label/value/id, etc.
    # For now we stop at extraction + validation, as per staged pipeline.

    print("\nDone.")


if __name__ == "__main__":
    main()
