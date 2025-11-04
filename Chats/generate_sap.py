import os
import sys
import glob
import time
import json
from dotenv import load_dotenv

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Classes.protocol_classes import Protocol
from chat_setup import get_chat
from Prompts import prompts_06 as prompts_file


load_dotenv()

# -----------------------
# Configuration
# -----------------------
# Single model configuration
MODEL_NAME = "gpt-4o-mini-2024-07-18"
REQUEST_DELAY_SEC = 1.0  # small delay to avoid rate limits
OUTPUT_DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), "SAP")

# -----------------------
# Prompt task list
# -----------------------
prompt_tasks = [
    ("title", prompts_file.generate_title_prompt),
    ("acronym", prompts_file.generate_acronym_prompt),
    ("isrctn_number", prompts_file.generate_isrctn_number_prompt),
    ("protocol_version", prompts_file.generate_protocol_version_prompt),
    ("protocol_date", prompts_file.generate_protocol_date_prompt),
    ("name_of_cheif_investigator", prompts_file.generate_name_of_cheif_investigator_prompt),
    ("senior_statistician", prompts_file.generate_senior_statistician_prompt),
    ("trial_acronym", prompts_file.generate_trial_acronym_prompt),
    ("description_of_trial", prompts_file.generate_description_of_trial_prompt),
    ("investigators", prompts_file.generate_investigators_prompt),
    ("principle_investigator", prompts_file.generate_principle_investigator_prompt),
    ("trial_manager", prompts_file.generate_trial_manager_prompt),
    ("trial_statisticians", prompts_file.generate_trial_statisticians_prompt),
    ("health_economist", prompts_file.generate_health_economist_prompt),
    ("primary_objectives", prompts_file.generate_primary_objectives_prompt),
    ("secondary_objectives", prompts_file.generate_secondary_objectives_prompt),
    ("trial_design", prompts_file.generate_trial_design_prompt),
    ("allocation_ratio", prompts_file.generate_allocation_ratio_prompt),
    ("randomization_level", prompts_file.generate_randomization_level_prompt),
    ("stratification_factors", prompts_file.generate_stratification_factors_prompt),
    ("number_of_arms", prompts_file.generate_number_of_arms_prompt),
    ("duration_of_treatment", prompts_file.generate_duration_of_treatment_prompt),
    ("follow_up_timepoints", prompts_file.generate_follow_up_timepoints_prompt),
    ("visit_windows", prompts_file.generate_visit_windows_prompt),
    ("data_collection_procedures", prompts_file.generate_data_collection_procedures_prompt),
    ("inclusion_criteria", prompts_file.generate_inclusion_criteria_prompt),
    ("exclusion_criteria", prompts_file.generate_exclusion_criteria_prompt),
    ("primary_outcome_measures", prompts_file.generate_primary_outcome_measures_prompt),
    ("secondary_outcome_measures", prompts_file.generate_secondary_outcome_measures_prompt),
    ("mediator_of_treatment", prompts_file.generate_mediator_of_treatment_prompt),
    ("moderator_of_treatment", prompts_file.generate_moderator_of_treatment_prompt),
    ("process_indicators", prompts_file.generate_process_indicators_prompt),
    ("adverse_events", prompts_file.generate_adverse_events_prompt),
    ("only_baseline_measures", prompts_file.generate_only_baseline_measures_prompt),
    ("additional_follow_up_measures", prompts_file.generate_additional_follow_up_measures_prompt),
    ("screening_recruitment_consort", prompts_file.generate_screening_recruitment_consort_prompt),
    ("treatment_compliance_definitition", prompts_file.generate_treatment_compliance_definitition_prompt),
    ("adherence_to_treatment", prompts_file.generate_adherence_to_treatment_prompt),
    ("descriptive_statistics", prompts_file.generate_descriptive_statistics_prompt),
    ("descriptive_of_intervention", prompts_file.generate_descriptive_of_intervention_prompt),
    ("descriptive_concomitant_medications", prompts_file.generate_descriptive_concomitant_medications_prompt),
    ("visit_window_deviation", prompts_file.generate_visit_window_deviation_prompt),
    ("primary_estimand", prompts_file.generate_primary_estimand_prompt),
    ("confidence_interval_p_value", prompts_file.generate_confidence_interval_p_value_prompt),
    ("primary_analysis_model", prompts_file.generate_primary_analysis_model_prompt),
    ("intercurrent_events_and_analysis", prompts_file.generate_intercurrent_events_and_analysis_prompt),
    ("secondary_estimands", prompts_file.generate_secondary_estimands_prompt),
    ("secondary_analysis", prompts_file.generate_secondary_analysis_prompt),
    ("time_points", prompts_file.generate_time_points_prompt),
    ("stratification_and_clustering", prompts_file.generate_stratification_and_clustering_prompt),
    ("missing_items_in_scales", prompts_file.generate_missing_items_in_scales_prompt),
    ("missing_baseline_data", prompts_file.generate_missing_baseline_data_prompt),
    ("missing_data_sensitivity_analysis", prompts_file.generate_missing_data_sensitivity_analysis_prompt),
    ("multiple_comparisons", prompts_file.generate_multiple_comparisons_prompt),
    ("analysis_for_noncompliance", prompts_file.generate_analysis_for_noncompliance_prompt),
    ("model_assumption_checks", prompts_file.generate_model_assumption_checks_prompt),
    ("other_sensitivity_analysis", prompts_file.generate_other_sensitivity_analysis_prompt),
    ("subgroup_analysis", prompts_file.generate_subgroup_analysis_prompt),
    ("any_additional_exploratory_analysis", prompts_file.generate_any_additional_exploratory_analysis_prompt),
    ("any_exploratory_mediator_and_moderator_analysis", prompts_file.generate_any_exploratory_mediator_and_moderator_analysis_prompt),
    ("interim_analysis", prompts_file.generate_interim_analysis_prompt),
]

# -----------------------
# Core functions
# -----------------------
def list_protocol_pdfs(protocols_dir: str):
    pattern = os.path.join(protocols_dir, "**", "*.pdf")
    return sorted(glob.glob(pattern, recursive=True))

def generate_sap_data(prompt_tasks, chat):
    """Run each prompt and build a JSON-serializable dict mapping tag -> AI response.

    Keys are the exact tag strings from prompts_06.ALL_TAGS where possible (e.g., "{{title}}").
    If a tag isn't found in ALL_TAGS, we'll default to wrapping the var name like "{{var_name}}".
    """
    # Build a normalization map from bare, lowercased tag name to the exact tag string with braces
    normalized_tag_map = {}
    if hasattr(prompts_file, "ALL_TAGS"):
        for tag in prompts_file.ALL_TAGS:
            bare = tag.strip("{}")
            normalized_tag_map[bare.lower()] = tag

    results = {}
    for var_name, prompt_func in prompt_tasks:
        prompt = prompt_func()

        print(f"Running {var_name}")
        try:
            response = chat.get_response(prompt=prompt)
            response_content = (response.get("content", "") or "").strip()
            if not response_content:
                response_content = "ERROR"
        except Exception as e:
            print(f"An error occurred: {e}")
            response_content = "ERROR"

        # Choose the JSON key using exact tag name if known; else, fall back to {{var_name}}
        key_norm = var_name.lower()
        tag_key = normalized_tag_map.get(key_norm, f"{{{{{var_name}}}}}")
        results[tag_key] = response_content

        time.sleep(REQUEST_DELAY_SEC)

    return results

def run_for_protocol(file_path: str):
    name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\n\n****** Trial: {name} ******\n")

    # Read protocol
    protocol = Protocol(file_path)
    protocol_txt = protocol.protocol_txt

    # Build system message using prompts_06
    system_message = prompts_file.system_message(protocol_txt)

    # Build chat
    chat = get_chat(system_message=system_message, model_name=MODEL_NAME)

    # Run prompts and build data dict
    sap_data = generate_sap_data(prompt_tasks, chat)

    # Save JSON
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Use the model name in the filename for clarity
    out_path = os.path.join(OUTPUT_DIR, f"{MODEL_NAME}_{name}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sap_data, f, ensure_ascii=False, indent=2)
    print(f"Wrote: {out_path}")

# -----------------------
# Main
# -----------------------
def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    protocols_dir = os.path.join(root_dir, "Protocols")

    pdf_paths = list_protocol_pdfs(protocols_dir)
    # Optionally restrict to a single filename by setting SAP_TARGET_PROTOCOL=boppp.pdf
    target = os.getenv("SAP_TARGET_PROTOCOL", "").strip().lower()
    if target:
        pdf_paths = [p for p in pdf_paths if os.path.basename(p).lower() == target]
    if not pdf_paths:
        if target:
            print(f"{target} not found under: {protocols_dir}")
        else:
            print(f"No PDF protocols found in: {protocols_dir}")
        return

    print(f"Found {len(pdf_paths)} protocol(s).")
    for file_path in pdf_paths:
        run_for_protocol(file_path)

if __name__ == "__main__":
    main()