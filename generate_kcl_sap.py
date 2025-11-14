from Classes.template_class import Template
from Classes.protocol_classes import Protocol
from Classes.prompt_register_class import PromptRegister

from Prompts import prompts_06 as prompts_file

#reasoning_effort ="high", "medium", or "low", "minimal"
# verbosity = "high", "medium", or "low"
#PromptRegister(variable, prompt_function, reasoning_effort, verbosity)
prompt_tasks = [
    PromptRegister("title", prompts_file.generate_title_prompt,"minimal","low"),
    PromptRegister("acronym", prompts_file.generate_acronym_prompt,"minimal","low"),
    PromptRegister("isrctn_number", prompts_file.generate_isrctn_number_prompt,"minimal","low"),
    PromptRegister("protocol_version", prompts_file.generate_protocol_version_prompt,"minimal","low"),
    PromptRegister("protocol_date", prompts_file.generate_protocol_date_prompt,"minimal","low"),
    PromptRegister("name_of_cheif_investigator", prompts_file.generate_name_of_cheif_investigator_prompt,"minimal","low"),
    PromptRegister("senior_statistician", prompts_file.generate_senior_statistician_prompt,"minimal","low"),
    PromptRegister("trial_acronym", prompts_file.generate_trial_acronym_prompt,"minimal","low"),
    PromptRegister("description_of_trial", prompts_file.generate_description_of_trial_prompt,"minimal","low"),
    PromptRegister("investigators", prompts_file.generate_investigators_prompt,"minimal","low"),
    PromptRegister("principle_investigator", prompts_file.generate_principle_investigator_prompt,"minimal","low"),
    PromptRegister("trial_manager", prompts_file.generate_trial_manager_prompt,"minimal","low"),
    PromptRegister("trial_statisticians", prompts_file.generate_trial_statisticians_prompt,"minimal","low"),
    PromptRegister("health_economist", prompts_file.generate_health_economist_prompt,"minimal","low"),
    PromptRegister("primary_objectives", prompts_file.generate_primary_objectives_prompt,"minimal","low"),
    PromptRegister("secondary_objectives", prompts_file.generate_secondary_objectives_prompt,"minimal","low"),
    PromptRegister("trial_design", prompts_file.generate_trial_design_prompt,"minimal","low"),
    PromptRegister("allocation_ratio", prompts_file.generate_allocation_ratio_prompt,"minimal","low"),
    PromptRegister("randomization_level", prompts_file.generate_randomization_level_prompt,"minimal","low"),
    PromptRegister("stratification_factors", prompts_file.generate_stratification_factors_prompt,"minimal","low"),
    PromptRegister("number_of_arms", prompts_file.generate_number_of_arms_prompt,"minimal","low"),
    PromptRegister("duration_of_treatment", prompts_file.generate_duration_of_treatment_prompt,"minimal","low"),
    PromptRegister("follow_up_timepoints", prompts_file.generate_follow_up_timepoints_prompt,"minimal","low"),
    PromptRegister("visit_windows", prompts_file.generate_visit_windows_prompt,"minimal","low"),
    PromptRegister("data_collection_procedures", prompts_file.generate_data_collection_procedures_prompt,"minimal","low"),
    PromptRegister("inclusion_criteria", prompts_file.generate_inclusion_criteria_prompt,"minimal","low"),
    PromptRegister("exclusion_criteria", prompts_file.generate_exclusion_criteria_prompt,"minimal","low"),
    PromptRegister("primary_outcome_measures", prompts_file.generate_primary_outcome_measures_prompt,"minimal","low"),
    PromptRegister("secondary_outcome_measures", prompts_file.generate_secondary_outcome_measures_prompt,"minimal","low"),
    PromptRegister("mediator_of_treatment", prompts_file.generate_mediator_of_treatment_prompt,"minimal","low"),
    PromptRegister("moderator_of_treatment", prompts_file.generate_moderator_of_treatment_prompt,"minimal","low"),
    PromptRegister("process_indicators", prompts_file.generate_process_indicators_prompt,"minimal","low"),
    PromptRegister("adverse_events", prompts_file.generate_adverse_events_prompt,"minimal","low"),
    PromptRegister("only_baseline_measures", prompts_file.generate_only_baseline_measures_prompt,"minimal","low"),
    PromptRegister("additional_follow_up_measures", prompts_file.generate_additional_follow_up_measures_prompt,"minimal","low"),
    PromptRegister("screening_recruitment_consort", prompts_file.generate_screening_recruitment_consort_prompt,"minimal","low"),
    PromptRegister("treatment_compliance_definitition", prompts_file.generate_treatment_compliance_definitition_prompt,"minimal","low"),
    PromptRegister("adherence_to_treatment", prompts_file.generate_adherence_to_treatment_prompt,"minimal","low"),
    PromptRegister("descriptive_statistics", prompts_file.generate_descriptive_statistics_prompt,"minimal","low"),
    PromptRegister("descriptive_of_intervention", prompts_file.generate_descriptive_of_intervention_prompt,"minimal","low"),
    PromptRegister("descriptive_concomitant_medications", prompts_file.generate_descriptive_concomitant_medications_prompt,"minimal","low"),
    PromptRegister("visit_window_deviation", prompts_file.generate_visit_window_deviation_prompt,"minimal","low"),
    PromptRegister("primary_estimand", prompts_file.generate_primary_estimand_prompt,"minimal","low"),
    PromptRegister("confidence_interval_p_value", prompts_file.generate_confidence_interval_p_value_prompt,"minimal","low"),
    PromptRegister("primary_analysis_model", prompts_file.generate_primary_analysis_model_prompt,"minimal","low"),
    PromptRegister("intercurrent_events_and_analysis", prompts_file.generate_intercurrent_events_and_analysis_prompt,"minimal","low"),
    PromptRegister("secondary_estimands", prompts_file.generate_secondary_estimands_prompt,"minimal","low"),
    PromptRegister("secondary_analysis", prompts_file.generate_secondary_analysis_prompt,"minimal","low"),
    PromptRegister("time_points", prompts_file.generate_time_points_prompt,"minimal","low"),
    PromptRegister("stratification_and_clustering", prompts_file.generate_stratification_and_clustering_prompt,"minimal","low"),
    PromptRegister("missing_items_in_scales", prompts_file.generate_missing_items_in_scales_prompt,"minimal","low"),
    PromptRegister("missing_baseline_data", prompts_file.generate_missing_baseline_data_prompt,"minimal","low"),
    PromptRegister("missing_data_sensitivity_analysis", prompts_file.generate_missing_data_sensitivity_analysis_prompt,"minimal","low"),
    PromptRegister("multiple_comparisons", prompts_file.generate_multiple_comparisons_prompt,"minimal","low"),
    PromptRegister("analysis_for_noncompliance", prompts_file.generate_analysis_for_noncompliance_prompt,"minimal","low"),
    PromptRegister("model_assumption_checks", prompts_file.generate_model_assumption_checks_prompt,"minimal","low"),
    PromptRegister("other_sensitivity_analysis", prompts_file.generate_other_sensitivity_analysis_prompt,"minimal","low"),
    PromptRegister("subgroup_analysis", prompts_file.generate_subgroup_analysis_prompt,"minimal","low"),
    PromptRegister("any_additional_exploratory_analysis", prompts_file.generate_any_additional_exploratory_analysis_prompt,"minimal","low"),
    PromptRegister("any_exploratory_mediator_and_moderator_analysis", prompts_file.generate_any_exploratory_mediator_and_moderator_analysis_prompt,"minimal","low"),
    PromptRegister("interim_analysis", prompts_file.generate_interim_analysis_prompt,"minimal","low"),
]
system_message = prompts_file.system_message

# Set up template with template file and prompts   
template = Template(
    template_path = "Templates/DRAFT Q-162 (SAP Template) V2.0.docx", 
    system_message_function=prompts_file.system_message, 
    prompt_register=prompt_tasks
)

# Give the template a prtocol and wtite a sap
def write_sap(protocol_path, sap_name, sap_folder_path = "SAPs", test = False):
    protocol = Protocol(protocol_path)
    if not test:
        template.get_sap_content(protocol.protocol_txts)
    else:
        print("Test enabled - running with gpt5 nano")
        template.get_sap_content(protocol.protocol_txt, model = "gpt-5-nano")

    template.save_content_as_text(path = f"{sap_folder_path}/{sap_name}_content.txt")
    template.populate(sap_folder = sap_folder_path, sap_name = f"{sap_name}.docx")



# running with test = true uses gpt-5-nano which is faster and cheaper. Use to make sure everything runs.
write_sap(
    protocol_path="Protocols/boppp.pdf",
    sap_folder_path = "SAPs",
    sap_name = "bopp_sap_v0.1_test",
    test = True
)

# running with without test mode on uses full gpt-5. This is what we'll use in production so when refining prompts is best to use.
# write_sap(
#     protocol_path="Protocols/boppp.pdf",
#     sap_folder_path = "SAPs",
#     sap_name = "bopp_sap_v0.1",
# )