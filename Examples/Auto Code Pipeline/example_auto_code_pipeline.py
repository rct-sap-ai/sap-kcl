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

Stage 3: Analyses (AI-driven extraction with validator)
- Extracts analyses using AnalysisExtractor + OpenAIChat
- Pulls allowed analysis methods via auto_code_api.get_methods()
- Loops through outcomes and uses AI to pick appropriate analysis methods
- Automatically creates baseline descriptives for each outcome at timepoint 0 (if present)
- Validates deterministically:
    - outcome_variable exists in outcomes
    - timepoint exists for that outcome
    - method is one of allowed method IDs
    - table is non-empty string
    - warns if baseline descriptives are missing

Assumptions:
- SAPAI_SHARED_PATH is set in your environment or .env
- auto_sap imports resolve in your environment
- auto_sap.classes.auto_code_classes contains TimepointExtractor, VariableExtractor, and AnalysisExtractor
"""

from pathlib import Path
import os
import json

import dotenv
dotenv.load_dotenv()

from auto_sap.classes.auto_code_classes import TimepointExtractor, VariableExtractor, AnalysisExtractor
from auto_sap.classes.chat_classes import OpenAIChat
from auto_sap.classes.auto_code_api_classes import TrialCreator, AutoCodeAPI







# Helper functions removed - now part of AnalysisExtractor class


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


    outcomes, error = variable_extractor.extract(sap_text = variable_content, timepoints = timepoints_list)
    if error:
        print("❌ Error during variable extraction:", error)
        raise ValueError(f"Variable extraction failed: {error}")



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
    # Step 4: Analyses extraction (Stage 3)
    # ----------------------------
    analysis_extractor = AnalysisExtractor(chat_bot=chat_bot)

    print("\n\nAnalysis content extraction")

    analysis_content = analysis_extractor.get_content(sap_json)
    print("\n--- analysis_content (start) ---\n")
    print(analysis_content[:500] + "..." if len(analysis_content) > 500 else analysis_content)
    print("\n--- analysis_content (end) ---\n")

    # Get available methods from API
    methods = auto_code_api.get_methods()
    print("\nAvailable methods from API:\n", methods)
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

    print(f"\nFound {len(methods)} available methods from API")

    # Extract analyses using AI
    analysis_list, error = analysis_extractor.extract(
        sap_text=analysis_content,
        outcomes=outcomes,
        timepoints=timepoints_list,
        methods=methods
    )

    if error:
        print("❌ Error during analysis extraction:", error)
        raise ValueError(f"Analysis extraction failed: {error}")

    print("\nExtracted analyses:\n", analysis_list)

    # Validate analyses
    errors, warnings = analysis_extractor.validate(analysis_list, outcomes, allowed_method_ids)
    print("\nAnalyses validation:")
    if errors:
        print("❌ invalid analyses")
        for e in errors:
            print(" -", e)
        raise ValueError("Analyses validation failed; see errors above.")
    else:
        print("✅ analyses valid")
        if warnings:
            print("Warnings:")
            for w in warnings:
                print(" -", w)

    print("\nDone (Stage 1 + Stage 2 + Stage 3 complete).")


if __name__ == "__main__":
    main()
