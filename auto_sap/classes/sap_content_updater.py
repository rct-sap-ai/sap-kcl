import json

from auto_sap.classes.auto_code_api_classes import TrialCreator
from auto_sap.classes.auto_code_classes import TimepointExtractor, VariableExtractor


class SAPContentUpdater:
    """
    Generates/updates SAP JSON text content fields from TrialManager's structured data.

    Fetches the current timepoints, outcome variables, and analyses from the API,
    then uses an LLM to write/refresh the following SAP content fields:
        - follow_up_timepoints
        - primary_outcome_measures
        - secondary_outcome_measures
        - analysis_methods

    Usage:
        updater = SAPContentUpdater(trial_manager, chat_bot)
        updated_sap = updater.update(existing_sap_json)
        # or to fetch + save in one step:
        updated_sap = updater.update_and_save(existing_sap_json)
    """

    def __init__(self, trial_manager: TrialCreator, chat_bot):
        self.trial_manager = trial_manager
        self.chat_bot = chat_bot
        self._timepoint_extractor = TimepointExtractor(chat_bot)
        self._variable_extractor = VariableExtractor(chat_bot)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _get_response(self, prompt: str) -> str:
        instructions = (
            "You are a helpful assistant that writes content for statistical analysis plans. "
            "Write clear, concise, professional text based on the structured data provided."
        )
        try:
            response = self.chat_bot.get_response(prompt=prompt, system_message=instructions)
        except Exception as e:
            print(f"LLM error: {e}")
            response = {"content": ""}
        return response.get("content", "")

    def _generate_timepoints_text(self, timepoints: list, existing_content: str) -> str:
        existing_section = (
            f"\nExisting SAP text (use for additional context on timepoint descriptions):\n{existing_content}\n"
            if existing_content else ""
        )
        prompt = f"""Write a brief description of the follow-up timepoints for a clinical trial SAP.

# Timepoint List (ordered) - this is the source of truth for which timepoints are included.:
{json.dumps(timepoints, indent=2)}

# Protocol based timepoint descriptions (if available, use these to enrich the descriptions of the timepoints above):
{existing_section}

# Instructions
        - For each timepoint in the Timpoint list above, write a concise description of the timepoint. Place each timepoint description on a new line, in the same order as the timepoints are listed above.
        - Write in complete sentences and give full descriptions of each timepoint using the provided protocol-based descriptions as additional context where available.
        - Do not use bullet points or dashes to introduce new lines.
        - Do not add additional line breaks between timepoints
        - Be concise.
        - Do not invent information not present in the data provided.
        - Do not include details on visit windows."""
        return self._get_response(prompt).strip()

    def _generate_outcomes_text(self, measures: list, timepoints: list, existing_content: str) -> tuple[str, str]:
        timepoint_labels = {tp["value"]: tp["label"] for tp in timepoints}
        existing_section = (
            f"\nExisting SAP text (use as the source of truth for which outcomes are primary and which are secondary):\n{existing_content}\n"
            if existing_content else ""
        )
        prompt = f"""Write descriptions of the primary and secondary outcome measures for a clinical trial SAP.

The following outcome variables have been extracted from the trial database and should be used as the source of truth.:
{json.dumps(measures, indent=2)}

Timepoint reference (value → label):
{json.dumps(timepoint_labels, indent=2)}


This text is extracted from the protocol and should be used for additional context on the outcome measures, but the database list above is the source of truth for which outcomes are included and which is primary vs secondary:
{existing_section}
Return a JSON object:
{{
  "primary_outcome_measures": "<description of the primary outcome(s)>",
  "secondary_outcome_measures": "<description of the secondary outcomes>"
}}

Guidelines for primary_outcome_measures:
- Use the `primary_outcome` field on each outcome object to determine which are primary and which are secondary. If the field is absent, fall back to the existing SAP text, or treat the first outcome in the database list as primary.
- For each primary outcome, write a single paragraph that includes: specification of the outcome (what is being measured), the variable type, and the timepoint for which the primary outcome is defined, naming the timpepoint wiht its label.
- Use the additional information to provide a richer description of the outcome measure, but do not contradict the database list above in terms of which outcomes are included. Where it is not obvious, include the label in brackets after defining the outcome.
- For outcomes measured at multiple timepoints, only describe the primary outcome timepoint in the primary outcome section; describe additional timepoints for that outcome in the secondary outcome section.
- Do not mention assessments at baseline in the outcome description.
- Do not include any information about the analysis of the outcome.
- Be concise.

Guidelines for secondary_outcome_measures:
- For each secondary outcome, write a single paragraph that includes: specification of the outcome, the variable type, and the timepoints at which it is measured (use timepoint labels, not values).
- Write each outcome as a separate paragraph.
- Use the additional information to provide a richer description of the outcome measure, but do not contradict the database list above in terms of which outcomes are included. Where it is not obvious, include the label in brackets after defining the outcome.
- Do not mention assessments at baseline in the outcome description.
- Do not include any information about the analysis of the outcome.
- Be concise.
- If there is only one outcome in total, leave secondary_outcome_measures as an empty string.

Output ONLY the JSON object, no markdown."""

        response = self._get_response(prompt).strip()
        cleaned = response
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            return (
                parsed.get("primary_outcome_measures", ""),
                parsed.get("secondary_outcome_measures", ""),
            )
        except json.JSONDecodeError:
            return response, ""

    def _generate_analysis_methods_text(self, analyses: list, methods: list) -> str:
        method_lookup = {
            m["id"]: {"title": m.get("title", str(m["id"])), "description": m.get("description", "")}
            for m in methods
        }
        enriched = [
            {
                "outcome_label": a["label"],
                "timepoints": a["timepoints"],
                "method": method_lookup.get(a["method"], {}).get("title", str(a["method"])),
                "method_description": method_lookup.get(a["method"], {}).get("description", ""),
                "covariates": a.get("covariates", []),
            }
            for a in analyses
        ]
        prompt = f"""Write a main analysis methods section for inclusion in a clinical trial Statistical Analysis Plan (SAP).

The following analyses have been extracted from the trial database:
{json.dumps(enriched, indent=2)}

Guidelines:
- For each outcome variable, describe the planned analysis model, including the modelling approach (e.g., linear regression, logistic regression, mixed-effects model).
- Where outcomes are analysed using the same method, group them together in the description to avoid repetition. Begin the descirption with an explicit list of the outcoes to be analysed at that timepoint using outome labels and timepoint labels.
- If not empty, base the description on the description field of the method. Populate any details in {} with relevant information. Edit as required so it reads well and is concise, but do not remove any details that are present in the method description.
- Specify any planned adjustment for baseline covariates where listed in the data above.
- Write the output as one or more concise paragraphs, without bullet points.
- Do not introduce analysis models, covariates, or populations beyond those present in the data above.
- Be concise and use professional statistical terminology.
- Only use outcome or covariate labels. do not use variable names from the database in the text
- Output only the plain text."""
        return self._get_response(prompt).strip()

    # ------------------------------------------------------------------ #
    # Public API — individual field updaters                              #
    # ------------------------------------------------------------------ #

    def _get_timepoint_content(self, sap_json: dict) -> str:
        try:
            return self._timepoint_extractor.get_content(sap_json)
        except ValueError:
            return ""

    def _get_variable_content(self, sap_json: dict) -> str:
        try:
            return self._variable_extractor.get_content(sap_json)
        except ValueError:
            return ""

    def update_follow_up_timepoints(self, sap_json: dict) -> dict:
        """Regenerate the follow_up_timepoints field in sap_json and return it."""
        timepoints = self.trial_manager.get_timepoints()
        existing_content = self._get_timepoint_content(sap_json)
        print("Generating follow_up_timepoints...")
        sap_json["follow_up_timepoints"] = self._generate_timepoints_text(timepoints, existing_content)
        return sap_json

    def update_primary_outcome_measures(self, sap_json: dict) -> dict:
        """Regenerate the primary_outcome_measures field in sap_json and return it."""
        timepoints = self.trial_manager.get_timepoints()
        measures = self.trial_manager.get_processed_measures()
        existing_content = self._get_variable_content(sap_json)
        print("Generating primary_outcome_measures...")
        primary, _ = self._generate_outcomes_text(measures, timepoints, existing_content)
        sap_json["primary_outcome_measures"] = primary
        return sap_json

    def update_secondary_outcome_measures(self, sap_json: dict) -> dict:
        """Regenerate the secondary_outcome_measures field in sap_json and return it."""
        timepoints = self.trial_manager.get_timepoints()
        measures = self.trial_manager.get_processed_measures()
        existing_content = self._get_variable_content(sap_json)
        print("Generating secondary_outcome_measures...")
        _, secondary = self._generate_outcomes_text(measures, timepoints, existing_content)
        sap_json["secondary_outcome_measures"] = secondary
        return sap_json

    def update_analysis_methods(self, sap_json: dict) -> dict:
        """Regenerate the analysis_methods field in sap_json and return it."""
        analyses = self.trial_manager.get_processed_analyses()
        methods = self.trial_manager.api.get_(endpoint="method")
        print("Generating analysis_methods...")
        sap_json["analysis_methods"] = self._generate_analysis_methods_text(analyses, methods)
        return sap_json

    # ------------------------------------------------------------------ #
    # Public API — bulk updaters                                          #
    # ------------------------------------------------------------------ #

    def update(self, existing_sap_json: dict | None = None) -> dict:
        """
        Fetch current trial data and regenerate all SAP content fields.

        Args:
            existing_sap_json: Existing SAP JSON dict. All other fields are
                               preserved; only the four content fields are updated.

        Returns:
            Updated SAP JSON dict.
        """
        updated = dict(existing_sap_json) if existing_sap_json else {}
        self.update_follow_up_timepoints(updated)
        self.update_primary_outcome_measures(updated)
        self.update_secondary_outcome_measures(updated)
        self.update_analysis_methods(updated)
        return updated

