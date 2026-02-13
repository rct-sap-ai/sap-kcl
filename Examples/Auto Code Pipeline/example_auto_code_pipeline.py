"""
Examples/example_auto_code_pipline.py

Stage 1 + Stage 2 + Stage 3 sandbox runner for SAPAI / AutoCode pipeline:

- Loads a pre-extracted SAP JSON from {SAPAI_SHARED_PATH}/SAPs/{sap_name}.json
- Creates a TrialCreator object using AutoCodeAPI

Stage 1: Timepoints
- Extracts timepoints using TimepointExtractor + OpenAIChat
- Validates deterministically:
    - list of dicts
    - keys are exactly {'value','label'}
    - value is int
    - label is non-empty str
    - value is UNIQUE (canonical identifier)

Stage 2: Variables (Outcomes)
- Extracts variables using VariableExtractor + OpenAIChat
- Validates deterministically:
    - list of dicts
    - keys are exactly {'variable','label','variable_type','timepoints'}
    - variable is non-empty str, unique, less than 28 charecters
    - label is non-empty str, warn if > 80 chars
    - variable_type is in allowed enum (error)
    - timepoints is list[int] and each is in extracted timepoint values (error)

Stage 3: Analyses (deterministic initial pass)
- Pulls allowed analysis methods via auto_code_api.get_methods()
- Picks descriptive + linear methods (keyword match; easy to swap to exact match)
- Generates a minimal analysis_list:
    - baseline descriptives for each outcome at timepoint 0 (if present)
    - main analysis linear model at max(timepoints) (if max != 0)
- Validates deterministically:
    - outcome_variable exists in outcomes
    - timepoint exists for that outcome
    - method is one of allowed method IDs
    - table is non-empty string

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







def pick_method_id(methods: list[dict], keyword: str) -> str:
    """
    Find a method id by keyword in method name/label/title.
    Expects items like: {"id": "...", "name": "..."} (or label/method/title).
    """
    keyword_l = keyword.lower()

    def get_name(m: dict) -> str:
        for k in ("name", "label", "method", "title"):
            if k in m and isinstance(m[k], str):
                return m[k]
        return ""

    for m in methods:
        if not isinstance(m, dict):
            continue
        name = get_name(m).lower()
        if keyword_l in name:
            return m.get("id") or m.get("method_id")

    raise ValueError(f"Could not find method id containing keyword: '{keyword}'")


def validate_analyses(analysis_list, outcomes: list[dict], allowed_method_ids: set) -> list[str]:
    """
    Deterministic validator for analyses.

    Expected schema (per analysis):
      {
        "outcome_variable": <str>,
        "timepoint": <int>,
        "method": <method_id>,
        "table": <str>
      }
    """
    errors = []

    if not isinstance(analysis_list, list):
        return ["analysis_list is not a list"]

    outcome_tp = {}
    for o in outcomes:
        v = o.get("variable")
        tps = o.get("timepoints")
        if isinstance(v, str) and isinstance(tps, list):
            outcome_tp[v] = set(tps)

    expected_keys = {"outcome_variable", "timepoint", "method", "table"}

    for i, a in enumerate(analysis_list):
        if not isinstance(a, dict):
            errors.append(f"analysis item {i} is not a dict")
            continue

        keys = set(a.keys())
        if keys != expected_keys:
            errors.append(f"analysis item {i} has keys {keys} (expected exactly {expected_keys})")
            continue

        ov = a.get("outcome_variable")
        tp = a.get("timepoint")
        mid = a.get("method")
        tab = a.get("table")

        if not isinstance(ov, str) or ov not in outcome_tp:
            errors.append(f"analysis item {i} outcome_variable '{ov}' not found in outcomes")
        else:
            if not isinstance(tp, int):
                errors.append(f"analysis item {i} timepoint must be int")
            else:
                if tp not in outcome_tp[ov]:
                    errors.append(
                        f"analysis item {i} timepoint {tp} not valid for outcome '{ov}' (allowed {sorted(outcome_tp[ov])})"
                    )

        if mid not in allowed_method_ids:
            errors.append(f"analysis item {i} method '{mid}' not in allowed methods from api.get_methods()")

        if not isinstance(tab, str) or not tab.strip():
            errors.append(f"analysis item {i} table must be non-empty string")

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

   
    timepoint_extractor = TimepointExtractor(chat_bot=chat_bot)

    print("\n\nTimepoint content extraction")

    timepoint_content = timepoint_extractor.get_content(sap_json)
    print("\n--- timepoint_content (start) ---\n")
    print(timepoint_content)
    print("\n--- timepoint_content (end) ---\n")


    timepoints_return = timepoint_extractor.extract(timepoint_content)

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

    errors = timepoint_extractor.validate(timepoints_list)
    print("\nTimepoint validation:")
    if errors:
        print("❌ invalid timepoints")
        for e in errors:
            print(" -", e)
        raise ValueError("Timepoints validation failed; see errors above.")
    else:
        print("✅ timepoints valid")

    # ----------------------------
    # Step 3: Variables extraction (Outcomes)
    # ----------------------------
    variable_extractor = VariableExtractor(chat_bot=chat_bot)


    print("\n\nVariable content extraction")

    variable_content = variable_extractor.get_content(sap_json)

    print("\n--- variable_content (start) ---\n")
    print(variable_content)
    print("\n--- variable_content (end) ---\n")


    variables_return = variable_extractor.extract(sap_text = variable_content, timepoints = timepoints_list)

    if isinstance(variables_return, (list, tuple)) and len(variables_return) > 0 and isinstance(variables_return[0], list):
        outcomes = variables_return[0]
    elif isinstance(variables_return, list):
        outcomes = variables_return
    else:
        raise TypeError(
            f"Unexpected return type from extract_variables: {type(variables_return)}; "
            f"value: {repr(variables_return)[:500]}"
        )

    print("\nExtracted outcomes are:\n", outcomes)

    errors, warnings = variable_extractor.validate(outcomes, timepoints_list)
    print("\nVariable validation:")
    if errors:
        print("❌ invalid variables")
        for e in errors:
            print(" -", e)
        raise ValueError("Variables validation failed; see errors above.")
    else:
        print("✅ variables valid")
        print("Warnings:")
        for w in warnings:
            print(" -", w)

    

    # ----------------------------
    # Step 4: Analyses generation (Stage 3)
    # ----------------------------
    print("\n\nAnalyses stage (API methods + minimal analysis_list)")

    methods = auto_code_api.get_methods()
    if not isinstance(methods, list) or len(methods) == 0:
        raise ValueError("api.get_methods() returned no methods or unexpected format")

    allowed_method_ids = set()
    for m in methods:
        if isinstance(m, dict):
            mid = m.get("id") or m.get("method_id")
            if mid:
                allowed_method_ids.add(mid)

    if not allowed_method_ids:
        raise ValueError("Could not extract any method IDs from api.get_methods() response")

    descriptive_method_id = pick_method_id(methods, "descriptive")
    linear_model_method_id = pick_method_id(methods, "linear")

    print("Picked descriptive_method_id:", descriptive_method_id)
    print("Picked linear_model_method_id:", linear_model_method_id)

    analysis_list = []

    for o in outcomes:
        ov = o["variable"]
        tps = o["timepoints"]

        if 0 in tps:
            analysis_list.append({
                "outcome_variable": ov,
                "timepoint": 0,
                "method": descriptive_method_id,
                "table": "baseline"
            })

        if len(tps) > 0:
            last_tp = max(tps)
            if last_tp != 0:
                analysis_list.append({
                    "outcome_variable": ov,
                    "timepoint": last_tp,
                    "method": linear_model_method_id,
                    "table": "main_analysis"
                })

    print("\nGenerated analysis_list:\n", analysis_list)

    analysis_errors = validate_analyses(analysis_list, outcomes, allowed_method_ids)
    print("\nAnalyses validation:")
    if analysis_errors:
        print("❌ invalid analyses")
        for e in analysis_errors:
            print(" -", e)
        raise ValueError("Analyses validation failed; see errors above.")
    else:
        print("✅ analyses valid")

    print("\nDone (Stage 1 + Stage 2 + Stage 3 complete).")


if __name__ == "__main__":
    main()
