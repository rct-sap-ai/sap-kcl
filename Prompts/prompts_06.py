
def system_message(part_protocol):
    system_message = f"""you are an expert statistician in the field of clinical trials.
    you are givena a clinical trial protocol with a full detail of the study design, including the primary 
    and secondary endpoints, sample size, and methods of statistical analysis and will be asked to write sections for a statistical analysis plan based on a clinical trial protocol.

    your answers always should be in the form of Statistical Analysis Plan (SAP). Only include in your response content that would be included in the specific section of a statistical analysis plan.
    
    Be concice. Write analysis section in paragrpahs, only use bullet points where specified in the prompt.
    
    The protocol for the trial is:
     
     {part_protocol}
    """

    return(system_message)



"""
prompts_06.py — Tag-specific prompt generators matching the structure and tone of prompts_05.py.
Each function returns a single prompt string for extracting content from a clinical trial protocol to populate the SAP template tags.
"""



# NOTE: Keep outputs concise, paragraph-first; use bullets only when the field is inherently a list.

ALL_TAGS = [
    "{{title}}",
    "{{acronym}}",
    "{{isrctn_number}}",
    "{{protocol_version}}",
    "{{protocol_date}}",
    "{{name_of_cheif_investigator}}",
    "{{senior_statistician}}",
    "{{trial_acronym}}",
    "{{description_of_trial}}",
    "{{investigators}}",
    "{{principle_investigator}}",
    "{{trial_manager}}",
    "{{trial_statisticians}}",
    "{{health_economist}}",
    "{{primary_objectives}}",
    "{{secondary_objectives}}",
    "{{trial_design}}",
    "{{allocation_ratio}}",
    "{{randomization_level}}",
    "{{stratification_factors}}",
    "{{number_of_arms}}",
    "{{duration_of_treatment}}",
    "{{follow_up_timepoints}}",
    "{{visit_windows}}",
    "{{data_collection_procedures}}",
    "{{inclusion_criteria}}",
    "{{exclusion_criteria}}",
    "{{primary_outcome_measures}}",
    "{{secondary_outcome_measures}}",
    "{{mediator_of_treatment}}",
    "{{moderator_of_treatment}}",
    "{{process_indicators}}",
    "{{adverse_events}}",
    "{{only_baseline_measures}}",
    "{{additional_follow_up_measures}}",
    "{{screening_recruitment_consort}}",
    "{{treatment_compliance_definitition}}",
    "{{adherence_to_treatment}}",
    "{{descriptive_statistics}}",
    "{{descriptive_of_intervention}}",
    "{{descriptive_concomitant_medications}}",
    "{{visit_window_deviation}}",
    "{{primary_estimand}}",
    "{{confidence_interval_p_value}}",
    "{{primary_analysis_model}}",
    "{{intercurrent_events_and_analysis}}",
    "{{secondary_estimands}}",
    "{{secondary_analysis}}",
    "{{time_points}}",
    "{{Stratification_and_clustering}}",
    "{{missing_items_in_scales}}",
    "{{missing_baseline_data}}",
    "{{missing_data_sensitivity_analysis}}",
    "{{multiple_comparisons}}",
    "{{analysis_for_noncompliance}}",
    "{{model_assumption_checks}}",
    "{{other_sensitivity_analysis}}",
    "{{subgroup_analysis}}",
    "{{any_additional_exploratory_analysis}}",
    "{{any_exploratory_mediator_and_moderator_analysis}}",
    "{{interim_analysis}}",
]

def get_all_tag_prompts():
    """Return a dict mapping '{{tag}}' -> prompt text."""
    return {
        "{{title}}": """Using the clinical trial protocol, extract the full trial title and return it exactly as it should appear in the Statistical Analysis Plan (SAP). Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{acronym}}": """Using the clinical trial protocol, extract the trial acronym and return it exactly as it should appear in the SAP. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{isrctn_number}}": """Using the clinical trial protocol, extract the ISRCTN (or equivalent single registry identifier if specified) and return it exactly as it should appear in the SAP. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{protocol_version}}": """Using the clinical trial protocol, extract the protocol version identifier and return it exactly as it should appear in the SAP. If multiple versions exist, select the current/most recent. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{protocol_date}}": """Using the clinical trial protocol, extract the protocol version date and return it exactly as it should appear in the SAP. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{name_of_cheif_investigator}}": """Using the clinical trial protocol, extract the full name and affiliation(s) for the Chief/Principal Investigator and return a concise SAP-ready line (name and affiliation only). Do not include postal addresses, emails, or phone numbers. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{senior_statistician}}": """Using the clinical trial protocol, extract the full name and affiliation(s) for the Senior Statistician and return a concise SAP-ready line (name and affiliation only). Do not include postal addresses, emails, or phone numbers. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{trial_acronym}}": """Using the clinical trial protocol, extract the trial acronym and return it exactly as it should appear in the SAP title line. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{description_of_trial}}": """Using the clinical trial protocol, write a brief description of the trial suitable for the SAP “Description of the trial” line (one or two sentences summarising population, interventions, and design). Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{investigators}}": """Using the clinical trial protocol, list the Investigators to be named in the SAP, presenting each as “Name, Affiliation”. Use one item per line. Do not include addresses or emails. Be concise. Write in paragraphs only if the protocol provides prose; otherwise present as a list exactly as specified. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{principle_investigator}}": """Using the clinical trial protocol, extract the full name and affiliation(s) for the Principal/Chief Investigator and return a concise SAP-ready line (name and affiliation only). Do not include postal addresses, emails, or phone numbers. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{trial_manager}}": """Using the clinical trial protocol, extract the full name and affiliation(s) for the Trial Manager and return a concise SAP-ready line (name and affiliation only). Do not include postal addresses, emails, or phone numbers. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{trial_statisticians}}": """Using the clinical trial protocol, list the Trial Statistician(s) with affiliation(s), one per line in “Name, Affiliation” format. Do not include postal addresses, emails, or phone numbers. Be concise. Use a list only if multiple persons are specified; otherwise provide a single line. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{health_economist}}": """Using the clinical trial protocol, extract the full name and affiliation(s) for the Trial Health Economist and return a concise SAP-ready line (name and affiliation only). Do not include postal addresses, emails, or phone numbers. Be concise. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{primary_objectives}}": """From the protocol, write the trial’s primary objective(s) exactly as specified. Present each primary objective as a separate sentence on its own line; do not add commentary. Be concise. Only include what belongs to this field. Do not invent information not present in the protocol.""",
        "{{secondary_objectives}}": """From the protocol, write the trial’s secondary objective(s) exactly as specified. Present each secondary objective as a separate sentence on its own line; do not add commentary. Be concise. Only include what belongs to this field. Do not invent information not present in the protocol.""",
        "{{trial_design}}": """Using the clinical trial protocol, write a concise description of the overall trial design (e.g., parallel-group randomised controlled trial; blinding status; hypothesis framework). Use full sentences; do not include randomisation mechanics here. Be concise. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{allocation_ratio}}": """Using the clinical trial protocol, extract the randomisation allocation ratio (e.g., 1:1, 2:1) and return it exactly as specified. Be concise. Only include what belongs to this field. Do not invent information not present in the protocol.""",
        "{{randomization_level}}": """Using the clinical trial protocol, extract the randomisation unit/level (e.g., participant, cluster/site) and return it exactly as specified. Be concise. Only include what belongs to this field. Do not invent information not present in the protocol.""",
        "{{stratification_factors}}": """From the protocol, list the randomisation stratification/minimisation factors exactly as specified (factor names and levels where given). Present each factor on its own bullet. Be concise. Do not add commentary. Do not invent information not present in the protocol.""",
        "{{number_of_arms}}": """Using the clinical trial protocol, state the number of treatment arms and provide the short name/label for each arm on its own line. Be concise. Only include what belongs to this field. Do not invent information not present in the protocol.""",
        "{{duration_of_treatment}}": """Using the clinical trial protocol, state the duration of treatment for each arm as applicable. Use sentences and include timing units exactly as specified. Be concise. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{follow_up_timepoints}}": """Using the clinical trial protocol, list all follow-up time points at which outcomes are measured. Present as bullets in chronological order, including timing windows if specified. Be concise. Do not invent information not present in the protocol.""",
        "{{visit_windows}}": """Using the clinical trial protocol, describe the visit windows for assessments exactly as specified. Use sentences or a compact list if the protocol lists discrete windows. Be concise. Do not invent information not present in the protocol.""",
        "{{data_collection_procedures}}": """Using the clinical trial protocol, summarise the data collection procedures relevant to the SAP (sources, systems, and timing) in one short paragraph. Be concise and factual. Do not include any content outside of this field. Do not invent information not present in the protocol.""",
        "{{inclusion_criteria}}": """From the protocol, list the inclusion criteria verbatim or as minimally edited bullets retaining the original meaning. One criterion per bullet. Do not add commentary or reorder unless the protocol provides an order. Be concise. Do not invent information not present in the protocol.""",
        "{{exclusion_criteria}}": """From the protocol, list the exclusion criteria verbatim or as minimally edited bullets retaining the original meaning. One criterion per bullet. Do not add commentary or reorder unless the protocol provides an order. Be concise. Do not invent information not present in the protocol.""",
        "{{primary_outcome_measures}}": """Using the clinical trial protocol, list each primary outcome as separate bullets and, for each, provide a one-sentence definition that includes the measure, timing, and unit (if applicable). Be concise. Do not invent information not present in the protocol.""",
        "{{secondary_outcome_measures}}": """Using the clinical trial protocol, list each secondary outcome as separate bullets and, for each, provide a one-sentence definition that includes the measure, timing, and unit (if applicable). Be concise. Do not invent information not present in the protocol.""",
        "{{mediator_of_treatment}}": """Using the clinical trial protocol, list any variables designated as mediators of treatment effects, one per bullet, with a brief phrase describing how each is assessed. Be concise. Do not invent information not present in the protocol.""",
        "{{moderator_of_treatment}}": """Using the clinical trial protocol, list any variables designated as moderators (effect modifiers), one per bullet, with a brief phrase describing how each is assessed. Be concise. Do not invent information not present in the protocol.""",
        "{{process_indicators}}": """Using the clinical trial protocol, list process indicators to be summarised (e.g., fidelity, exposure), one per bullet, with a short descriptor if provided. Be concise. Do not invent information not present in the protocol.""",
        "{{adverse_events}}": """Using the clinical trial protocol, write an adverse event reporting summary suitable for the SAP Harms section, including definitions to be used (AE/AR/SAE/SUSAR etc.), coding system (e.g., MedDRA) if specified, and which summaries will be presented. Be concise, paragraph style. Do not invent information not present in the protocol.""",
        "{{only_baseline_measures}}": """Using the clinical trial protocol, list any additional pre-randomisation measures to be collected and used in the SAP, one per bullet, including scale names where given. Be concise. Do not invent information not present in the protocol.""",
        "{{additional_follow_up_measures}}": """Using the clinical trial protocol, list any additional post-randomisation follow-up measures, one per bullet, including timing if specified. Be concise. Do not invent information not present in the protocol.""",
        "{{screening_recruitment_consort}}": """Using the clinical trial protocol, provide the key counts and pathways to populate a CONSORT-style flow (screened, eligible, randomised, allocated, treated, followed-up, analysed) as text bullets in logical order. Use only information available in the protocol. Be concise. Do not invent information not present in the protocol.""",
        "{{treatment_compliance_definitition}}": """Using the clinical trial protocol, define “treatment compliance/adherence” exactly as specified (thresholds, metrics, timing). Provide a single concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{adherence_to_treatment}}": """Using the clinical trial protocol, describe how adherence to allocated treatment will be assessed and summarised in the SAP (what, when, and how summarised). Provide one short paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{descriptive_statistics}}": """Using the clinical trial protocol, specify the descriptive statistics planned for outcome measures (what summaries, by which groups/time points). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{descriptive_of_intervention}}": """Using the clinical trial protocol, describe what descriptive summaries will be presented about the intervention(s) and those delivering them (e.g., dose, sessions, role). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{descriptive_concomitant_medications}}": """Using the clinical trial protocol, describe how concomitant medication data will be summarised in the SAP (what variables, how presented, timing). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{visit_window_deviation}}": """Using the clinical trial protocol, state how visit-window deviations will be handled/classified for reporting in the SAP. Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{primary_estimand}}": """Using the clinical trial protocol, define the primary estimand in text, explicitly covering: population, endpoint, treatment condition, intercurrent events handling strategy, and population-level summary. Provide concise SAP-ready prose. Be concise. Do not invent information not present in the protocol.""",
        "{{confidence_interval_p_value}}": """Using the clinical trial protocol, state the nominal significance level and the confidence interval level(s) to be used for reporting the treatment effect(s) in the SAP. Provide a concise sentence or short paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{primary_analysis_model}}": """Using the clinical trial protocol, describe the analysis model(s) for the primary outcome(s), including treatment effect parameterisation and planned covariate adjustments (e.g., stratification factors, baseline value of outcome). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{intercurrent_events_and_analysis}}": """Using the clinical trial protocol, list anticipated intercurrent events and the corresponding strategies or supplementary analyses to address them in the SAP. Use short sentences or bullets where the protocol lists items. Be concise. Do not invent information not present in the protocol.""",
        "{{secondary_estimands}}": """Using the clinical trial protocol, describe estimands for secondary outcomes where they differ from the primary estimand. Provide concise paragraph(s). Be concise. Do not invent information not present in the protocol.""",
        "{{secondary_analysis}}": """Using the clinical trial protocol, describe the analysis approach for secondary outcomes, including any shared model structures or covariate adjustments. Provide concise paragraph(s). Be concise. Do not invent information not present in the protocol.""",
        "{{time_points}}": """Using the clinical trial protocol, state the analysis time points for outcomes (how time will be used, and what data are used when windows exist). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{Stratification_and_clustering}}": """Using the clinical trial protocol, describe how stratification factors and any clustering will be accounted for in the analysis models. Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{missing_items_in_scales}}": """Using the clinical trial protocol, describe how missing items within multi-item scales/subscales will be handled (e.g., prorating rules). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{missing_baseline_data}}": """Using the clinical trial protocol, describe how missing baseline covariate data will be handled for analyses planned in the SAP. Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{missing_data_sensitivity_analysis}}": """Using the clinical trial protocol, outline any sensitivity analyses planned for missing outcome data (e.g., MNAR analyses), including the general approach. Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{multiple_comparisons}}": """Using the clinical trial protocol, state the approach to multiplicity (e.g., no adjustment; or specify adjustment method and scope). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{analysis_for_noncompliance}}": """Using the clinical trial protocol, describe any planned analyses addressing non-compliance (e.g., per-protocol, CACE), including the general approach. Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{model_assumption_checks}}": """Using the clinical trial protocol, describe the model assumption checks to be conducted and planned remedies if assumptions fail. Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{other_sensitivity_analysis}}": """Using the clinical trial protocol, describe any additional sensitivity analyses beyond missing data (what, why, and how in brief). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol.""",
        "{{subgroup_analysis}}": """Using the clinical trial protocol, describe any planned subgroup analyses and how they will be implemented (interaction terms in the main model). If none are planned, return: “No subgroup analysis will be conducted.” Be concise. Do not invent information not present in the protocol.""",
        "{{any_additional_exploratory_analysis}}": """Using the clinical trial protocol, describe any additional exploratory analyses planned (what outcomes, population, and general model). If none are planned, return: “No additional analysis will be conducted.” Be concise. Do not invent information not present in the protocol.""",
        "{{any_exploratory_mediator_and_moderator_analysis}}": """Using the clinical trial protocol, describe any planned exploratory mediation or moderation analyses (outcomes, mediators/moderators, and general model). If none are planned, return a single sentence stating none are planned. Be concise. Do not invent information not present in the protocol.""",
        "{{interim_analysis}}": """Using the clinical trial protocol, state whether interim analysis or an internal pilot is planned. If yes, provide the objectives, timing, methods/stopping rules, and any alpha/sample-size adjustments in concise prose; if not planned, return one clear sentence stating these are not included and no significance-level adjustments will be made. Be concise. Do not invent information not present in the protocol.""",
    }

def generate_title_prompt():
    """Return the prompt string for title."""
    return """Using the clinical trial protocol, extract the full trial title and return it exactly as it should appear in the Statistical Analysis Plan (SAP). Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_acronym_prompt():
    """Return the prompt string for acronym."""
    return """Using the clinical trial protocol, extract the trial acronym and return it exactly as it should appear in the SAP. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_isrctn_number_prompt():
    """Return the prompt string for isrctn_number."""
    return """Using the clinical trial protocol, extract the ISRCTN (or equivalent single registry identifier if specified) and return it exactly as it should appear in the SAP. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_protocol_version_prompt():
    """Return the prompt string for protocol_version."""
    return """Using the clinical trial protocol, extract the protocol version identifier and return it exactly as it should appear in the SAP. If multiple versions exist, select the current/most recent. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_protocol_date_prompt():
    """Return the prompt string for protocol_date."""
    return """Using the clinical trial protocol, extract the protocol version date and return it exactly as it should appear in the SAP. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_name_of_cheif_investigator_prompt():
    """Return the prompt string for name_of_cheif_investigator."""
    return """Using the clinical trial protocol, extract the full name and affiliation(s) for the Chief/Principal Investigator and return a concise SAP-ready line (name and affiliation only). Do not include postal addresses, emails, or phone numbers. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_senior_statistician_prompt():
    """Return the prompt string for senior_statistician."""
    return """Using the clinical trial protocol, extract the full name and affiliation(s) for the Senior Statistician and return a concise SAP-ready line (name and affiliation only). Do not include postal addresses, emails, or phone numbers. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_trial_acronym_prompt():
    """Return the prompt string for trial_acronym."""
    return """Using the clinical trial protocol, extract the trial acronym and return it exactly as it should appear in the SAP title line. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_description_of_trial_prompt():
    """Return the prompt string for description_of_trial."""
    return """Using the clinical trial protocol, write a brief description of the trial suitable for the SAP “Description of the trial” line (one or two sentences summarising population, interventions, and design). Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_investigators_prompt():
    """Return the prompt string for investigators."""
    return """Using the clinical trial protocol, list the Investigators to be named in the SAP, presenting each as “Name, Affiliation”. Use one item per line. Do not include addresses or emails. Be concise. Write in paragraphs only if the protocol provides prose; otherwise present as a list exactly as specified. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_principle_investigator_prompt():
    """Return the prompt string for principle_investigator."""
    return """Using the clinical trial protocol, extract the full name and affiliation(s) for the Principal/Chief Investigator and return a concise SAP-ready line (name and affiliation only). Do not include postal addresses, emails, or phone numbers. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_trial_manager_prompt():
    """Return the prompt string for trial_manager."""
    return """Using the clinical trial protocol, extract the full name and affiliation(s) for the Trial Manager and return a concise SAP-ready line (name and affiliation only). Do not include postal addresses, emails, or phone numbers. Be concise. Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_trial_statisticians_prompt():
    """Return the prompt string for trial_statisticians."""
    return """Using the clinical trial protocol, list the Trial Statistician(s) with affiliation(s), one per line in “Name, Affiliation” format. Do not include postal addresses, emails, or phone numbers. Be concise. Use a list only if multiple persons are specified; otherwise provide a single line. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_health_economist_prompt():
    """Return the prompt string for health_economist."""
    return """Using the clinical trial protocol, extract the full name and affiliation(s) for the Trial Health Economist and return a concise SAP-ready line (name and affiliation only). Do not include postal addresses, emails, or phone numbers. Be concise. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_primary_objectives_prompt():
    """Return the prompt string for primary_objectives."""
    return """From the protocol, write the trial’s primary objective(s) exactly as specified. Present each primary objective as a separate sentence on its own line; do not add commentary. Be concise. Only include what belongs to this field. Do not invent information not present in the protocol."""

def generate_secondary_objectives_prompt():
    """Return the prompt string for secondary_objectives."""
    return """From the protocol, write the trial’s secondary objective(s) exactly as specified. Present each secondary objective as a separate sentence on its own line; do not add commentary. Be concise. Only include what belongs to this field. Do not invent information not present in the protocol."""

def generate_trial_design_prompt():
    """Return the prompt string for trial_design."""
    return """Using the clinical trial protocol, write a concise description of the overall trial design (e.g., parallel-group randomised controlled trial; blinding status; hypothesis framework). Use full sentences; do not include randomisation mechanics here. Be concise. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_allocation_ratio_prompt():
    """Return the prompt string for allocation_ratio."""
    return """Using the clinical trial protocol, extract the randomisation allocation ratio (e.g., 1:1, 2:1) and return it exactly as specified. Be concise. Only include what belongs to this field. Do not invent information not present in the protocol."""

def generate_randomization_level_prompt():
    """Return the prompt string for randomization_level."""
    return """Using the clinical trial protocol, extract the randomisation unit/level (e.g., participant, cluster/site) and return it exactly as specified. Be concise. Only include what belongs to this field. Do not invent information not present in the protocol."""

def generate_stratification_factors_prompt():
    """Return the prompt string for stratification_factors."""
    return """From the protocol, list the randomisation stratification/minimisation factors exactly as specified (factor names and levels where given). Present each factor on its own bullet. Be concise. Do not add commentary. Do not invent information not present in the protocol."""

def generate_number_of_arms_prompt():
    """Return the prompt string for number_of_arms."""
    return """Using the clinical trial protocol, state the number of treatment arms and provide the short name/label for each arm on its own line. Be concise. Only include what belongs to this field. Do not invent information not present in the protocol."""

def generate_duration_of_treatment_prompt():
    """Return the prompt string for duration_of_treatment."""
    return """Using the clinical trial protocol, state the duration of treatment for each arm as applicable. Use sentences and include timing units exactly as specified. Be concise. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_follow_up_timepoints_prompt():
    """Return the prompt string for follow_up_timepoints."""
    return """Using the clinical trial protocol, list all follow-up time points at which outcomes are measured. Present as bullets in chronological order, including timing windows if specified. Be concise. Do not invent information not present in the protocol."""

def generate_visit_windows_prompt():
    """Return the prompt string for visit_windows."""
    return """Using the clinical trial protocol, describe the visit windows for assessments exactly as specified. Use sentences or a compact list if the protocol lists discrete windows. Be concise. Do not invent information not present in the protocol."""

def generate_data_collection_procedures_prompt():
    """Return the prompt string for data_collection_procedures."""
    return """Using the clinical trial protocol, summarise the data collection procedures relevant to the SAP (sources, systems, and timing) in one short paragraph. Be concise and factual. Do not include any content outside of this field. Do not invent information not present in the protocol."""

def generate_inclusion_criteria_prompt():
    """Return the prompt string for inclusion_criteria."""
    return """From the protocol, list the inclusion criteria verbatim or as minimally edited bullets retaining the original meaning. One criterion per bullet. Do not add commentary or reorder unless the protocol provides an order. Be concise. Do not invent information not present in the protocol."""

def generate_exclusion_criteria_prompt():
    """Return the prompt string for exclusion_criteria."""
    return """From the protocol, list the exclusion criteria verbatim or as minimally edited bullets retaining the original meaning. One criterion per bullet. Do not add commentary or reorder unless the protocol provides an order. Be concise. Do not invent information not present in the protocol."""

def generate_primary_outcome_measures_prompt():
    """Return the prompt string for primary_outcome_measures."""
    return """Using the clinical trial protocol, list each primary outcome as separate bullets and, for each, provide a one-sentence definition that includes the measure, timing, and unit (if applicable). Be concise. Do not invent information not present in the protocol."""

def generate_secondary_outcome_measures_prompt():
    """Return the prompt string for secondary_outcome_measures."""
    return """Using the clinical trial protocol, list each secondary outcome as separate bullets and, for each, provide a one-sentence definition that includes the measure, timing, and unit (if applicable). Be concise. Do not invent information not present in the protocol."""

def generate_mediator_of_treatment_prompt():
    """Return the prompt string for mediator_of_treatment."""
    return """Using the clinical trial protocol, list any variables designated as mediators of treatment effects, one per bullet, with a brief phrase describing how each is assessed. Be concise. Do not invent information not present in the protocol."""

def generate_moderator_of_treatment_prompt():
    """Return the prompt string for moderator_of_treatment."""
    return """Using the clinical trial protocol, list any variables designated as moderators (effect modifiers), one per bullet, with a brief phrase describing how each is assessed. Be concise. Do not invent information not present in the protocol."""

def generate_process_indicators_prompt():
    """Return the prompt string for process_indicators."""
    return """Using the clinical trial protocol, list process indicators to be summarised (e.g., fidelity, exposure), one per bullet, with a short descriptor if provided. Be concise. Do not invent information not present in the protocol."""

def generate_adverse_events_prompt():
    """Return the prompt string for adverse_events."""
    return """Using the clinical trial protocol, write an adverse event reporting summary suitable for the SAP Harms section, including definitions to be used (AE/AR/SAE/SUSAR etc.), coding system (e.g., MedDRA) if specified, and which summaries will be presented. Be concise, paragraph style. Do not invent information not present in the protocol."""

def generate_only_baseline_measures_prompt():
    """Return the prompt string for only_baseline_measures."""
    return """Using the clinical trial protocol, list any additional pre-randomisation measures to be collected and used in the SAP, one per bullet, including scale names where given. Be concise. Do not invent information not present in the protocol."""

def generate_additional_follow_up_measures_prompt():
    """Return the prompt string for additional_follow_up_measures."""
    return """Using the clinical trial protocol, list any additional post-randomisation follow-up measures, one per bullet, including timing if specified. Be concise. Do not invent information not present in the protocol."""

def generate_screening_recruitment_consort_prompt():
    """Return the prompt string for screening_recruitment_consort."""
    return """Using the clinical trial protocol, provide the key counts and pathways to populate a CONSORT-style flow (screened, eligible, randomised, allocated, treated, followed-up, analysed) as text bullets in logical order. Use only information available in the protocol. Be concise. Do not invent information not present in the protocol."""

def generate_treatment_compliance_definitition_prompt():
    """Return the prompt string for treatment_compliance_definitition."""
    return """Using the clinical trial protocol, define “treatment compliance/adherence” exactly as specified (thresholds, metrics, timing). Provide a single concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_adherence_to_treatment_prompt():
    """Return the prompt string for adherence_to_treatment."""
    return """Using the clinical trial protocol, describe how adherence to allocated treatment will be assessed and summarised in the SAP (what, when, and how summarised). Provide one short paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_descriptive_statistics_prompt():
    """Return the prompt string for descriptive_statistics."""
    return """Using the clinical trial protocol, specify the descriptive statistics planned for outcome measures (what summaries, by which groups/time points). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_descriptive_of_intervention_prompt():
    """Return the prompt string for descriptive_of_intervention."""
    return """Using the clinical trial protocol, describe what descriptive summaries will be presented about the intervention(s) and those delivering them (e.g., dose, sessions, role). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_descriptive_concomitant_medications_prompt():
    """Return the prompt string for descriptive_concomitant_medications."""
    return """Using the clinical trial protocol, describe how concomitant medication data will be summarised in the SAP (what variables, how presented, timing). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_visit_window_deviation_prompt():
    """Return the prompt string for visit_window_deviation."""
    return """Using the clinical trial protocol, state how visit-window deviations will be handled/classified for reporting in the SAP. Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_primary_estimand_prompt():
    """Return the prompt string for primary_estimand."""
    return """Using the clinical trial protocol, define the primary estimand in text, explicitly covering: population, endpoint, treatment condition, intercurrent events handling strategy, and population-level summary. Provide concise SAP-ready prose. Be concise. Do not invent information not present in the protocol."""

def generate_confidence_interval_p_value_prompt():
    """Return the prompt string for confidence_interval_p_value."""
    return """Using the clinical trial protocol, state the nominal significance level and the confidence interval level(s) to be used for reporting the treatment effect(s) in the SAP. Provide a concise sentence or short paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_primary_analysis_model_prompt():
    """Return the prompt string for primary_analysis_model."""
    return """Using the clinical trial protocol, describe the analysis model(s) for the primary outcome(s), including treatment effect parameterisation and planned covariate adjustments (e.g., stratification factors, baseline value of outcome). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_intercurrent_events_and_analysis_prompt():
    """Return the prompt string for intercurrent_events_and_analysis."""
    return """Using the clinical trial protocol, list anticipated intercurrent events and the corresponding strategies or supplementary analyses to address them in the SAP. Use short sentences or bullets where the protocol lists items. Be concise. Do not invent information not present in the protocol."""

def generate_secondary_estimands_prompt():
    """Return the prompt string for secondary_estimands."""
    return """Using the clinical trial protocol, describe estimands for secondary outcomes where they differ from the primary estimand. Provide concise paragraph(s). Be concise. Do not invent information not present in the protocol."""

def generate_secondary_analysis_prompt():
    """Return the prompt string for secondary_analysis."""
    return """Using the clinical trial protocol, describe the analysis approach for secondary outcomes, including any shared model structures or covariate adjustments. Provide concise paragraph(s). Be concise. Do not invent information not present in the protocol."""

def generate_time_points_prompt():
    """Return the prompt string for time_points."""
    return """Using the clinical trial protocol, state the analysis time points for outcomes (how time will be used, and what data are used when windows exist). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_stratification_and_clustering_prompt():
    """Return the prompt string for Stratification_and_clustering."""
    return """Using the clinical trial protocol, describe how stratification factors and any clustering will be accounted for in the analysis models. Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_missing_items_in_scales_prompt():
    """Return the prompt string for missing_items_in_scales."""
    return """Using the clinical trial protocol, describe how missing items within multi-item scales/subscales will be handled (e.g., prorating rules). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_missing_baseline_data_prompt():
    """Return the prompt string for missing_baseline_data."""
    return """Using the clinical trial protocol, describe how missing baseline covariate data will be handled for analyses planned in the SAP. Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_missing_data_sensitivity_analysis_prompt():
    """Return the prompt string for missing_data_sensitivity_analysis."""
    return """Using the clinical trial protocol, outline any sensitivity analyses planned for missing outcome data (e.g., MNAR analyses), including the general approach. Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_multiple_comparisons_prompt():
    """Return the prompt string for multiple_comparisons."""
    return """Using the clinical trial protocol, state the approach to multiplicity (e.g., no adjustment; or specify adjustment method and scope). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_analysis_for_noncompliance_prompt():
    """Return the prompt string for analysis_for_noncompliance."""
    return """Using the clinical trial protocol, describe any planned analyses addressing non-compliance (e.g., per-protocol, CACE), including the general approach. Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_model_assumption_checks_prompt():
    """Return the prompt string for model_assumption_checks."""
    return """Using the clinical trial protocol, describe the model assumption checks to be conducted and planned remedies if assumptions fail. Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_other_sensitivity_analysis_prompt():
    """Return the prompt string for other_sensitivity_analysis."""
    return """Using the clinical trial protocol, describe any additional sensitivity analyses beyond missing data (what, why, and how in brief). Provide one concise paragraph. Be concise. Do not invent information not present in the protocol."""

def generate_subgroup_analysis_prompt():
    """Return the prompt string for subgroup_analysis."""
    return """Using the clinical trial protocol, describe any planned subgroup analyses and how they will be implemented (interaction terms in the main model). If none are planned, return: “No subgroup analysis will be conducted.” Be concise. Do not invent information not present in the protocol."""

def generate_any_additional_exploratory_analysis_prompt():
    """Return the prompt string for any_additional_exploratory_analysis."""
    return """Using the clinical trial protocol, describe any additional exploratory analyses planned (what outcomes, population, and general model). If none are planned, return: “No additional analysis will be conducted.” Be concise. Do not invent information not present in the protocol."""

def generate_any_exploratory_mediator_and_moderator_analysis_prompt():
    """Return the prompt string for any_exploratory_mediator_and_moderator_analysis."""
    return """Using the clinical trial protocol, describe any planned exploratory mediation or moderation analyses (outcomes, mediators/moderators, and general model). If none are planned, return a single sentence stating none are planned. Be concise. Do not invent information not present in the protocol."""

def generate_interim_analysis_prompt():
    """Return the prompt string for interim_analysis."""
    return """Using the clinical trial protocol, state whether interim analysis or an internal pilot is planned. If yes, provide the objectives, timing, methods/stopping rules, and any alpha/sample-size adjustments in concise prose; if not planned, return one clear sentence stating these are not included and no significance-level adjustments will be made. Be concise. Do not invent information not present in the protocol."""
