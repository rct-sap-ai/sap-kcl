from Classes.template_class import Template
from Classes.protocol_classes import Protocol
from Prompts import prompts_06 as prompts_file

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

# Set up template with template file and prompts   
template = Template(
    template_path = "Templates/DRAFT Q-162 (SAP Template) V2.0.docx", 
    prompts_file=prompts_file, 
    prompt_register=prompt_tasks
)

# Give the template a prtocol and wtite a sap
protocol = Protocol("Protocols/boppp.pdf")
template.get_sap_content(protocol.protocol_txt)

template.save_content_as_text(path = "SAPs/bopp_sap_content.txt")
template.populate(sap_folder = "SAPs", sap_name = "bopp_sap_v0.1.docx")