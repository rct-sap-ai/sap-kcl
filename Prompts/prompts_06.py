


def system_message(part_protocol):
    system_message = f"""you are an expert statistician in the field of clinical trials.
    you are givena a clinical trial protocol with a full detail of the study design, including the primary 
    and secondary endpoints, sample size, and methods of statistical analysis and will be asked to write sections for a statistical analysis plan based on a clinical trial protocol.

    Only include in your response content that would be included in the specific section of a statistical analysis plan.
    
    Be concice. Write analysis section in paragrpahs, only use bullet points where specified in the prompt.
    
    The protocol for the trial is:
     
     {part_protocol}
    """

    return(system_message)



"""
Each function returns a single prompt string for extracting content from a clinical trial protocol to populate the SAP template tags.
"""



# NOTE: Keep outputs concise, paragraph-first; use bullets only when the field is inherently a list.

# 1. Put all your prompt texts in a single dict.

PROMPTS_TITLE_ADMIN = {

    
        "{{title}}": """
        - Extract the full trial title from the protocol and return it exactly as it is given in the trial protcol. 
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        """,

        "{{acronym}}": """
        - Extract the trial acronym from the protocol and return it exactly as it is given in the trial protcol. 
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        """,
        
        "{{isrctn_number}}": """
        - Extract the ISRCTN (or equivalent single registry identifier if specified) from the protocol and return it exactly as it is given in the trial protcol. 
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        """,
        
        "{{protocol_version}}": """
        - Extract the protocol version identifier from the protocol and return it exactly as it is given in the trial protcol. 
        - If multiple versions exist, select the current/most recent (usually the biggest number). 
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        """,
        
        "{{protocol_date}}": """
        - Extract the protocol version date from the protocol and return it exactly as it is given in the trial protcol.
        - If multiple versions exist, select the current/most recent (usually the most recent date). 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,
        
        "{{name_of_cheif_investigator}}": """
        - Extract the full name and affiliation(s) for the Chief/Principal Investigator from the protocol and return a concise SAP-ready line (name and affiliation only). 
        - Do not include postal addresses, emails, or phone numbers. 
        - Example: Dr. Ben Carter, Kings College London Clinical Trials Unit, Institute of Psychiatry, Psychology and Neuroscience, King's College London 
        - Be concise. 
        - Do not include any content outside of this field. Do not invent information not present in the protocol.
        """,
        
        "{{senior_statistician}}": """
        - Extract the  full name and affiliation(s) for the Senior Statistician from the protocol and return a concise SAP-ready line (name and affiliation only). 
        - Do not include postal addresses, emails, or phone numbers. 
         - Example: Dr. Ben Carter, Kings College London Clinical Trials Unit, Institute of Psychiatry, Psychology and Neuroscience, King's College London 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        """,
}

def get_people_prompt(who):
        prompt = f""" 
        - Using the clinical trial protocol, list the {who} to be named in the SAP, presenting each as “Name, Affiliation”. 
        - Use one item per person. 
        - Do not include addresses or emails. 
        - Be concise. 
        - Do not include any content outside of this field. 
        - Do not invent information not present in the protocol.
        - If there are no {who} listed in the protocol, return "No {who} are specified in the protocol.""

        - Example: Dr. Ben Carter, Kings College London Clinical Trials Unit, Institute of Psychiatry, Psychology and Neuroscience, King's College London 

        """
        return(prompt)

PROMPTS_PEOPLE = {
           "{{investigators}}": get_people_prompt("investigators"),
           "{{principle_investigator}}": get_people_prompt("Chief/Principal Investigator"),
           "{{senior_statistician}}": get_people_prompt("senior statisticin"),
           "{{statisticians}}": get_people_prompt("statisticians"),
           "{{trial_manager}}": get_people_prompt("trial manager"),
           "{{health_economist}}": get_people_prompt("health economist"),


}

PROMPTS_INTRO_AND_DESIGN = {        
        "{{description_of_trial}}": """
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
        - Using the clinical trial protocol, write a concise description of the overall trial design 
        - Provide a  description of the study design (e.g., parallel, crossover, factorial, cluster-randomised, adaptive, etc.)
        - Describe the number of arms and provide a brief description of each arm.
        - Specify the hypothesis testing framework (e.g., superiority, non-inferiority, equivalence); where applicable, specify which comparisons will be based on which framework.
        - Include a description of blinding, specifying which members of the research team are blinded. Timing of when statisticians and other members of team will be unblinded should also be included. 
        - Do not include randomisation mechanics here.
        - Do not include details on the objectives of the study.
        - Write in paragrpahs using full sentences
        - Be concise.
        - Do not include any content outside of this field, provide only the content detailed above
        - Use only information about the trial from the protocol, do not invent information not present in the protocol.
        """,
        
        "{{allocation_ratio}}": """
        - Using the clinical trial protocol, extract the randomisation allocation ratio (e.g., 1:1, 2:1) and return it exactly as specified. 
        - Be concise, just give the ratio no other detilas. 
        - Do not invent information not present in the protocol.
        - Example: 1:1
        """,

        "{{randomization_level}}": """
        - Using the clinical trial protocol, extract the randomisation unit/level (e.g., participant, cluster/site) and return it exactly as specified. 
        - Be concise, just the level. 
        - Only include what belongs to this field. 
        - Do not invent information not present in the protocol.
        - Example for individually randomised trial: participant
        - Example for a cluster randomised trial: cluster
        - Example for a cluster randomised trial where the unit of randomisation are hopstials: hospital 
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
        - Example: two arms, beta blocker, placebo
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
        - Present as bullets in chronological order. 
        - Be concise. 
        - Do not invent information not present in the protocol.
        - Do not include details on visit windows.
        """,
        
        "{{visit_windows}}": """
        - Using the clinical trial protocol, describe the visit windows for assessments timepoints exactly as specified. 
        - Use sentences/lines or a compact list if the protocol lists discrete windows. 
        - If no visit windows are given state "visit windows not defined in protocol".
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


        "{{descriptive_concomitant_medications}}": """
        - Using only the clinical trial protocol, write a concise paragraph describing how concomitant medication data will be summarised for inclusion in the Statistical Analysis Plan (SAP).
        - Specify which concomitant medication variables will be summarised (e.g., any use, specific drug classes, prohibited or rescue medications, baseline vs on-treatment medications), and whether any coding system (e.g., ATC, WHO Drug) will be used, if stated in the protocol.
        - Describe how concomitant medications will be presented (e.g., counts and percentages by treatment arm, by medication class or specific agents, summaries of number of concomitant medications per participant), and indicate the time periods or timepoints over which these summaries will be made (e.g., baseline, during treatment, follow-up), as specified in the protocol.
        - If relevant, describe any planned distinction between allowed, prohibited, rescue, or protocol-defined concomitant medications and how these will be summarised.
        - Write the output as a single concise paragraph (no bullet points in the output itself), using the terminology from the protocol where possible.
        - Do not describe or propose any statistical tests; focus only on descriptive summaries of concomitant medication data.
        - Do not infer or invent concomitant medication variables, coding systems, time periods, or summary methods that are not explicitly reported in the protocol; if certain details are not specified, state briefly that these are not reported.
        """,

        "{{visit_window_deviation}}": """
        - Using only the clinical trial protocol, write a single short descriptive clause (not a full sentence) that can directly follow the words 'classified as protocol deviation as' in the SAP text.
        - The clause should describe how visit-window deviations will be handled or classified for reporting (e.g., within or outside pre-specified visit windows, minor vs major deviations, inclusion/exclusion from specific analyses), using the terminology from the protocol where possible.
        - Do not start the clause with a capital letter and do not end it with a full stop, so that it reads grammatically within the sentence: 'All visit window deviations will be classified as protocol deviation as {{visit_window_deviation}}.'
        - Be concise and keep the clause brief (no more than one short line of text).
        - Do not infer or invent any visit-window rules, classifications, or handling strategies that are not explicitly reported in the protocol.
        - If the protocol does not specify how visit-window deviations are handled or classified, return the clause: 'per the visit-window deviation rules specified in the protocol, which are not detailed here'
        """,

        "{{primary_estimand}}": """
        - Using only the clinical trial protocol, describe the primary estimand(s) in SAP-ready text.
        - If a single primary estimand is specified, begin with one short paragraph summarising it in words, then present its components under the five aspects: Population, Endpoint, Treatment condition, Intercurrent events, and Population-level summary.
        - If multiple primary estimands are defined, provide a brief introductory paragraph and then, for each estimand, give the five aspects clearly labelled so they can be placed under:
          • Population:
          • Endpoint:
          • Treatment condition:
          • Intercurrent events:
          • Population-level summary:
        - For the Population, describe the target population for the estimand as defined in the protocol (e.g., all randomised participants, all participants who received at least one dose, specific subgroups), using the protocol terminology.
        - For the Endpoint, state the outcome(s) and timepoint(s) relevant to the estimand, including any composite or derived measures, exactly as specified in the protocol.
        - For the Treatment condition, describe the treatment regimens or arms being contrasted (including dose, duration, and any relevant co-interventions) as they are defined for the estimand in the protocol.
        - For Intercurrent events, list the intercurrent events considered relevant to the estimand (e.g., treatment discontinuation, rescue medication, death, switch to alternative therapy) and, where stated, describe the handling strategy for each (e.g., treatment-policy, hypothetical, composite, while-on-treatment, principal stratum), using the protocol wording where possible and not inventing strategy labels.
        - For the Population-level summary, state the contrast or summary measure for the estimand (e.g., difference in means, ratio of means, risk difference, risk ratio, odds ratio, hazard ratio, difference in restricted mean survival time), and the time horizon or follow-up if specified.
        - Use clear prose and, where appropriate, bullet points so that the output can be placed directly under the headings given in the SAP template.
        - Do not introduce any additional estimands, populations, endpoints, intercurrent events, or population-level summaries beyond those explicitly described in the protocol.
        - Do not describe estimation methods, statistical models, or inference procedures here; focus only on defining the estimand(s).
        - Do not infer or invent any missing details; if one of the five aspects is not explicitly defined in the protocol, state briefly under that aspect that it is not clearly specified.
        """,

        "{{effect_size}}": """
        - Using only the clinical trial protocol, describe any additional effect sizes (beyond those implied by the primary estimand) that are planned to be reported in the Statistical Analysis Plan (SAP).
        - For each additional effect size, state what measure will be reported (e.g., risk difference, risk ratio, odds ratio, mean difference, standardised mean difference, hazard ratio, number needed to treat), the outcome(s) and timepoint(s) to which it applies, and the comparison (e.g., experimental vs control).
        - Briefly describe how each effect size will be obtained in words (e.g., derived from a specified model, based on proportions at a given timepoint, based on mean change from baseline), without giving mathematical formulae or performing any new calculations.
        - Write the output as one concise paragraph; if there are several distinct effect sizes, they may be listed in sentences within the same paragraph.
        - Do not provide any justification or interpretation of the effect sizes; only state what will be reported and how they will be calculated according to the protocol.
        - Do not infer or invent any effect sizes, outcomes, timepoints, or calculation methods that are not explicitly reported in the protocol; if no additional effect sizes are specified, write a single sentence: "No additional effect sizes beyond those used for the primary analysis are explicitly specified in the protocol."
        """,

        "{{confidence_interval_p_value}}": """
        - Using only the clinical trial protocol, state the nominal significance level (alpha) and the confidence interval level(s) that will be used for reporting treatment effects in the Statistical Analysis Plan (SAP).
        - Specify whether the significance level is one-sided or two-sided if this is stated in the protocol (if not mentioned then use two-sided), and indicate if different alpha levels or confidence interval levels are planned for different outcomes or analyses (e.g., primary vs secondary outcomes, interim analyses), as described in the protocol.
        - Write the output as a single concise sentence or short paragraph suitable for direct inclusion in the SAP (no bullet points in the output itself).
        - Do not include mathematical formulae or perform any new calculations; simply report the levels and types of p-values and confidence intervals as specified.
        - Do not infer or invent significance levels, sidedness, or confidence interval levels that are not explicitly reported in the protocol; if these details are not specified, state briefly that the nominal significance level and/or confidence interval level are not clearly specified in the protocol.
        """,
        
        "{{primary_analysis_model}}": """
        - Using only the extracted information from the clinical trial protocol, write a main analysis section for all primary and secondary utcomes (excluding health economic and cost-utility outcomes), suitable for inclusion in the Statistical Analysis Plan (SAP).
        - Begin by stating the analysis population for the primary and secondary outcomes exactly as defined in the protocol (e.g., ntention-to-treat (ITT), modified ITT, per-protocol, safety); do not describe or justify the population, just name it.
        - For the primary outcome(s), clearly describe the planned analysis model(s), including the outcome type, the regression or modelling approach (e.g., linear regression, logistic regression, Cox proportional hazards model, mixed-effects model, repeated-measures model), and how the treatment effect will be parameterised and presented (e.g., mean difference, odds ratio, risk atio, hazard ratio, with corresponding confidence intervals).
        - Specify any planned adjustment for baseline covariates, including stratification factors used in randomisation (if applicable) and aseline values of the outcome where stated; use the terminology and factor definitions from the protocol.
        - For secondary outcomes, describe the analysis models in a similar manner, grouping outcomes that are of the same type and will be analysed using the same model; explicitly state which outcomes are analysed with each model and how the treatment effect will be resented for each group of outcomes.
        - If different analysis populations are specified for some outcomes (e.g., safety outcomes, per-protocol analyses), state this riefly where relevant, using the protocol’s terminology.
        - Do not provide analysis methods for outcomes relating to health economics or cost-utility; if such outcomes are mentioned in the rotocol, state briefly that their analysis is described elsewhere.
        - Write the output as one or more concise paragraphs, without bullet points, with enough detail that the analysis could be implemented unambiguously (e.g., clearly identifying the outcome, treatment variable, covariates, and general model structure), but ithout mathematical formulae.
        - Do not introduce new analysis models, covariates, transformations, or populations beyond those explicitly described in the protocol; if important details (e.g., covariate adjustments or specific model forms) are not specified, state briefly that these are ot clearly specified in the protocol.
        - Be concise and focus only on the analysis models and covariate adjustments for the primary and secondary outcomes as described bove.
        """,

        
        "{{intercurrent_events_and_analysis}}": """
        - Using only the clinical trial protocol, describe the anticipated intercurrent events and any planned supplementary analyses using different strategies or estimands, for inclusion in the Statistical Analysis Plan (SAP).
        - List all anticipated intercurrent events that are explicitly mentioned in the protocol (e.g., treatment discontinuation, treatment switch, use of rescue medication, protocol-prohibited medication, withdrawal from follow-up, death), using the protocol’s terminology.
        - Where reported, state perceived or estimated rates of occurrence of each intercurrent event and, if described, any expected differences in rates between treatment arms and the reasons for these expectations.
        - If the protocol provides explanations of why particular events are considered intercurrent events, briefly summarise these explanations in short sentences.
        - Describe any supplementary analyses planned to address these intercurrent events (e.g., analyses using alternative strategies such as treatment-policy, hypothetical, composite, while-on-treatment, or principal stratum) and/or any analyses corresponding to different estimands, as outlined in the protocol, without introducing new strategies or estimands.
        - Write the output as concise prose; where the protocol lists intercurrent events or analyses as items, it is acceptable to present them as bullet points or short sentences mirroring that structure.
        - Do not describe or propose new intercurrent events, rates, handling strategies, or supplementary analyses that are not explicitly reported in the protocol; if no anticipated intercurrent events or related supplementary analyses are specified, write a single sentence stating that these are not explicitly specified in the protocol.
        """,


        "{{secondary_estimands}}": """
        - Using only the clinical trial protocol, describe estimands for secondary outcomes where these differ from the primary estimand, for inclusion in the Statistical Analysis Plan (SAP).
        - Identify secondary outcomes whose estimands differ from the primary estimand in any of the five aspects (Population, Endpoint, Treatment condition, Intercurrent events, Population-level summary), and summarise these differences clearly.
        - For each such secondary estimand, briefly describe in words: the target population, the endpoint and timepoint(s), the treatment condition(s) being compared, the handling of key intercurrent events (if specified), and the population-level summary measure.
        - Group secondary outcomes that share the same estimand structure, and state explicitly which outcomes follow each estimand where this is described in the protocol.
        - Write the output as one or more concise paragraphs (no bullet points in the output itself), using terminology from the protocol and from the primary estimand section where appropriate.
        - Do not introduce new estimands or modify aspects of the primary estimand unless such differences are explicitly stated or clearly implied in the protocol.
        - Do not infer or invent populations, endpoints, treatment conditions, intercurrent-event strategies, or summary measures that are not documented in the protocol; if no secondary estimands differing from the primary estimand are specified, write a single sentence stating that secondary outcomes are assumed to share the same estimand as the primary outcome unless otherwise specified.
        """,

        "{{secondary_analysis}}": """
        - Using only the clinical trial protocol, describe the planned analysis approach for secondary outcomes, for inclusion in the Statistical Analysis Plan (SAP), ensuring consistency with the defined secondary estimands.
        - Summarise the analysis models to be used for each group of secondary outcomes, specifying the outcome type, the model or method (e.g., linear regression, logistic regression, Cox proportional hazards model, mixed-effects model, repeated-measures model), and how treatment effects will be presented (e.g., mean differences, odds ratios, risk ratios, hazard ratios, with confidence intervals), as described in the protocol.
        - Identify groups of secondary outcomes that share the same model structure and covariate adjustments, and explicitly state which outcomes are analysed with each shared approach.
        - State any planned covariate adjustments for secondary outcomes, including stratification factors and baseline values of the outcome or other prognostic variables, using the terminology and factor definitions from the protocol.
        - If different analysis populations are specified for some secondary outcomes (e.g., safety or per-protocol analyses), briefly state these where relevant, without redefining them.
        - Write the output as one or more concise paragraphs (no bullet points in the output itself), providing sufficient detail for the analyses to be implemented unambiguously, but without mathematical formulae or new methods.
        - Do not introduce new models, covariates, transformations, or analysis populations beyond those explicitly described in the protocol; if the protocol does not clearly specify the analysis approach for certain secondary outcomes, state briefly that the analysis method for those outcomes is not clearly specified.
        """,

       
        "{{time_points}}": """
        - Using only the clinical trial protocol, describe how timepoints/time will be used in the analysis of the trial outcomes, for inclusion in the Statistical Analysis Plan (SAP).
        - State the analysis time points for each key outcome or group of outcomes (e.g., primary endpoint at 12 months, secondary endpoints at 6 and 12 months, repeated measures over all scheduled visits), as specified in the protocol.
        - Describe how time will enter the analysis models where relevant (e.g., as discrete visit factors, continuous time, follow-up duration in survival models, repeated-measures over visits), using the terminology from the protocol.
        - If visit windows are defined, state what data will be used when measurements fall within or outside the specified windows (e.g., closest measurement within the window, rules for assigning visits, handling of out-of-window data), as described in the protocol.
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Time points” section of the SAP.
        - Do not infer or invent timepoints, visit windows, or analysis-time structures that are not explicitly reported in the protocol; if details of how time or visit windows are handled are not specified, state briefly that these are not clearly specified in the protocol.
        """,


        "{{Stratification_and_clustering}}": """
        - Using only the clinical trial protocol, describe how stratification factors and any potential clustering will be accounted for in the analysis models, for inclusion in the Statistical Analysis Plan (SAP).
        - State whether stratified randomisation is used and, if so, identify the stratification factors and indicate that the primary (and, if specified, secondary) analysis models will adjust for these factors, using the terminology from the protocol.
        - If the trial has a clustered or multi-level design (e.g., cluster randomisation, repeated measures within centres, therapists, or practices), describe how clustering will be handled in the analysis (e.g., random effects/mixed models, generalised estimating equations with robust standard errors, cluster-level summaries), as specified in the protocol.
        - If both stratification and clustering are present, briefly explain how both will be incorporated into the analysis models (e.g., adjustment for stratification factors as fixed effects and inclusion of a random effect for cluster).
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Stratification and clustering” section of the SAP.
        - Do not infer or invent stratification factors, clustering structures, or modelling approaches that are not explicitly reported in the protocol; if stratification and/or clustering are used but their handling in the analysis is not specified, state briefly that the approach to accounting for these is not clearly specified in the protocol.
        """,


        
        "{{missing_items_in_scales}}": """
        - Using only the clinical trial protocol, write a concise paragraph describing how missing items within multi-item scales and subscales will be handled for inclusion in the Statistical Analysis Plan (SAP).
        - State whether the proportion of participants with complete data on each scale/subscale will be reported (e.g., number and percentage with complete responses), if this is specified in the protocol.
        - If the protocol provides scale-specific missing data guidance or scoring rules (e.g., from instrument manuals), briefly summarise these rules (such as allowable numbers/proportions of missing items and how scores are to be calculated) and refer to them in general terms rather than reproducing full scoring instructions.
        - If prorating or similar approaches are specified (e.g., replacing missing items based on averages of completed items when a certain percentage or number of items is missing), describe these rules clearly in words, including any thresholds for applying prorating, as stated in the protocol.
        - Make clear whether different scales/subscales use different missing-item rules, and, if so, summarise these differences briefly.
        - Write the output as a single concise paragraph (no bullet points in the output itself), using the terminology from the protocol where possible.
        - Do not infer or invent prorating rules, thresholds, or other missing-item handling procedures that are not explicitly described in the protocol; if the protocol does not specify how missing items within scales are handled, state briefly that the handling of missing items in scales/subscales is not clearly specified.
        """,


        "{{missing_baseline_data}}": """
        - Using only the clinical trial protocol, write a concise paragraph describing how missing baseline covariate data will be handled in analyses planned for the Statistical Analysis Plan (SAP).
        - State whether missing baseline data are expected to affect the primary analysis, and, if relevant, note that some extended or exploratory analyses may use additional baseline variables that could have missing values, as described in the protocol.
        - Describe how the extent of missing baseline data will be reported (e.g., number and percentage of participants with complete data for each baseline covariate), if this is specified.
        - Summarise the planned approach to handling missing baseline covariate data in the analysis (e.g., complete-case analysis, single imputation, multiple imputation, imputation “using a method suitable to the variable” per a named recommendation or reference), using the wording and references given in the protocol (such as White and Thompson) without adding new methods.
        - If different approaches are planned for different types of baseline variables (e.g., continuous vs categorical), briefly summarise these distinctions where specified.
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Missing baseline data” section of the SAP.
        - Do not infer or invent expectations about missingness, reporting methods, or imputation approaches that are not explicitly described in the protocol; if the handling of missing baseline data is not clearly specified, state this briefly.
        """,

        "{{missing_data_sensitivity_analysis}}": """
        - Using only the clinical trial protocol, write a concise paragraph outlining any planned sensitivity analyses for missing outcome data for inclusion in the Statistical Analysis Plan (SAP).
        - Describe which outcomes and timepoints the sensitivity analyses apply to and indicate which primary analysis they are intended to assess the robustness of (e.g., mixed-model analyses under a MAR assumption).
        - Summarise the general approach to each planned sensitivity analysis (e.g., alternative modelling assumptions, multiple imputation under different imputation models, pattern-mixture or selection models, delta-based or tipping-point analyses) and the underlying assumptions about the missing data mechanism (e.g., MAR vs MNAR), using the terminology from the protocol and without mathematical formulae.
        - If sensitivity analyses are planned specifically to examine scenarios where data may be missing not at random (MNAR), briefly describe the nature of these analyses and how they differ from the primary analysis, in general terms.
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Missing outcome data” section of the SAP.
        - Do not infer or invent additional sensitivity analyses, missing data mechanisms, or modelling strategies that are not explicitly described in the protocol; if no sensitivity analyses for missing outcome data are specified, write a single sentence stating that no such sensitivity analyses are explicitly specified in the protocol.
        """,

        "{{multiple_comparisons}}": """
        - Using only the clinical trial protocol, write a concise paragraph describing the planned approach to handling multiple comparisons/multiplicity for inclusion in the Statistical Analysis Plan (SAP).
        - State whether any formal adjustment for multiplicity will be applied, and if so, describe the method (e.g., Bonferroni, Holm, Hochberg, gatekeeping procedures, family-wise error control, false discovery rate) and the scope of outcomes or comparisons to which it applies (e.g., co-primary outcomes, key secondary outcomes, multiple treatment arm comparisons).
        - If no adjustment for multiple comparisons is planned, state this explicitly and, where described in the protocol, briefly summarise how results from multiple outcomes or comparisons are intended to be interpreted (e.g., separate interpretation of each secondary outcome, emphasis on estimation and confidence intervals rather than strict hypothesis testing).
        - If different multiplicity strategies are specified for different sets of outcomes (e.g., co-primary vs secondary outcomes, primary vs exploratory comparisons), summarise these distinctions clearly.
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Method for handling multiple comparisons/multiplicity” section of the SAP.
        - Do not infer or invent multiplicity adjustment methods, outcome groupings, or interpretative strategies that are not explicitly reported in the protocol; if the approach to multiplicity is not specified, write a single sentence stating that no explicit strategy for handling multiple comparisons is described in the protocol.
        """,

        "{{analysis_for_noncompliance}}": """
        - Using only the clinical trial protocol, write a concise paragraph describing any planned analyses to address non-compliance with the allocated treatment for inclusion in the Statistical Analysis Plan (SAP).
        - State whether a per-protocol, as-treated, complier-average causal effect (CACE), or other non-compliance–focused analysis is planned, and briefly describe the general approach in words (e.g., analysis restricted to participants meeting predefined adherence criteria, instrumental variable methods using randomisation as an instrument), as specified in the protocol.
        - Make clear which outcomes these non-compliance analyses will apply to (e.g., primary outcome only, primary and key secondary outcomes) and how their role is positioned relative to the primary intention-to-treat analysis (e.g., supplementary or sensitivity analyses).
        - If non-compliance thresholds or definitions (e.g., minimum dose, number of sessions, or proportion of medication taken) are specified, summarise these briefly using the protocol terminology.
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Method for handling non-compliance (per protocol/CACE analyses)” section of the SAP.
        - Do not infer or invent additional non-compliance analyses, definitions, thresholds, or modelling strategies that are not explicitly described in the protocol; if no specific analyses for non-compliance are planned, write a single sentence stating that no additional analyses addressing non-compliance are explicitly specified in the protocol.
        """,


        "{{model_assumption_checks}}": """
        - Using only the clinical trial protocol, write a concise paragraph describing the planned checks of model assumptions and any pre-specified remedies if assumptions are not met, for inclusion in the Statistical Analysis Plan (SAP).
        - Summarise which assumptions will be checked for the main analysis models (e.g., normality of residuals, homoscedasticity, linearity, proportional hazards, independence, appropriate link function) and how these will be assessed (e.g., residual plots, Q–Q plots, tests of proportional hazards), using the terminology from the protocol.
        - Where specified, describe planned actions if assumptions appear to be violated (e.g., data transformation, use of robust standard errors, alternative link functions or distributions, non-parametric methods, alternative time-to-event models), without introducing new methods.
        - If the protocol states that certain diagnostics will be performed when describing the data (e.g., checking normality of residuals, inspection for outliers), briefly include these as part of the assumption-checking description.
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Model assumption checks” section of the SAP.
        - Do not infer or invent additional assumptions, diagnostics, or remedial methods that are not explicitly reported in the protocol; if the protocol does not clearly specify model assumption checks or remedies, state briefly that these are not clearly specified.
        """,


        "{{other_sensitivity_analysis}}": """
        - Using only the clinical trial protocol, write a concise paragraph describing any planned sensitivity analyses beyond those specifically addressing missing data, for inclusion in the Statistical Analysis Plan (SAP).
        - For each planned sensitivity analysis, briefly state what is being varied or examined (e.g., alternative analysis populations, different covariate adjustment sets, alternative outcome definitions, alternative model specifications, different handling of protocol deviations or non-compliance) and why it is being done (e.g., to assess robustness of primary results to particular assumptions or design choices), using the protocol’s wording where possible.
        - Summarise the general analytical approach for each sensitivity analysis in words (e.g., repeating the primary analysis in the per-protocol population, re-estimating the model excluding specific subgroups, using an alternative link function or distribution), without giving mathematical formulae or introducing new methods.
        - Do not repeat sensitivity analyses that are solely concerned with missing outcome data if these are described elsewhere; focus on other types of sensitivity analyses.
        - Write the output as a single concise paragraph (no bullet points in the output itself), suitable for direct insertion under the “Sensitivity analyses” section of the SAP.
        - Do not infer or invent additional sensitivity analyses, rationales, or methods that are not explicitly reported in the protocol; if no additional sensitivity analyses beyond those for missing data are specified, write a single sentence stating that no further sensitivity analyses are explicitly specified in the protocol.
        """,


        "{{subgroup_analysis}}": """
        - Using only the clinical trial protocol, write a concise description of any planned subgroup analyses for inclusion in the Statistical Analysis Plan (SAP).
        - Identify all pre-specified subgroups (e.g., by age, sex, baseline severity, centre, biomarker status) and state clearly which outcomes they apply to, using the terminology from the protocol.
        - Describe how subgroup analyses will be implemented in brief, typically as interaction terms between treatment and subgroup variables within the main analysis model(s), or as separate models by subgroup if this is what the protocol specifies.
        - If the protocol comments on the purpose or interpretation of subgroup analyses (e.g., exploratory vs confirmatory), or on whether these are adjusted for multiplicity, summarise this briefly without adding new rationale.
        - Write the output as one short paragraph (no bullet points in the output itself), providing enough detail that the planned subgroup analyses could be implemented unambiguously.
        - If the protocol explicitly states that no subgroup analyses are planned, or if no subgroup analyses are described, return exactly the sentence: "No subgroup analysis will be conducted."
        - Do not infer or invent subgroup factors, outcomes, models, or interaction structures that are not explicitly reported in the protocol.
        """,

        
        "{{any_additional_exploratory_analysis}}": """
        - Using only the clinical trial protocol, write a concise description of any additional exploratory analyses planned for inclusion in the Statistical Analysis Plan (SAP).
        - For each exploratory analysis, briefly state the outcomes involved, the analysis population (e.g., ITT, per-protocol, specific subgroups), and the general form of the analysis model or method (e.g., regression model, correlation analysis, additional time-to-event analysis), using the terminology from the protocol.
        - Make clear that these analyses are exploratory and distinguish them from the primary and secondary analyses where this is indicated in the protocol.
        - Write the output as one short paragraph (no bullet points in the output itself), providing enough detail that the planned exploratory analyses could be implemented in general terms, but without mathematical formulae or introducing new methods.
        - If the protocol states that no exploratory analyses are planned, or if no exploratory analyses are described, return exactly the sentence: "No additional analysis will be conducted."
        - Do not infer or invent exploratory outcomes, populations, or analytical approaches that are not explicitly reported in the protocol.
        """,

        
        "{{any_exploratory_mediator_and_moderator_analysis}}": """
        - Using only the clinical trial protocol, write a concise description of any planned exploratory mediation or moderation analyses for inclusion in the Statistical Analysis Plan (SAP).
        - For each exploratory mediation analysis, briefly state the outcome(s), mediator(s), and the general analytical approach or model in words (e.g., regression-based mediation, longitudinal mediation), using the terminology from the protocol and without mathematical formulae.
        - For each exploratory moderation analysis, briefly state the outcome(s), moderator(s), and how moderation will be examined in general terms (e.g., inclusion of treatment-by-moderator interaction terms in the relevant model), as described in the protocol.
        - Make clear that these analyses are exploratory and, if stated in the protocol, note whether they are intended for the main statistical report/primary paper or for separate reporting/SAP.
        - Write the output as one short paragraph (no bullet points in the output itself), providing enough detail to convey the planned outcomes, mediators/moderators, and general model structure, but without introducing new methods.
        - If the protocol does not describe any exploratory mediation or moderation analyses, return exactly the sentence: "No exploratory mediation or moderation analyses are planned."
        - Do not infer or invent outcomes, mediators, moderators, or analytical approaches that are not explicitly reported in the protocol.
        """,

        
        "{{interim_analysis}}": """
        - Using only the extracted information from the clinical trial protocol, write a section on Interim Analysis and Internal Pilot for inclusion in the Statistical Analysis Plan (SAP).
        - First, clearly state whether any interim analysis and/or internal pilot phase is planned in the study.
        - If an interim analysis and/or internal pilot is planned, describe in concise prose:
          - the objectives and timing of the interim analysis or internal pilot (e.g., information fraction, calendar time, recruitment milestones, or follow-up duration),
          - the statistical methods and any stopping rules or decision criteria to be used (e.g., for efficacy, futility, or safety),
          - any adjustments to significance levels or sample size (e.g., alpha spending, group-sequential design, sample size re-estimation),
          - and, where specified, the roles and responsibilities of the Data Monitoring Committee or equivalent oversight body.
        - Write the output as one or more short paragraphs; do not use bullet points in the output itself unless the protocol presents key elements as a list that must be preserved.
        - If no interim analysis or internal pilot is planned, return exactly the sentence: "No interim analyses or internal pilot phases are planned, and no adjustments to significance levels will be made."
        - Do not infer or invent interim analyses, internal pilot phases, objectives, timings, stopping rules, or alpha/sample-size adjustments that are not explicitly reported in the protocol; if certain aspects are mentioned but not detailed (e.g., stopping boundaries), state briefly that further details are not specified in the protocol.
        """,

    }

PROMPTS = PROMPTS_TITLE_ADMIN | PROMPTS_INTRO_AND_DESIGN |PROMPTS_PEOPLE






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