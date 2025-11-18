
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
    "{{sample_size}}",
    "{{timing_of_analysis}}",
    "{{screening_recruitment_consort}}",
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



# 1. Put all your prompt texts in a single dict.



PROMPTS = {
        "{{title}}": """
        - Using the clinical trial protocol, extract the full trial title and return it exactly as it should appear in the Statistical Analysis Plan (SAP). 
        - Be concise. 
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        """,

        "{{acronym}}": """
        - Using the clinical trial protocol, extract the trial acronym and return it exactly as it should appear in the SAP. 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{isrctn_number}}": """
        - Using the clinical trial protocol, extract the ISRCTN (or equivalent single registry identifier if specified) and return it exactly as it should appear in the SAP. 
        - Be concise. 
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        """,
        
        "{{protocol_version}}": """
        - Using the clinical trial protocol, extract the protocol version identifier and return it exactly as it should appear in the SAP. 
        - If multiple versions exist, select the current/most recent (usually the biggest number). 
        - Be concise. 
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        """,
        
        "{{protocol_date}}": """
        - Using the clinical trial protocol, extract the protocol version date and return it exactly as it should appear in the SAP. 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{name_of_cheif_investigator}}": """
        - Using the clinical trial protocol, extract the full name and affiliation(s) for the Chief/Principal Investigator and return a concise SAP-ready line (name and affiliation only). 
        - Do not include postal addresses, emails, or phone numbers. 
        - Be concise. 
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        """,
        
        "{{senior_statistician}}": """
        - Using the clinical trial protocol, extract the full name and affiliation(s) for the Senior Statistician and return a concise SAP-ready line (name and affiliation only). 
        - Do not include postal addresses, emails, or phone numbers. 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{trial_acronym}}": """
        - Using the clinical trial protocol, extract the trial acronym and return it exactly as it should appear in the SAP title line. 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{description_of_trial}}": """
        - Using the clinical trial protocol, write a brief description of the trial suitable for the SAP “Description of the trial”.
        - Write a brief introduction that outlines the background and rationale for the study and the study objectives.
        - The background and rationale should consist of a synopsis of trial the background and rationale including a brief description of research question and brief justification for undertaking the trial
        - Breiefly mention the trial intervention.
        - Clearly state specific objectives or hypothesis.
        - Write this section using full paragraphs Do not use bullet points.
        - Do not write about the statistical analysis.
        - Be concise. 
        - Write in paragraphs, and only use bullet points when the protocol itself lists items or when the field is a list. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{investigators}}": """
        - Using the clinical trial protocol, list the Investigators to be named in the SAP, presenting each as “Name, Affiliation”. 
        - Use one item per line. 
        - Do not include addresses or emails. 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        - If there are no investigators listed in the protocol, return "No investigators are specified in the protocol."
        """,
        
        
        "{{principle_investigator}}": """
        - Using the clinical trial protocol, extract the full name and affiliation(s) for the Principal/Chief Investigator and return a concise SAP-ready line (name and affiliation only). 
        - Do not include postal addresses, emails, or phone numbers. 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,


        "{{trial_manager}}": """
        - Using the clinical trial protocol, extract the full name and affiliation(s) for the Trial Manager and return a concise SAP-ready line (name and affiliation only). 
        - Do not include postal addresses, emails, or phone numbers. 
        - Be concise. 
        - Do not invent information not present in the protocol.
        - if no trial manager mentioned in the protocol, return "No trial manager is specified in the protocol."
        """,
             
        "{{trial_statisticians}}": """
        - Using the clinical trial protocol, list the Trial Statistician(s) with affiliation(s), one per line in “Name, Affiliation” format. Do not include postal addresses, emails, or phone numbers. 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        - If no trial statisticians mentioned in the protocol, return "No trial statisticians are specified in the protocol.
        """,
        
        "{{health_economist}}": """
        - Using the clinical trial protocol, extract the full name and affiliation(s) for the Trial Health Economist and return a concise SAP-ready line (name and affiliation only). 
        - Do not include postal addresses, emails, or phone numbers. 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        - If no health economist mentioned in the protocol, return "No health economist is specified in the protocol.
        """,
        
        "{{primary_objectives}}": """
        - From the protocol, write the trial’s primary objective(s) exactly as specified. 
        - Present each primary objective as a separate sentence on its own line; do not add commentary.
        - Be concise. 
        - Only include what belongs to this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{secondary_objectives}}": """
        - From the protocol, write the trial’s secondary objective(s) exactly as specified. 
        - Present each secondary objective as a separate sentence on its own line; do not add commentary. 
        - Be concise. 
        - Only include what belongs to this field. 
        - Do not invent information not present in the protocol.
        """,


        "{{trial_design}}": """
        - Using the clinical trial protocol, write a concise description of the overall trial design (e.g., parallel-group randomised controlled trial; blinding status; hypothesis framework).
        - Use full sentences; do not include randomisation mechanics here.
        - Be concise.
        - Do not include any content outside of this field.
        - Do not invent information not present in the protocol.
        - Provide a general description of the study design (e.g., parallel, crossover, factorial, cluster-randomised, adaptive, etc.); do not include details on the objectives of the study.
        - Describe the number of arms and the allocation ratio (e.g., 1:1, 2:1); do not include details of the randomisation process.
        - Provide a brief description of each arm.
        - Specify the hypothesis testing framework (e.g., superiority, non-inferiority, equivalence); where applicable, specify which comparisons will be based on which framework.
        - Do not include details of the study objectives.
        - Write in full detail, using paragraphs and clear explanations; only use bullet points if absolutely necessary.
        - Focus only on the Study Design section as outlined above.
        """,
        
        "{{allocation_ratio}}": """
        - Using the clinical trial protocol, extract the randomisation allocation ratio (e.g., 1:1, 2:1) and return it exactly as specified. 
        - Be concise, just the ratio. 
        - Only include what belongs to this field. 
        - Do not invent information not present in the protocol.
        """,

        "{{randomization_level}}": """
        - Using the clinical trial protocol, extract the randomisation unit/level (e.g., participant, cluster/site) and return it exactly as specified. 
        - Be concise, just the level. 
        - Only include what belongs to this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{stratification_factors}}": """
        - From the protocol, list the randomisation stratification/minimisation factors exactly as specified (factor names and levels where given). 
        - Present each factor, just the names as a list separated by comma (,) in a single sentence. 
        - Be concise. 
        - Do not add commentary, or any other explanation in the beggining or the end. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{number_of_arms}}": """
        - Using the clinical trial protocol, state the number of treatment arms and provide the short name/label for each arm.
        - present it in a single senetnce separated ny comma, (like, two arms, beta blocker, placebo).
        - Be concise. 
        - Do not add commentary, or any other explanation in the beggining or the end. 
        - Only include what belongs to this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{duration_of_treatment}}": """
        - Using the clinical trial protocol, state the duration of treatment for each arm as applicable if the two arms are different, otherwise metion it is the same in both arms. 
        - Use sentences and include timing units exactly as specified. 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{follow_up_timepoints}}": """
        - Using the clinical trial protocol, list all follow-up time points at which outcomes are measured. 
        - Present as bullets in chronological order, including timing windows if specified. 
        - Be concise. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{visit_windows}}": """
        - Using the clinical trial protocol, describe the visit windows for assessments exactly as specified. 
        - Use sentences/lines or a compact list if the protocol lists discrete windows. 
        - Be concise. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{data_collection_procedures}}": """
        - Using the clinical trial protocol, summarise the data collection procedures relevant to the SAP (sources, systems, and timing) in one short paragraph. 
        - Be concise and factual. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{inclusion_criteria}}": """
        - From the protocol, list the inclusion criteria as minimally edited bullets retaining the original inclusion criteria. 
        - One criterion per bullet. 
        - Do not add commentary or reorder unless the protocol provides an order. 
        - Be concise. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{exclusion_criteria}}": """
        -From the protocol, list the exclusion criteria verbatim or as minimally edited bullets retaining the original meaning. One criterion per bullet. 
        - Do not add commentary or reorder unless the protocol provides an order. 
        - Be concise. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{primary_outcome_measures}}": """
        - Using the clinical trial protocol, list the primary outcome (or if more than one) and provide a  definition that includes the measure, timing, and unit (if applicable).
        - Speicfication of outcome
        Timing of assessment
        Specific measurement units if applicable
        Any transformations or calculations used to derive the outcome.
        Use a single paragraph to describe each outcome. Write a separeate paragraph for each outcome, even if given together in the protocol.
        - Do not report health or cost utility outocmes
        #Examples: 
        protocl text: Rate of readmission to hopsital within 30 or 90 days of discharge, survival (overall, progression-free).
        correct output:    
        Number of particiapants readmitted to hospital within 30 days of discharge.
        Number of participants readmitted to hospital within 90 days of discharge. 
        Time to death from any cause (overall survival), assessed from randomisation to death or final follow-up.
        Time to disease progression or death (progression-free survival), assessed from randomisation to disease progression,  death, or final follow up.
        - Be concise. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{secondary_outcome_measures}}": """
        - Using the clinical trial protocol, list each secondary outcome as separate bullets and, for each, provide a one-sentence definition that includes the measure, timing, and unit (if applicable).
        - Speicfication of outcome
        Timing of assessment
        Specific measurement units if applicable
        Any transformations or calculations used to derive the outcome.
        Use a single paragraph to describe each outcome. Write a separeate paragraph for each outcome, even if given together in the protocol.
        - Do not report health or cost utility outocmes
        #Examples: 
        protocl text: Rate of readmission to hopsital within 30 or 90 days of discharge, survival (overall, progression-free).
        correct output:    
        Number of particiapants readmitted to hospital within 30 days of discharge.
        Number of participants readmitted to hospital within 90 days of discharge. 
        Time to death from any cause (overall survival), assessed from randomisation to death or final follow-up.
        Time to disease progression or death (progression-free survival), assessed from randomisation to disease progression,  death, or final follow up. 
        - Be concise. 
        - Do not invent information not present in the protocol.
        """,

        "{{mediator_of_treatment}}": """
        - Using only the clinical trial protocol, identify variables that are explicitly specified as mediators of treatment effects or described as lying on the causal pathway between treatment and the primary or key secondary outcomes.
        - Include only variables that are pre-specified in the protocol; do not introduce post hoc mediators.
        - For each such variable, output one bullet containing a single sentence that states: the variable name, how it is assessed (instrument/scale, units), and planned measurement timepoints, if stated.
        - Be concise and use the terminology from the protocol where possible.
        - Do not infer or invent variables, timepoints, or measurement details that are not present in the protocol.
        - Do not describe or propose any mediation analysis; only list and describe the mediator variables.
        - If no mediators are specified, output a single bullet with the sentence: "No mediators of treatment effects are explicitly specified in the protocol."
        """,


        "{{moderator_of_treatment}}": """
        - Using only the clinical trial protocol, identify variables that are explicitly specified as moderators of treatment effects, effect modifiers, or subgroup-defining variables for assessing differential treatment effects.
        - Include only variables that are pre-specified in the protocol; do not introduce post hoc moderators.
        - For each such variable, output one bullet containing a single sentence that states: the variable name, whether it is baseline or time-varying, how it is assessed (instrument/scale, units or categories), and any relevant categories or cut-points if stated.
        - Be concise and use the terminology from the protocol where possible.
        - Do not infer or invent variables, categories, or measurement details that are not present in the protocol.
        - Do not describe or propose any moderation, interaction, or subgroup analysis; only list and describe the moderator variables.
        - If no moderators of treatment effects are specified, output a single bullet with the sentence: "No moderators of treatment effects are explicitly specified in the protocol."
        """,

        
        "{{process_indicators}}": """
        - Using only the clinical trial protocol, identify variables specified as process indicators to be summarised (e.g., fidelity, exposure, adherence, engagement, reach, implementation quality).
        - Include only process indicators that are pre-specified in the protocol; do not introduce post hoc indicators.
        - For each such variable, output one bullet containing a single sentence that states: the indicator name, what aspect of the process it reflects (e.g., fidelity, exposure), how it is assessed (instrument/measure, units or categories), and planned measurement timepoints, if stated.
        - Be concise and use the terminology from the protocol where possible.
        - Do not infer or invent indicators, categories, or measurement details that are not present in the protocol.
        - Do not describe or propose any statistical analysis of process indicators; only list and describe the indicators to be summarised.
        - If no process indicators are specified, output a single bullet with the sentence: "No process indicators are explicitly specified in the protocol."
        """,

        "{{adverse_events}}": """
        - Using only the clinical trial protocol, write a concise, paragraph-style summary of adverse event (harms) reporting suitable for inclusion in the Statistical Analysis Plan (SAP) Harms section.
        - Describe the adverse event–related definitions and terminology that will be used (e.g., AE, AR, SAE, SAR, SUSAR, AESI), using the wording from the protocol where possible.
        - State the coding system or dictionary for adverse events (e.g., MedDRA and version) if specified in the protocol.
        - Summarise which adverse event summaries and tabulations are planned according to the protocol (e.g., overall incidence, by treatment arm, by system organ class and preferred term, by severity, by relationship to treatment, serious vs non-serious events, AESIs, and relevant time windows such as on-treatment or follow-up), without adding new analyses.
        - Be concise and write in continuous prose (one to three short paragraphs), not bullet points.
        - Do not infer or invent definitions, coding systems, time windows, or analyses that are not present in the protocol.
        - If the protocol does not specify adverse event definitions, coding system, or planned summaries, write a single short paragraph stating that the protocol does not provide detailed specifications for adverse event reporting.
        """,

        "{{only_baseline_measures}}": """
        - Using only the clinical trial protocol, identify measures that are collected pre-randomisation (e.g., baseline covariates, screening or baseline assessments) and are intended to be used or reported in the Statistical Analysis Plan (SAP).
        - Include only pre-randomisation measures that are explicitly specified in the protocol; do not introduce post hoc measures.
        - For each such measure, output one bullet containing a single sentence that states: the measure/variable name, any scale or instrument used (including scale names and versions where given), the type of measure (e.g., clinical, laboratory, questionnaire), and the nominal timepoint (e.g., screening, baseline) if stated.
        - Be concise and use the terminology from the protocol where possible.
        - Do not infer or invent measures, scales, timepoints, or other details that are not present in the protocol.
        - Do not describe or propose any statistical analyses; only list and describe the pre-randomisation measures.
        - If no additional pre-randomisation measures are specified, output a single bullet with the sentence: "No additional pre-randomisation measures to be used in the SAP are explicitly specified in the protocol."
        """,

        "{{additional_follow_up_measures}}": """
        - Using only the clinical trial protocol, identify post-randomisation follow-up measures that are collected in addition to the primary and secondary outcomes (e.g., exploratory outcomes, additional questionnaires, long-term follow-up assessments, resource-use measures).
        - Include only additional follow-up measures that are explicitly specified in the protocol; do not introduce post hoc measures.
        - For each such measure, output one bullet containing a single sentence that states: the measure/variable name, any scale or instrument used (including scale names/versions where given), the planned follow-up timepoint(s), and a brief description of what it assesses if stated.
        - Be concise and use the terminology from the protocol where possible.
        - Do not repeat primary or secondary outcome measures that are already specified elsewhere.
        - Do not infer or invent measures, scales, timepoints, or other details that are not present in the protocol.
        - If no additional post-randomisation follow-up measures beyond the primary and secondary outcomes are specified, output a single bullet with the sentence: "No additional post-randomisation follow-up measures are explicitly specified in the protocol."
        """,

       "{{sample_size}}": """
        - Using only the extracted information from the clinical trial protocol provided above, write a comprehensive Sample Size and Power section suitable for inclusion in the Statistical Analysis Plan (SAP).
        - Describe in detail the methods used for sample size determination, including relevant design features (e.g., number of arms, allocation ratio, parallel-group or cluster-randomised design, superiority/non-inferiority/equivalence framework) as specified in the protocol.
        - Clearly state all assumptions used in the calculation, including effect size, standard deviation, event rates, control-group rates, variability parameters, correlations (e.g., for clustering or repeated measures), and any other explicitly reported inputs.
        - Specify the statistical test(s) or model(s) on which the sample size estimation is based (e.g., two-sample t-test, chi-square test, log-rank test, Cox model, mixed model), using the terminology from the protocol.
        - Report the planned power and significance level(s), stating whether the alpha level is one-sided or two-sided, as described in the protocol.
        - Describe any adjustments to the sample size for multiplicity, interim analyses, clustering (e.g., design effect, ICC, average cluster size), stratification, or unequal allocation, if these are specified.
        - Report any inflation or adjustment for anticipated dropouts, losses to follow-up, missing data, non-adherence, or other forms of attrition, including the target sample size after such adjustments.
        - Do not provide any justifications, critiques, or explanations for the methods or assumptions used; simply report the methods and parameters as described in the extracted information.
        - Write full paragraphs (not bullet points), be concise, and focus only on the Sample Size and Power section as outlined above.
        - Do not include any mathematical formulae or perform any new calculations beyond what is stated in the protocol.
        - Do not infer or invent methods, assumptions, or parameter values that are not present in the extracted information; if key details (e.g., certain assumptions or adjustments) are not specified, state briefly that these are not reported in the protocol.
        """,

        "{{timing_of_analysis}}": """
        - Using only the clinical trial protocol, write a concise section describing the timing of the final analysis suitable for inclusion in the Statistical Analysis Plan (SAP).
        - Clearly state when the final analysis will be conducted (e.g., after completion of follow-up for all participants and database lock, or at specific calendar dates or follow-up durations), using the terminology and conditions described in the protocol.
        - Describe the time points at which key outcomes are measured, including any planned visit “windows” or allowable ranges around the nominal visit dates, if these are specified.
        - If interim, safety, or other scheduled analyses are described in the protocol and are relevant to the timing of the final analysis, briefly summarise their timing and relationship to the final analysis.
        - Write in clear prose as one or more short paragraphs; do not use bullet points in the output unless the protocol itself presents timing information as a list that must be preserved.
        - Focus only on the timing of the final analysis and outcome data collection (measurement time points and windows); do not describe statistical methods, endpoints, or analysis sets in detail.
        - Be concise and use the terminology from the protocol where possible.
        - Do not infer or invent any analysis timings, measurement occasions, or visit windows that are not explicitly reported in the protocol.
        - If key details about the timing of the final analysis or the outcome measurement schedule are not specified in the protocol, state briefly that these details are not reported.
        """,

        "{{screening_recruitment_consort}}": """
        - Using only the clinical trial protocol, write a concise section for the Statistical Analysis Plan (SAP) describing screening, recruitment, and the planned CONSORT flow of participants.
        - Summarise how screening data (if collected) will be reported to describe the representativeness of the trial sample, including any information on the population approached or assessed for eligibility.
        - Provide a brief summary of eligibility based on the inclusion and exclusion criteria as described in the protocol, focusing on how these criteria relate to screening and recruitment reporting (do not restate the full criteria verbatim unless required for clarity).
        - Describe the information that will be included in the CONSORT flow diagram, including: numbers assessed for eligibility, eligible, consenting, refusing or declining participation, randomised/allocated, and, by treatment arm, numbers treated (or adequately/inadequately treated or compliant/non-compliant), numbers continuing in follow-up, numbers withdrawing, numbers lost to follow-up, numbers excluded from analysis, and numbers analysed, as specified in the protocol.
        - State the level and type of withdrawal (e.g., from intervention and/or from follow-up) that will be summarised, and indicate the timepoints at which withdrawal and lost to follow-up data will be presented if these are specified.
        - Describe how withdrawal and lost to follow-up data will be presented (e.g., counts and percentages by treatment arm and timepoint, reasons for withdrawal where available), including what details will be summarised, as outlined in the protocol.
        - List the baseline characteristics that are planned to be summarised to describe the recruited sample, using the terminology and structure given in the protocol (e.g., demographic, clinical, and other key prognostic variables), without proposing new variables.
        - Write the output in one or more clear paragraphs suitable for the SAP; do not use bullet points in the output unless the protocol itself presents key items as a list that must be preserved.
        - Do not describe or propose any new statistical analyses; focus only on the planned reporting of screening, recruitment, baseline characteristics, and the CONSORT flow of participants.
        - Be concise and use the terminology from the protocol where possible.
        - Do not infer or invent any screening, recruitment, or flow-diagram elements, timepoints, or baseline characteristics that are not explicitly reported in the protocol; if specific details (e.g., collection of screening logs, certain follow-up timepoints, or reasons for withdrawal) are not specified, state briefly that these details are not reported.
        """,

        
        "{{adherence_to_treatment}}": """
        - Using only the clinical trial protocol, write a concise description of how adherence to the allocated treatment/intervention will be assessed and summarised for inclusion in the Statistical Analysis Plan (SAP).
        - Clearly define adherence as specified in the protocol (e.g., threshold for being considered adherent, extent of exposure, allowed deviations), and describe how adherence is measured (e.g., pill counts, infusion records, self-report, electronic monitoring, clinic attendance).
        - State when adherence is assessed (e.g., at each visit, at specific follow-up timepoints, over the full treatment period), including any relevant assessment windows if these are reported.
        - Describe how adherence will be presented in the SAP (e.g., descriptively by treatment arm and timepoint, numbers and percentages adherent, summaries of continuous adherence measures such as percentage of doses taken), using the terminology from the protocol where possible.
        - Write the output as a single short paragraph (no bullet points in the output itself), be concise, and do not provide any justification or discussion beyond stating what is planned.
        - Do not infer or invent adherence definitions, thresholds, assessment methods, timepoints, or summaries that are not explicitly reported in the protocol; if details of adherence assessment or presentation are not specified, state briefly that these are not reported.
        """,

        "{{descriptive_statistics}}": """
        - Using only the clinical trial protocol, write a concise paragraph specifying the planned descriptive statistics for outcome measures and baseline characteristics for inclusion in the Statistical Analysis Plan (SAP).
        - For outcome measures, describe what descriptive summaries will be presented (e.g., means and standard deviations, medians and interquartile ranges, counts and percentages, change-from-baseline summaries), and indicate by which groups (e.g., treatment arms, overall) and at which timepoints or visits these summaries will be presented, as specified in the protocol.
        - For baseline characteristics, describe which types of variables (e.g., demographic, clinical, prognostic) will be summarised and how they will be summarised (e.g., continuous variables as means and standard deviations or medians and interquartile ranges; categorical variables as counts and percentages), and state whether summaries will be presented by treatment arm and/or overall, according to the protocol.
        - Do not include or propose any statistical tests or p-values for assessing imbalance in baseline characteristics; focus only on descriptive summaries.
        - Write the output as a single concise paragraph (no bullet points in the output itself), using the terminology from the protocol where possible.
        - Do not infer or invent types of summaries, variables, groups, or timepoints that are not explicitly reported in the protocol; if specific details of planned descriptive statistics are not specified, state briefly that these details are not reported.
        """,

        "{{descriptive_of_intervention}}": """
        - Using only the clinical trial protocol, write a concise paragraph describing the planned descriptive summaries of the intervention(s) (and, if applicable, control arms) and the people who deliver them for inclusion in the Statistical Analysis Plan (SAP).
        - Describe what aspects of the intervention(s) will be summarised (e.g., dose, number and duration of sessions, components delivered, mode of delivery, setting), and indicate how these will be summarised (e.g., means and standard deviations, medians and interquartile ranges, counts and percentages) and by which groups or arms, as specified in the protocol.
        - If applicable, describe what characteristics of the people delivering the intervention(s) (e.g., therapists, clinicians, facilitators) will be summarised (e.g., role, professional background, training, experience, number of patients treated) and how these summaries will be presented, according to the protocol.
        - Write the output as a single concise paragraph (no bullet points in the output itself), using the terminology from the protocol where possible.
        - Do not describe or propose any statistical tests; focus only on descriptive summaries of the intervention(s) and those delivering them.
        - Do not infer or invent intervention characteristics, provider characteristics, or descriptive summaries that are not explicitly reported in the protocol; if certain details are not specified, state briefly that these are not reported.
        """,



        
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


# 2. If you still want ALL_TAGS, derive it from PROMPTS so it never goes out of sync.
ALL_TAGS = list(PROMPTS.keys())


def get_prompt(tag: str) -> str:
    tag = tag.strip()
    if not tag.startswith("{{"):
        tag = f"{{{{{tag}}}}}"
    return PROMPTS.get(tag, "")



def generate_title_prompt():
    return get_prompt("title")

def generate_acronym_prompt():
    return get_prompt("acronym")

def generate_isrctn_number_prompt():
    return get_prompt("isrctn_number")

def generate_protocol_version_prompt():
    return get_prompt("protocol_version")

def generate_protocol_date_prompt():
    return get_prompt("protocol_date")

def generate_name_of_cheif_investigator_prompt():
    return get_prompt("name_of_cheif_investigator")

def generate_senior_statistician_prompt():
    return get_prompt("senior_statistician")

def generate_trial_acronym_prompt():
    return get_prompt("trial_acronym")

def generate_description_of_trial_prompt():
    return get_prompt("description_of_trial")

def generate_investigators_prompt():
    return get_prompt("investigators")

def generate_principle_investigator_prompt():
    return get_prompt("principle_investigator")

def generate_trial_manager_prompt():
    return get_prompt("trial_manager")

def generate_trial_statisticians_prompt():
    return get_prompt("trial_statisticians")

def generate_health_economist_prompt():
    return get_prompt("health_economist")

def generate_primary_objectives_prompt():
    return get_prompt("primary_objectives")

def generate_secondary_objectives_prompt():
    return get_prompt("secondary_objectives")

def generate_trial_design_prompt():
    return get_prompt("trial_design")

def generate_allocation_ratio_prompt():
    return get_prompt("allocation_ratio")

def generate_randomization_level_prompt():
    return get_prompt("randomization_level")

def generate_stratification_factors_prompt():
    return get_prompt("stratification_factors")

def generate_number_of_arms_prompt():
    return get_prompt("number_of_arms")

def generate_duration_of_treatment_prompt():
    return get_prompt("duration_of_treatment")

def generate_follow_up_timepoints_prompt():
    return get_prompt("follow_up_timepoints")

def generate_visit_windows_prompt():
    return get_prompt("visit_windows")

def generate_data_collection_procedures_prompt():
    return get_prompt("data_collection_procedures")

def generate_inclusion_criteria_prompt():
    return get_prompt("inclusion_criteria")

def generate_exclusion_criteria_prompt():
    return get_prompt("exclusion_criteria")

def generate_primary_outcome_measures_prompt():
    return get_prompt("primary_outcome_measures")

def generate_secondary_outcome_measures_prompt():
    return get_prompt("secondary_outcome_measures")

def generate_mediator_of_treatment_prompt():
    return get_prompt("mediator_of_treatment")

def generate_moderator_of_treatment_prompt():
    return get_prompt("moderator_of_treatment")

def generate_process_indicators_prompt():
    return get_prompt("process_indicators")

def generate_adverse_events_prompt():
    return get_prompt("adverse_events")

def generate_only_baseline_measures_prompt():
    return get_prompt("only_baseline_measures")

def generate_additional_follow_up_measures_prompt():
    return get_prompt("additional_follow_up_measures")

def generate_sample_size():
    return get_prompt("sample_size")

def generate_timing_of_analysis_prompt():
    return get_prompt("timing_of_analysis")

def generate_screening_recruitment_consort_prompt():
    return get_prompt("screening_recruitment_consort")

def generate_adherence_to_treatment_prompt():
    return get_prompt("adherence_to_treatment")

def generate_descriptive_statistics_prompt():
    return get_prompt("descriptive_statistics")

def generate_descriptive_of_intervention_prompt():
    return get_prompt("descriptive_of_intervention")

def generate_descriptive_concomitant_medications_prompt():
    return get_prompt("descriptive_concomitant_medications")

def generate_visit_window_deviation_prompt():
    return get_prompt("visit_window_deviation")

def generate_primary_estimand_prompt():
    return get_prompt("primary_estimand")

def generate_confidence_interval_p_value_prompt():
    return get_prompt("confidence_interval_p_value")

def generate_primary_analysis_model_prompt():
    return get_prompt("primary_analysis_model")

def generate_intercurrent_events_and_analysis_prompt():
    return get_prompt("intercurrent_events_and_analysis")

def generate_secondary_estimands_prompt():
    return get_prompt("secondary_estimands")

def generate_secondary_analysis_prompt():
    return get_prompt("secondary_analysis")

def generate_time_points_prompt():
    return get_prompt("time_points")

def generate_stratification_and_clustering_prompt():
    return get_prompt("stratification_and_clustering")

def generate_missing_items_in_scales_prompt():
    return get_prompt("missing_items_in_scales")

def generate_missing_baseline_data_prompt():
    return get_prompt("missing_baseline_data")

def generate_missing_data_sensitivity_analysis_prompt():
    return get_prompt("missing_data_sensitivity_analysis")

def generate_multiple_comparisons_prompt():
    return get_prompt("multiple_comparisons")

def generate_analysis_for_noncompliance_prompt():
    return get_prompt("analysis_for_noncompliance")

def generate_model_assumption_checks_prompt():
    return get_prompt("model_assumption_checks")

def generate_other_sensitivity_analysis_prompt():
    return get_prompt("other_sensitivity_analysis")

def generate_subgroup_analysis_prompt():
    return get_prompt("subgroup_analysis")

def generate_any_additional_exploratory_analysis_prompt():
    return get_prompt("any_additional_exploratory_analysis")

def generate_any_exploratory_mediator_and_moderator_analysis_prompt():
    return get_prompt("any_exploratory_mediator_and_moderator_analysis")

def generate_interim_analysis_prompt():
    return get_prompt("interim_analysis")