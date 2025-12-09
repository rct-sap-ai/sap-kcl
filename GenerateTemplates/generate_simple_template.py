from Classes.template_class import Template
from Classes.prompt_register_class import PromptRegister

from Prompts import prompts_06 as prompts_file

import time 

#reasoning_effort ="high", "medium", or "low", "minimal"
# verbosity = "high", "medium", or "low"
#PromptRegister(variable, prompt_function, reasoning_effort, verbosity)
prompt_tasks = [
    PromptRegister("title", "low","low"),
    PromptRegister("trial_acronym", "minimal","low"),
    PromptRegister("primary_outcome_measures", "medium","low"),
    PromptRegister("secondary_outcome_measures", "medium","low"),
    PromptRegister("timing_of_analysis", "low","low"),
    PromptRegister("primary_analysis_model", "minimal","low"),
    PromptRegister("secondary_analysis", "minimal","low"),
]


# Set up template with template file and prompts   
simple_template = Template(
    template_path = "Templates/sapai_kcl_template_v0.2_clean.docx", 
    system_message_function=prompts_file.system_message, 
    prompt_register=prompt_tasks,
    prompts_dictionary = prompts_file.PROMPTS_DICTIONARY,
    template_name = "simple test template", # this is identifying information that is recorded in the SAP
    prompts_name = "v6, 04/12/2025"
)
