from auto_sap.classes.template_class import Template
from auto_sap.classes.prompt_register_class import PromptRegister
from auto_sap.classes.chat_classes import OpenAIChat
from auto_sap.classes.auto_code_classes import run_autocode_with_conversation
from auto_sap.prompts import prompts_06 as prompts_file
from importlib.resources import files

prompt_tasks = [
    PromptRegister("title",                      "minimal", "low"),
    PromptRegister("trial_acronym",              "minimal", "low"),
    PromptRegister("primary_outcome_measures",   "minimal", "low"),
    PromptRegister("secondary_outcome_measures", "minimal", "low"),
    PromptRegister("timing_of_analysis",         "minimal", "low"),
    PromptRegister("primary_analysis_model",     "minimal", "low"),
    PromptRegister("secondary_analysis",         "minimal", "low"),
]

simple_template = Template(
    template_path=files("auto_sap").joinpath("templates/sapai_kcl_template_v0.2_clean.docx"),
    system_message_function=prompts_file.system_message,
    prompt_register=prompt_tasks,
    prompts_dictionary=prompts_file.PROMPTS_DICTIONARY,
    template_name="simple test template",
    prompts_name="v6, 04/12/2025",
)


def get_sap_content_for_protocol(protocol_txt, model="gpt-5-nano", api_key=None):
    simple_template.get_sap_content(protocol_txt, model=model, api_key=api_key)
    return simple_template


def build_autocode_content_dictionary_from_sap():
    sap_data = getattr(simple_template, "sap_content", "")
    if isinstance(sap_data, dict):
        def g(k): return sap_data.get(k, "") if isinstance(sap_data.get(k, ""), str) else ""
        return {
            "timepoint_content": "\n\n".join([g("primary_outcome_measures"), g("secondary_outcome_measures"), g("timing_of_analysis"), g("primary_analysis_model"), g("secondary_analysis")]),
            "variables_content": "\n\n".join([g("primary_outcome_measures"), g("secondary_outcome_measures"), g("primary_analysis_model"), g("secondary_analysis")]),
            "analysis_content":  "\n\n".join([g("primary_analysis_model"), g("secondary_analysis"), g("timing_of_analysis")]),
        }
    sap_text = sap_data if isinstance(sap_data, str) else str(sap_data)
    return {"timepoint_content": sap_text, "variables_content": sap_text, "analysis_content": sap_text}


def get_autocode_conversation_for_protocol(protocol_txt, model="gpt-5-nano", validate=False, api_key=None):
    get_sap_content_for_protocol(protocol_txt, model=model, api_key=api_key)
    content_dictionary = build_autocode_content_dictionary_from_sap()
    chat_bot = OpenAIChat(model_name=model, api_key=api_key)
    return run_autocode_with_conversation(
        chat_bot=chat_bot,
        content_dictionary=content_dictionary,
        validate=validate,
    )
