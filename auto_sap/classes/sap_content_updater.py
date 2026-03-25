import json

from auto_sap.classes.auto_code_api_classes import TrialCreator


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

    def _generate_timepoints_text(self, timepoints: list) -> str:
        prompt = f"""Write a brief description of the follow-up timepoints for a clinical trial SAP.

Timepoints (ordered):
{json.dumps(timepoints, indent=2)}

        - Using the above timepoints list, describe all follow-up time points at which outcomes are measured. 
        - Write in complete sentences, using the timepoint labels (not values).
        - Present each timepoint on a new line, in chronological order.
        - Do not use bullet points or dashes to introduce new lines. 
        - Do not add additional line breaks between timepoints
        - Be concise. 
        - Do not invent information not present in the protocol.
        - Do not include details on visit windows."""
        return self._get_response(prompt).strip()

    def _generate_outcomes_text(self, measures: list, timepoints: list) -> tuple[str, str]:
        timepoint_labels = {tp["value"]: tp["label"] for tp in timepoints}
        prompt = f"""Write descriptions of the primary and secondary outcome measures for a clinical trial SAP.

The following outcome variables have been extracted from the trial database (treat the first as the primary outcome):
{json.dumps(measures, indent=2)}

Timepoint reference (value → label):
{json.dumps(timepoint_labels, indent=2)}

Return a JSON object:
{{
  "primary_outcome_measures": "<description of the first/primary outcome>",
  "secondary_outcome_measures": "<description of remaining secondary outcomes>"
}}

Guidelines for primary_outcome_measures:
- For each primary outcome, write a single paragraph that includes: specification of the outcome (what is being measured), the variable type, and the timepoints at which it is measured (use timepoint labels, not values).
- For outcomes measured at multiple timepoints, clearly state which is the primary timepoint for the main analysis and note that other timepoints will be analysed as secondary outcomes.
- Do not mention assessments at baseline in the outcome description.
- Do not include any information about the analysis of the outcome.
- Be concise.

Guidelines for secondary_outcome_measures:
- For each secondary outcome, write a single paragraph that includes: specification of the outcome, the variable type, and the timepoints at which it is measured (use timepoint labels, not values).
- Write each outcome as a separate paragraph.
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
            m["id"]: m.get("title", m.get("slug", str(m["id"])))
            for m in methods
        }
        enriched = [
            {
                "outcome_variable": a["outcome_variable"],
                "timepoints": a["timepoints"],
                "method": method_lookup.get(a["method"], str(a["method"])),
                "covariates": a.get("covariates", []),
            }
            for a in analyses
        ]
        prompt = f"""Write a main analysis methods section for inclusion in a clinical trial Statistical Analysis Plan (SAP).

The following analyses have been extracted from the trial database:
{json.dumps(enriched, indent=2)}

Guidelines:
- For each outcome variable, describe the planned analysis model, including the modelling approach (e.g., linear regression, logistic regression, mixed-effects model) and how the treatment effect will be parameterised and presented (e.g., mean difference, odds ratio).
- Specify any planned adjustment for baseline covariates where listed in the data above.
- Write the output as one or more concise paragraphs, without bullet points.
- Do not introduce analysis models, covariates, or populations beyond those present in the data above.
- Be concise and use professional statistical terminology.
- Output only the plain text."""
        return self._get_response(prompt).strip()

    # ------------------------------------------------------------------ #
    # Public API — individual field updaters                              #
    # ------------------------------------------------------------------ #

    def update_follow_up_timepoints(self, sap_json: dict) -> dict:
        """Regenerate the follow_up_timepoints field in sap_json and return it."""
        timepoints = self.trial_manager.get_timepoints()
        print("Generating follow_up_timepoints...")
        sap_json["follow_up_timepoints"] = self._generate_timepoints_text(timepoints)
        return sap_json

    def update_primary_outcome_measures(self, sap_json: dict) -> dict:
        """Regenerate the primary_outcome_measures field in sap_json and return it."""
        timepoints = self.trial_manager.get_timepoints()
        measures = self.trial_manager.get_processed_measures()
        print("Generating primary_outcome_measures...")
        primary, _ = self._generate_outcomes_text(measures, timepoints)
        sap_json["primary_outcome_measures"] = primary
        return sap_json

    def update_secondary_outcome_measures(self, sap_json: dict) -> dict:
        """Regenerate the secondary_outcome_measures field in sap_json and return it."""
        timepoints = self.trial_manager.get_timepoints()
        measures = self.trial_manager.get_processed_measures()
        print("Generating secondary_outcome_measures...")
        _, secondary = self._generate_outcomes_text(measures, timepoints)
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

