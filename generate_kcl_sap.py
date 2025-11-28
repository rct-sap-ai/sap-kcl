from Classes.template_class import Template
from Classes.protocol_classes import Protocol
from Classes.prompt_register_class import PromptRegister

from Prompts import prompts_06 as prompts_file

import time 

#reasoning_effort ="high", "medium", or "low", "minimal"
# verbosity = "high", "medium", or "low"
#PromptRegister(variable, prompt_function, reasoning_effort, verbosity)
prompt_tasks = [
    PromptRegister("title", "low","low"),
    PromptRegister("trial_acronym", "minimal","low"),
    PromptRegister("isrctn_number", "minimal","low"),
    PromptRegister("protocol_version_date", "minimal", "low"),
    PromptRegister("name_of_cheif_investigator", "low","low"),
    PromptRegister("senior_statistician", "low","low"),
    PromptRegister("trial_statistician", "low","low"),
    PromptRegister("description_of_trial", "medium","low"),
    PromptRegister("investigators", "low","low"),
    PromptRegister("trial_manager", "low","low"),
    PromptRegister("trial_statisticians", "low","low"),
    PromptRegister("health_economist", "low","low"),
    PromptRegister("primary_objectives", "minimal","low"),
    PromptRegister("secondary_objectives", "minimal","low"), 
    PromptRegister("trial_design", "minimal","low"),
    PromptRegister("randomisation_method", "minimal","low"),
    PromptRegister("randomisation_implementation", "minimal","low"),
    PromptRegister("duration_of_treatment", "minimal","low"),
    PromptRegister("follow_up_timepoints", "minimal","low"),
    PromptRegister("visit_windows", "low","low"),
    PromptRegister("data_collection_procedures", "minimal","low"), 
    PromptRegister("inclusion_criteria", "minimal","low"),
    PromptRegister("exclusion_criteria", "minimal","low"), # end of first section - trial design
    PromptRegister("primary_outcome_measures", "low","low"),
    PromptRegister("secondary_outcome_measures", "low","low"),
    PromptRegister("mediator_of_treatment", "low","low"),
    PromptRegister("moderator_of_treatment", "low","low"), 
    PromptRegister("process_indicators", "low","low"),
    PromptRegister("adverse_events", "low","low"),
    PromptRegister("only_baseline_measures", "low","low"),
    PromptRegister("additional_follow_up_measures", "low","low"),
    PromptRegister("sample_size", "low","low"),
    PromptRegister("timing_of_analysis", "low","low"),
    PromptRegister("screening_recruitment_consort", "minimal","low"),
    #PromptRegister("treatment_compliance_definitition", prompts_file.generate_treatment_compliance_definitition_prompt,"minimal","low"),
    PromptRegister("adherence_to_treatment", "minimal","low"),
    PromptRegister("descriptive_statistics", "minimal","low"),
    PromptRegister("descriptive_of_intervention", "minimal","low"),
    PromptRegister("descriptive_concomitant_medications", "minimal","low"),
    PromptRegister("visit_window_deviation", "minimal","low"), # end of second section - outcomes and descriptive analysis
    PromptRegister("primary_estimand", "minimal","low"),
    PromptRegister("confidence_interval_p_value", "minimal","low"),
    PromptRegister("primary_analysis_model", "minimal","low"),
    PromptRegister("intercurrent_events_and_analysis", "minimal","low"), 
    PromptRegister("secondary_estimands", "minimal","low"),
    PromptRegister("secondary_analysis", "minimal","low"),
    PromptRegister("time_points", "minimal","low"),  # end of third section - main analysis
    PromptRegister("stratification_and_clustering", "minimal","low"),
    PromptRegister("missing_items_in_scales", "minimal","low"),
    PromptRegister("missing_baseline_data", "minimal","low"),
    PromptRegister("missing_data_sensitivity_analysis", "minimal","low"),
    PromptRegister("multiple_comparisons", "minimal","low"),
    PromptRegister("analysis_for_noncompliance","minimal","low"),
    PromptRegister("model_assumption_checks", "minimal","low"),
    PromptRegister("other_sensitivity_analysis", "minimal","low"),
    PromptRegister("subgroup_analysis", "minimal","low"),
    PromptRegister("any_additional_exploratory_analysis", "minimal","low"),
    PromptRegister("any_exploratory_mediator_and_moderator_analysis", "minimal","low"),
    PromptRegister("interim_analysis", "minimal","low"), # end of final section - other bits
    PromptRegister("table_outcomes", "low","low"),
]


# Set up template with template file and prompts   
template = Template(
    template_path = "Templates/sapai_kcl_template_v0.1.docx", 
    system_message_function=prompts_file.system_message, 
    prompt_register=prompt_tasks,
    prompts_dictionary = prompts_file.PROMPTS_DICTIONARY
)

# Give the template a prtocol and wtite a sap
def write_sap(protocol_path, sap_name, sap_folder_path = "SAPs", test = False):
    t0 = time.time()

    protocol = Protocol(protocol_path)
    if not test:
        template.get_sap_content(protocol.protocol_txt)
    else:
        print("Test enabled - running with gpt5 nano")
        template.get_sap_content(protocol.protocol_txt, model = "gpt-5-nano")

    template.save_content_as_text(path = f"{sap_folder_path}/{sap_name}_content.txt")
    template.populate(sap_folder = sap_folder_path, sap_name = f"{sap_name}.docx")

    t1 = time.time()
    total_time = round(t1- t0)
    print(f"SAP written in {total_time} seconds")


#running with test = true uses gpt-5-nano which is faster and cheaper. Use to make sure everything runs.
# write_sap(
#     protocol_path="Protocols/boppp.pdf",
#     sap_folder_path = "SAPs",
#     sap_name = "bopp_sap_v0.1_test",
#     test = True
# )

#running with without test mode on uses full gpt-5. This is what we'll use in production so when refining prompts is best to use.
write_sap(
    protocol_path="Protocols/Feeling_safer.pdf",  
    sap_folder_path = "SAPs",
    sap_name = "feeling_safer_sap_v0.1",
)
