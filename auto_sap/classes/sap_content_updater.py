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

Write 1-3 sentences describing when participants are assessed. Be concise and professional.
Output only the plain text, no JSON, no bullet points."""
        return self._get_response(prompt).strip()

    def _generate_outcomes_text(self, measures: list, timepoints: list) -> tuple[str, str]:
        timepoint_labels = {tp["value"]: tp["label"] for tp in timepoints}
        prompt = f"""Write descriptions of the primary and secondary outcome measures for a clinical trial SAP.

Outcome variables (in order — treat the first as the primary outcome):
{json.dumps(measures, indent=2)}

Timepoint reference (value → label):
{json.dumps(timepoint_labels, indent=2)}

Return a JSON object:
{{
  "primary_outcome_measures": "<description of the first/primary outcome>",
  "secondary_outcome_measures": "<description of remaining secondary outcomes>"
}}

Guidelines:
- For each outcome: mention its label, variable type, and the timepoints it is measured at (use labels not values)
- Be concise and professional
- If there is only one outcome, leave secondary_outcome_measures as an empty string
- Output ONLY the JSON object, no markdown"""

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
        prompt = f"""Write a description of the statistical analysis methods for a clinical trial SAP.

Planned analyses (method names resolved):
{json.dumps(enriched, indent=2)}

Write 2-5 sentences describing the statistical methods. Mention the methods used for each outcome,
the relevant timepoints, and any covariates. Be concise and professional.
Output only the plain text."""
        return self._get_response(prompt).strip()

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def update(self, existing_sap_json: dict = None) -> dict:
        """
        Fetch current trial data and regenerate the SAP content fields.

        Args:
            existing_sap_json: Existing SAP JSON dict. All other fields are
                               preserved; only the four content fields are updated.

        Returns:
            Updated SAP JSON dict.
        """
        print("Fetching trial data for SAP update...")
        timepoints = self.trial_manager.get_timepoints()
        measures = self.trial_manager.get_processed_measures()
        analyses = self.trial_manager.get_processed_analyses()
        methods = self.trial_manager.api.get_(endpoint="method")

        updated = dict(existing_sap_json) if existing_sap_json else {}

        print("Generating follow_up_timepoints...")
        updated["follow_up_timepoints"] = self._generate_timepoints_text(timepoints)

        print("Generating primary/secondary outcome measures...")
        primary, secondary = self._generate_outcomes_text(measures, timepoints)
        updated["primary_outcome_measures"] = primary
        updated["secondary_outcome_measures"] = secondary

        print("Generating analysis_methods...")
        updated["analysis_methods"] = self._generate_analysis_methods_text(analyses, methods)

        return updated

    def update_and_save(self, existing_sap_json: dict = None) -> dict:
        """Update SAP content fields and post the result back to the API."""
        updated = self.update(existing_sap_json)
        print("Saving updated SAP JSON to API...")
        self.trial_manager.add_sap_json(updated)
        return updated
