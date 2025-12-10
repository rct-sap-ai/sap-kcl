from Classes.template_class import Template
from Classes.prompt_register_class import PromptRegister
from Classes.chat_classes import OpenAIChat
from Classes.auto_code_classes import run_autocode_with_conversation

from Prompts import prompts_06 as prompts_file

import time

# reasoning_effort = "high", "medium", "low", or "minimal"
# verbosity = "high", "medium", or "low"
# PromptRegister(variable, reasoning_effort, verbosity)
prompt_tasks = [
    PromptRegister("title", "low", "low"),
    PromptRegister("trial_acronym", "minimal", "low"),
    PromptRegister("primary_outcome_measures", "medium", "low"),
    PromptRegister("secondary_outcome_measures", "medium", "low"),
    PromptRegister("timing_of_analysis", "low", "low"),
    PromptRegister("primary_analysis_model", "minimal", "low"),
    PromptRegister("secondary_analysis", "minimal", "low"),
]

# Set up template with template file and prompts
simple_template = Template(
    template_path="Templates/sapai_kcl_template_v0.2_clean.docx",
    system_message_function=prompts_file.system_message,
    prompt_register=prompt_tasks,
    prompts_dictionary=prompts_file.PROMPTS_DICTIONARY,
    template_name="simple test template",  # identifying information that is recorded in the SAP
    prompts_name="v6, 04/12/2025",
)


# ----------------------------------------------------------------------
# Helper to run SAP generation from a protocol text
# ----------------------------------------------------------------------
def get_sap_content_for_protocol(protocol_txt: str, model: str = "gpt-5-nano"):
    """
    Convenience wrapper to populate the template using a protocol text.
    This calls Template.get_sap_content and stores the result in
    simple_template.sap_content.
    """
    simple_template.get_sap_content(protocol_txt, model=model)
    return simple_template


# ----------------------------------------------------------------------
# Build a content_dictionary for the autocode pipeline
# ----------------------------------------------------------------------
def build_autocode_content_dictionary_from_sap() -> dict[str, str]:
    """
    Build the content_dictionary expected by AutoCodePipeline / run_autocode_with_conversation.

    We know from inspection that:
      - simple_template.sap_content is a dict
      - keys like 'primary_outcome_measures', 'secondary_outcome_measures',
        'timing_of_analysis', 'primary_analysis_model', and 'secondary_analysis'
        are plain strings containing the generated SAP text.

    We map:
      - timepoint_content  <- timing_of_analysis
      - variables_content  <- primary_outcome_measures + secondary_outcome_measures
      - analysis_content   <- primary_analysis_model + secondary_analysis
    """

    sap_content = getattr(simple_template, "sap_content", {})

    # Fallback: if something changes and sap_content is not a dict, treat it as one big block
    if not isinstance(sap_content, dict):
        full_text = str(sap_content) if sap_content is not None else ""
        return {
            "timepoint_content": full_text,
            "variables_content": full_text,
            "analysis_content": full_text,
        }

    # TIMEPOINTS: timing_of_analysis
    timepoint_content = sap_content.get("timing_of_analysis", "")

    # VARIABLES: primary + secondary outcome measures
    variables_parts = [
        sap_content.get("primary_outcome_measures", ""),
        sap_content.get("secondary_outcome_measures", ""),
    ]
    variables_content = "\n\n".join([part for part in variables_parts if part])

    # ANALYSES: primary + secondary analysis sections
    analysis_parts = [
        sap_content.get("primary_analysis_model", ""),
        sap_content.get("secondary_analysis", ""),
    ]
    analysis_content = "\n\n".join([part for part in analysis_parts if part])

    return {
        "timepoint_content": timepoint_content,
        "variables_content": variables_content,
        "analysis_content": analysis_content,
    }


# ----------------------------------------------------------------------
# End-to-end helper returning an AutoCodeConversation
# ----------------------------------------------------------------------
def get_autocode_conversation_for_protocol(
    protocol_txt: str,
    model: str = "gpt-5-nano",
    validate: bool = False,
):
    """
    End-to-end helper that:
      1) runs the SAP generation for a given protocol text
      2) builds the autocode content_dictionary from the SAP text
      3) runs the AutoCodePipeline (via run_autocode_with_conversation)
      4) returns an AutoCodeConversation object for interactive editing

    Usage example:

        protocol = Protocol("Protocols/boppp.pdf")
        convo = get_autocode_conversation_for_protocol(protocol.protocol_txt)

        # initial JSON:
        convo.result["timepoints"]

        # user says: "no, you've added an extra timepoint at 6 months..."
        convo.apply_user_edit("timepoints", user_message)

        # final JSON:
        final_json = convo.result
    """

    # Step 1: populate the template from the protocol text
    get_sap_content_for_protocol(protocol_txt, model=model)

    # Step 2: build content dictionary from the relevant SAP sections
    content_dictionary = build_autocode_content_dictionary_from_sap()

    # Step 3: set up chat bot and run autocode pipeline with conversational wrapper
    chat_bot = OpenAIChat(model_name=model)
    convo = run_autocode_with_conversation(
        chat_bot=chat_bot,
        content_dictionary=content_dictionary,
        validate=validate,
    )

    return convo
