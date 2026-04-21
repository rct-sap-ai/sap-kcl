from turtle import pd
from typing import Any, Dict, List, Optional, Tuple
import json
import time
import pandas as pd
from altair import value


# ============================================================
# BASE PIPELINE
# ============================================================

class AutoCodePipeline:
    """Complete pipeline using SAP-derived content for each extraction step"""

    def __init__(self, chat_bot, validate: bool = False):
        self.timepoint_bot = TimepointExtractor(chat_bot)
        self.variable_bot = VariableExtractor(chat_bot)
        self.analysis_bot = AnalysisExtractor(chat_bot)
        self.validation_bot = ValidationBot(chat_bot)
        self.evaluator = ExtractionEvaluator()
        self.errors: List[Tuple[str, str]] = []
        self.validate = validate

    def extract_all(self, content_dictionary: Dict[str, str]) -> Dict[str, Any]:
        """Extract all data with validation - uses specific content for each step"""

        print("=" * 60)
        print("EXTRACTION PHASE")
        print("=" * 60)

        timepoint_content = content_dictionary.get("timepoint_content", "") or ""
        variables_content = content_dictionary.get("variables_content", "") or ""
        analysis_content = content_dictionary.get("analysis_content", "") or ""

        # This is used only for validation / metrics
        input_content = (
            (timepoint_content or "")
            + "\n\n"
            + (variables_content or "")
            + "\n\n"
            + (analysis_content or "")
        )

        # Step 1: Extract timepoints
        print("[1/3] Extracting timepoints...")
        timepoints, timepoint_error = self.timepoint_bot.extract_timepoints(timepoint_content)
        if timepoint_error:
            self.errors.append(("timepoints", timepoint_error))
            print(f"\n    💬 {timepoint_error}\n")

        # Step 2: Extract variables
        print("\n[2/3] Extracting variables...")
        variables, variable_error = self.variable_bot.extract_variables(variables_content, timepoints)
        if variable_error:
            self.errors.append(("variables", variable_error))
            print(f"\n    💬 {variable_error}\n")

        # Step 3: Extract analyses
        print("\n[3/3] Extracting analyses...")
        analyses, analysis_error = self.analysis_bot.extract_analyses(analysis_content, variables)
        if analysis_error:
            self.errors.append(("analyses", analysis_error))
            print(f"\n    💬 {analysis_error}\n")

        result: Dict[str, Any] = {
            "timepoints": timepoints,
            "variables": variables,
            "analyses": analyses,
        }

        # Check if everything failed
        if not timepoints and not variables and not analyses:
            print("\n" + "=" * 60)
            print("⚠️  EXTRACTION INCOMPLETE")
            print("=" * 60)
            print("\nI tried my best, but couldn't extract anything useful. This might happen if:")
            print("  - The document is not a Statistical Analysis Plan")
            print("  - The format is very unusual or non-standard")
            print("  - Key sections are missing or poorly labeled")
            return result

        # Step 4: Validation (optional)
        validation_result: Optional[Dict[str, Any]] = None
        if self.validate and (timepoints or variables or analyses):
            print("\n" + "=" * 60)
            print("VALIDATION PHASE")
            print("=" * 60)
            print("\nValidating extraction...")
            validation_result = self.validation_bot.validate_extraction(input_content, result)

            print(f"\n  Completeness: {validation_result.get('completeness_score', 0)}/10")
            print(f"  Accuracy: {validation_result.get('accuracy_score', 0)}/10")

            if validation_result.get('issues'):
                print(f"\n  Issues found:")
                for issue in validation_result['issues'][:5]:
                    print(f"    - {issue}")

            if validation_result.get('missing_elements'):
                print(f"\n  Missing elements:")
                for missing in validation_result['missing_elements'][:5]:
                    print(f"    - {missing}")

        # Step 5: Evaluate
        print("\n" + "=" * 60)
        print("EVALUATION")
        print("=" * 60)
        metrics = self.evaluator.evaluate(input_content, result, validation_result)

        print(f"\n  Items extracted:")
        print(f"    - Timepoints: {metrics['items_extracted']['timepoints']}")
        print(f"    - Variables: {metrics['items_extracted']['variables']}")
        print(f"    - Analyses: {metrics['items_extracted']['analyses']}")
        print(f"\n  Format valid: {metrics['format_valid']}")

        if metrics['issues']:
            print(f"\n  Format issues:")
            for issue in metrics['issues']:
                print(f"    - {issue}")

        # Metadata (minimal for now)
        result["metadata"] = {
            "extraction_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "validation_enabled": self.validate,
            "metrics": metrics,
            "errors": [{"type": t, "message": m} for t, m in self.errors],
        }

        if validation_result:
            result["metadata"]["validation"] = validation_result

        if self.errors:
            print("\n" + "=" * 60)
            print("⚠️  PARTIAL SUCCESS")
            print("=" * 60)
            print(
                f"\nI managed to extract some information, "
                f"but had trouble with {len(self.errors)} section(s)."
            )

        return result

    def save_to_json(self, data: Dict[str, Any], output_path: str):
        """Save extracted data to JSON file"""
        with open(output_path, "w") as f:
            json.dump(data, indent=2, fp=f)
        print(f"\n✓ Saved to {output_path}")


# ============================================================
# BASE EXTRACTOR
# ============================================================

class AutoCodeExtractor:
    """Base class for autoCode format extraction with retry logic"""

    def __init__(self, chat_bot, max_retries: int = 1):
        self.chat_bot = chat_bot
        self.max_retries = max_retries

    def get_response(self, prompt: str) -> str:
        instructions = (
            "You are a helpful assistant that extracts structured data from "
            "statistical analysis plans. Always respond with valid JSON only."
        )
        try:
            response = self.chat_bot.get_response(prompt=prompt, system_message=instructions)
        except Exception as e:
            print(f"An error occurred while getting response: {e}")
            response = {"content": ""}
        return response.get("content", "")


# ============================================================
# EXTRACTION BOTS
# ============================================================

class TimepointExtractor(AutoCodeExtractor):
    """Bot 1: Extract timepoints"""

    def get_content(self, sap_json: Dict[str, Any]) -> str:
        print("\n\nTimepoint content extraction")

        timepoint_content = (
            (sap_json.get("follow_up_timepoints", "") or "")
            + "\n"
            + (sap_json.get("primary_outcome_measures", "") or "")
            + "\n"
            + (sap_json.get("secondary_outcome_measures", "") or "")
        ).strip()

        if not timepoint_content:
            raise ValueError(
                "No timepoint content found. Expected at least one of: "
                "follow_up_timepoints, primary_outcome_measures, secondary_outcome_measures."
            )
        return timepoint_content

    def extract(self, sap_text: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Extract timepoints with retry logic using SAP-derived text"""

        print(f"    Using content: {len(sap_text):,} chars")

        prompt = f"""Extract all timepoints mentioned in this Statistical Analysis Plan.

SAP Text:
{sap_text}

Your task: Extract the timepoints from the follow_up_timepoints field.

Return a JSON array in this EXACT format:
[
  {{"value": 0, "label": "Baseline"}},
  {{"value": 1, "label": "6 months"}}
]

Rules:
- Always start with 0 = Baseline
- Order the timepoints in the order they occur with Baseline always first (value=0)
- eg. 0 = Baseline, 1 = 6 weeks, 2 = 2 months, 3 = 10 weeks, etc.
- label = exact description of timepoint. For post baseline timepoints, only include number and units (e.g., "6 months", "12 weeks"). 
- Do not state post-randomisation or similar.
- Include ALL timepoints you find
- Do not include any duplicate timepoints
- Output ONLY the JSON array, no explanation, no markdown
"""

        last_error = None
        for attempt in range(self.max_retries):
            response = self.get_response(prompt=prompt)

            if not response or response.strip() == "":
                last_error = "The AI returned an empty response"
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Empty response, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(2)
                    continue
                else:
                    print(f"    ✗ Failed: Empty response after {self.max_retries} attempts")
                    break

            # Clean response
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            try:
                timepoints = json.loads(cleaned)

                # Validate format
                if not isinstance(timepoints, list):
                    last_error = "Response was not a list format"
                    raise ValueError("Response is not a list")

                if len(timepoints) == 0:
                    last_error = "No timepoints found in the document"
                    print(f"    ⚠ Warning: AI found 0 timepoints")
                    return [], (
                        "Sorry, I couldn't find any timepoints mentioned. "
                        "The SAP or prompts might not clearly specify when measurements are taken."
                    )

                for tp in timepoints:
                    if not isinstance(tp, dict) or "value" not in tp or "label" not in tp:
                        last_error = "Timepoints were not in the correct format"
                        raise ValueError("Invalid timepoint format")

                print(f"    ✓ Extracted {len(timepoints)} timepoints")
                return timepoints, None

            except (json.JSONDecodeError, ValueError) as e:
                last_error = f"Could not parse the AI's response as valid JSON: {str(e)}"
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Parse error, retry {attempt + 1}/{self.max_retries}: {e}")
                    time.sleep(2)
                    continue
                else:
                    print(f"    ✗ Failed: {e}")
                    print(f"    Response preview: {cleaned[:300]}")
                    break

        # Fallback message
        error_msg = (
            f"Sorry friend, I tried {self.max_retries} times but couldn't extract timepoints. "
            f"{last_error if last_error else 'Unknown error'}."
        )
        return [], error_msg
    
    def validate(self, timepoints) -> list[str]:
        """
        Deterministic validator for extracted timepoints.

        Expected schema (per timepoint):
        {"value": int, "label": str}

        Additional invariant:
        - 'value' must be UNIQUE across the list (used as canonical identifier)

        Returns:
        List of error strings. Empty list => valid.
        """
        errors = []

        if not isinstance(timepoints, list):
            return ["timepoints is not a list"]

        seen_values = set()

        for i, item in enumerate(timepoints):
            if not isinstance(item, dict):
                errors.append(f"item {i} is not a dict")
                continue

            expected_keys = {"value", "label"}
            keys = set(item.keys())

            if keys != expected_keys:
                errors.append(f"item {i} has keys {keys} (expected exactly {expected_keys})")
                continue

            v = item.get("value", None)
            if value is None:
                raise ValueError("value is missing")


            if not isinstance(v, int):
                errors.append(f"item {i} value must be int (got {type(v).__name__})")
            else:
                if v in seen_values:
                    errors.append(f"duplicate timepoint value: {v} (item {i})")
                else:
                    seen_values.add(v)

            lab = item.get("label", None)
            if not isinstance(lab, str) or not lab.strip():
                errors.append(f"item {i} label must be a non-empty string")

        return errors 


class VariableExtractor(AutoCodeExtractor):
    """Bot 2: Extract variables"""

    def get_content(self, sap_json):
        variable_content = (
            (sap_json.get("primary_outcome_measures", "") or "")
            + "\n"
            + (sap_json.get("secondary_outcome_measures", "") or "")
            + "\n"
            + (sap_json.get("other_variables", "") or "")
        ).strip()

        if not variable_content:
            raise ValueError(
                "No variable content found. Expected at least one of: "
                "primary_outcome_measures, secondary_outcome_measures, other_variables."
            )
        



        return(variable_content)

    def extract(
        self, sap_text: str, timepoints: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Extract variables with retry logic using SAP-derived text"""

        print(f"    Using content: {len(sap_text):,} chars")

        timepoints_str = json.dumps(timepoints, indent=2) if timepoints else "[]"

        prompt = f"""Extract all outcome variables from this Statistical Analysis Plan.

        SAP Text:
        {sap_text}

        Available timepoints:
        {timepoints_str}

        Return a JSON array in this EXACT format:
        [
        {{
            "label": "Depression score (PHQ-9)",
            "variable": "phq9_total",
            "timepoints": [0, 1, 2],
            "variable_type": "Continuous",
            "primary_outcome": true
        }}
        ]



        Rules:
        - label = human readable description less than 80 characters.
        - variable = short lowercase variable name with underscores, no spaces. max 28 characters.
        - Use aberviations and acronyms to ensure variable is less than 28 characters.
        - timepoints = list of timepoint values from above
        - variable_type = one of: Continuous, Binary, Categorical, Count, Time to event
        - primary_outcome = true if this is the primary endpoint, false otherwise
        - Output ONLY the JSON array
        """

        for attempt in range(self.max_retries):
            response = self.get_response(prompt=prompt)

            # Clean response
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            errors = None
            try:
                variables = json.loads(cleaned)
            except json.JSONDecodeError as e:
                errors = f"Could not parse the AI's response as valid JSON: {str(e)}"
               
            if not errors:
                errors, warnings = self.validate(variables, timepoints)

            for w in warnings:
                print("Warning:", w)

            if errors:
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Error in response: {errors}, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(1)
                    continue
                else:
                    print(f"    ✗ Failed: {errors}")
                    error_msg = (
                        f"Sorry homie, I tried {self.max_retries} times but couldn't extract variables. \n {errors}."
                    )           
                    return [], errors
            else:
                return variables, None



        
    
    def validate(
        self,
        variables_input,
        timepoints_list,
    ) -> tuple[list[str], list[str]]:

        valid_timepoint_values = {
            tp["value"] for tp in timepoints_list
        }

        errors, warnings = self.validate_variables_list(
            variables_input,
            valid_timepoint_values,
        )

        return errors, warnings


    def validate_variables_list(
        self,
        variables_input: list | str,
        valid_timepoint_values: set[int],
    ) -> tuple[list[str], list[str]]:

        errors: list[str] = []
        warnings: list[str] = []

        variables, parse_errors = self._parse_variables(variables_input)
        if parse_errors:
            return parse_errors, []

        if not variables:
            return ["No variables found in variables list"], []

        seen_vars: set[str] = set()

        for i, item in enumerate(variables):
            item_errors, item_warnings = self._validate_variable_item(
                item,
                i,
                seen_vars,
                valid_timepoint_values,
            )
            errors.extend(item_errors)
            warnings.extend(item_warnings)

        return errors, warnings
    
    def _parse_variables(
        self,
        variables_input,
    ) -> tuple[list | None, list[str]]:

        if isinstance(variables_input, str):
            try:
                parsed = json.loads(variables_input)
            except (json.JSONDecodeError, ValueError) as e:
                return None, [f"Could not parse JSON: {str(e)}"]
        else:
            parsed = variables_input

        if not isinstance(parsed, list):
            return None, ["variables must be a list"]

        return parsed, []
    
    def _validate_variable_item(
        self,
        item,
        index: int,
        seen_vars: set[str],
        valid_timepoint_values: set[int],
    ) -> tuple[list[str], list[str]]:



        allowed_types = {
            "Continuous",
            "Binary",
            "Count",
            "Categorical",
            "Time to event",
        }

        expected_keys = {
            "variable",
            "label",
            "variable_type",
            "timepoints",
            "primary_outcome",
        }

        errors: list[str] = []
        warnings: list[str] = []

        if not isinstance(item, dict):
            return [f"variable item {index} is not a dict"], []

        if set(item.keys()) != expected_keys:
            return [
                f"variable item {index} must contain exactly {expected_keys}"
            ], []

        var = item["variable"]
        lab = item["label"]
        vtype = item["variable_type"]
        tps = item["timepoints"]

        if not isinstance(var, str) or not var.strip():
            errors.append(
                f"variable item {index} variable must be non empty string"
            )
        else:
            if len(var) > 28:
                errors.append(
                    f"variable  {lab} variable, '{var}' exceeds 28 chars"
                )
            if var in seen_vars:
                warnings.append(
                    f"duplicate variable name '{var}' (item {index})"
                )
            seen_vars.add(var)

        if not isinstance(lab, str) or not lab.strip():
            errors.append(
                f"variable item {index} label must be non empty string"
            )
        elif len(lab) > 80:
            warnings.append(
                f"variable item {index} label > 80 chars"
            )

        if vtype not in allowed_types:
            errors.append(
                f"variable item {index} variable_type must be one of "
                f"{sorted(allowed_types)}"
            )

        if not isinstance(tps, list) or not all(isinstance(x, int) for x in tps):
            errors.append(
                f"variable item {index} timepoints must be list[int]"
            )
        else:
            missing = [
                x for x in tps if x not in valid_timepoint_values
            ]
            if missing:
                errors.append(
                    f"variable item {index} references missing timepoints {missing}"
                )

        po = item.get("primary_outcome")
        if not isinstance(po, bool):
            errors.append(
                f"variable item {index} primary_outcome must be a bool"
            )

        return errors, warnings





class AnalysisExtractor(AutoCodeExtractor):
    """Bot 3: Extract analyses - loops through outcomes and uses AI to pick appropriate analyses"""

    def get_content(self, sap_json: Dict[str, Any]) -> str:
        """Extract relevant content for analysis extraction from SAP JSON"""
        print("\n\nAnalysis content extraction")

        analysis_content = (
            (sap_json.get("primary_analysis_model", "") or "")
            + "\n"
            + (sap_json.get("secondary_analysis", "") or "")
        ).strip()

        if not analysis_content:
            raise ValueError(
                "No analysis content found. Expected at least one of: "
                "statistical_analysis_plan, primary_outcome_measures, secondary_outcome_measures, analysis_methods."
            )

        return analysis_content

    def extract(
        self,
        sap_text: str,
        outcomes: List[Dict[str, Any]],
        timepoints: List[Dict[str, Any]],
        methods: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Extract analyses with retry logic using SAP-derived text.
        Loops through outcomes and uses AI to pick appropriate analysis methods.
        Always creates a descriptive analysis if timepoint=0 is present.

        Args:
            sap_text: SAP content for analysis extraction
            outcomes: List of outcome variables with timepoints
            timepoints: List of available timepoints
            methods: List of available analysis methods from API

        Returns:
            Tuple of (analysis_list, error_message)
        """
        print(f"    Using content: {len(sap_text):,} chars")

        # Build analysis list starting with baseline descriptives
        analysis_list = []

        # Find descriptive method ID for baseline
        descriptive_method_id = None
        for m in methods:
            if isinstance(m, dict):
                name = m.get("slug", "")
                if "descriptive" in name.lower():
                    descriptive_method_id = m.get("id") or m.get("method_id")
                    break

        if not descriptive_method_id:
            print("    ⚠ Warning: Could not find descriptive method in methods list")

        # Add baseline descriptive analysis for each outcome if timepoint 0 exists
        timepoint_values = {tp["value"] for tp in timepoints}
        if 0 in timepoint_values and descriptive_method_id:
            for outcome in outcomes:
                if 0 in outcome.get("timepoints", []):
                    analysis_list.append({
                        "outcome_variable": outcome["variable"],
                        "timepoints": [0],
                        "method": descriptive_method_id,
                        "covariates": [],
                    })
            print(f"    ✓ Added {len([a for a in analysis_list if 0 in a.get('timepoints', [])])} baseline descriptive analyses")

        # Now use AI to determine main analyses for each outcome
        outcomes_str = json.dumps(outcomes, indent=2)
        methods_str = json.dumps(methods, indent=2)

        prompt = f"""Extract the appropriate statistical analysis for each outcome variable from this Statistical Analysis Plan.

SAP Text:
{sap_text}

Available outcomes:
{outcomes_str}

Available analysis methods:
{methods_str}

Your task: For each outcome variable, determine the appropriate analysis method, timepoints, and covariates for the MAIN analysis.

Return a JSON array in this EXACT format:
[
  {{
    "outcome_variable": "phq9_total",
    "timepoints": [2,3,4],
    "method": "method_id_from_list",
    "covariates": ["age", "baseline_score"]
  }}
]

Rules:
- outcome_variable = must match "variable" field from outcomes list
- timepoints = list of integer values, include all post randomisation timepoints relevant for the main analysis of that outcome
- method = must be an "id" value from the available methods list
- covariates = list of variable name strings matching "variable" fields from the outcomes list; include only variables mentioned as covariates or adjustment variables in the SAP for that outcome; use an empty list [] if none are specified
- Choose the most appropriate statistical method based on:
  * variable_type (Continuous → linear/mixed model, Binary → logistic, etc.)
  * what the SAP describes for that outcome
  * standard practice for that outcome type
- Do NOT include baseline (timepoint 0) descriptive analyses - those are handled separately
- Include one main analysis per outcome variable
- Output ONLY the JSON array, no explanation
"""

        last_error = None
        for attempt in range(self.max_retries):
            response = self.get_response(prompt=prompt)

            if not response or response.strip() == "":
                last_error = "The AI returned an empty response"
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Empty response, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(2)
                    continue
                else:
                    print(f"    ✗ Failed: Empty response after {self.max_retries} attempts")
                    break

            # Clean response
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            try:
                ai_analyses = json.loads(cleaned)

                # Validate format
                if not isinstance(ai_analyses, list):
                    last_error = "Response was not a list format"
                    raise ValueError("Response is not a list")

                # Combine baseline descriptives with AI-generated analyses
                analysis_list.extend(ai_analyses)

                if len(analysis_list) == 0:
                    last_error = "No analyses generated"
                    print(f"    ⚠ Warning: No analyses were generated")
                    return [], (
                        "Sorry, I couldn't generate any analyses. "
                        "The analysis section might be missing or unclear."
                    )

                print(f"    ✓ Generated {len(analysis_list)} total analyses ({len(ai_analyses)} main + {len(analysis_list) - len(ai_analyses)} baseline)")
                return analysis_list, None

            except (json.JSONDecodeError, ValueError) as e:
                last_error = f"Could not parse the AI's response as valid JSON: {str(e)}"
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Parse error, retry {attempt + 1}/{self.max_retries}: {e}")
                    time.sleep(2)
                    continue
                else:
                    print(f"    ✗ Failed: {e}")
                    print(f"    Response preview: {cleaned[:300]}")
                    break

        # Fallback message
        error_msg = (
            f"Sorry friend, I tried {self.max_retries} times but couldn't extract analyses. "
            f"{last_error if last_error else 'Unknown error'}."
        )
        return analysis_list, error_msg  # Return whatever baseline analyses we managed to create

    def validate(
        self,
        analysis_list: List[Dict[str, Any]],
        outcomes: List[Dict[str, Any]],
        allowed_method_ids: set
    ) -> Tuple[List[str], List[str]]:
        """
        Deterministic validator for analyses.

        Expected schema (per analysis):
          {
            "outcome_variable": <str>,
            "timepoints": <list[int]>,
            "method": <method_id>,
            "covariates": <list[str]>,
          }

        Returns:
            Tuple of (errors, warnings) - both are lists of strings
        """
        errors = []
        warnings = []

        if not isinstance(analysis_list, list):
            return ["analysis_list is not a list"], []

        # Build outcome->timepoints mapping and set of valid variable names
        outcome_tp = {}
        valid_variables = set()
        for o in outcomes:
            v = o.get("variable")
            tps = o.get("timepoints")
            if isinstance(v, str) and isinstance(tps, list):
                outcome_tp[v] = set(tps)
                valid_variables.add(v)

        expected_keys = {"outcome_variable", "timepoints", "method", "covariates"}

        for i, a in enumerate(analysis_list):
            if not isinstance(a, dict):
                errors.append(f"analysis item {i} is not a dict")
                continue

            keys = set(a.keys())
            if keys != expected_keys:
                errors.append(f"analysis item {i} has keys {keys} (expected exactly {expected_keys})")
                continue

            ov = a.get("outcome_variable")
            tps = a.get("timepoints")
            mid = a.get("method")
            covs = a.get("covariates")

            # Validate outcome_variable
            if not isinstance(ov, str) or ov not in outcome_tp:
                errors.append(f"analysis item {i} outcome_variable '{ov}' not found in outcomes")
            else:
                # Validate timepoints for this outcome
                if not isinstance(tps, list):
                    errors.append(f"analysis item {i} timepoints must be a list")
                else:
                    for tp in tps:
                        if not isinstance(tp, int):
                            errors.append(f"analysis item {i} timepoints must contain integers, found {type(tp).__name__}")
                            break
                        if tp not in outcome_tp[ov]:
                            errors.append(
                                f"analysis item {i} timepoint {tp} not valid for outcome '{ov}' "
                                f"(allowed {sorted(outcome_tp[ov])})"
                            )

            # Validate method
            if mid not in allowed_method_ids:
                print(f"*******checking if {mid} is in {allowed_method_ids}")
                errors.append(f"analysis item {i} method '{mid}' not in allowed methods from API")

            # Validate covariates
            if not isinstance(covs, list):
                errors.append(f"analysis item {i} covariates must be a list")
            else:
                for cov in covs:
                    if not isinstance(cov, str):
                        errors.append(f"analysis item {i} covariates must contain strings, found {type(cov).__name__}")
                        break
                    if cov not in valid_variables:
                        errors.append(f"analysis item {i} covariate '{cov}' not found in outcomes")


        # Check for missing baseline descriptives
        baseline_outcomes = {o["variable"] for o in outcomes if 0 in o.get("timepoints", [])}
        baseline_analyses = {a["outcome_variable"] for a in analysis_list if 0 in a.get("timepoints", [])}
        missing_baseline = baseline_outcomes - baseline_analyses
        if missing_baseline:
            warnings.append(
                f"Missing baseline descriptive analyses for: {', '.join(sorted(missing_baseline))}"
            )

        return errors, warnings


# ============================================================
# VALIDATION BOT
# ============================================================

class ValidationBot(AutoCodeExtractor):
    """Validates extracted data against the SAP"""

    def validate_extraction(self, sap_text: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the complete extraction"""

        sap_excerpt = sap_text[:1000000]
        print(f"    Using excerpt for validation: {len(sap_excerpt):,} chars")

        prompt = f"""Review this extracted data against the Statistical Analysis Plan.

SAP Text (excerpt):
{sap_excerpt}

Extracted Data:
{json.dumps(extracted_data, indent=2)}

Return ONLY a JSON object:
{{
  "completeness_score": 8,
  "accuracy_score": 9,
  "issues": ["list any problems"],
  "missing_elements": ["list missing items"],
  "suggestions": ["improvement suggestions"]
}}

Scores are 0-10 (10 = perfect). Output ONLY JSON.
"""

        response = self.get_response(prompt=prompt)

        if not response:
            return {
                "completeness_score": 0,
                "accuracy_score": 0,
                "issues": ["Validation failed: no response"],
                "missing_elements": [],
                "suggestions": [],
            }

        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            validation = json.loads(cleaned)
            return validation
        except json.JSONDecodeError as e:
            return {
                "completeness_score": 0,
                "accuracy_score": 0,
                "issues": [f"Validation parse error: {e}"],
                "missing_elements": [],
                "suggestions": [],
            }


# ============================================================
# EVALUATION
# ============================================================

class ExtractionEvaluator:
    """Evaluate extraction quality with metrics"""

    @staticmethod
    def evaluate(
        sap_text: str, extracted_data: Dict[str, Any], validation_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate metrics for the extraction"""

        metrics: Dict[str, Any] = {
            "items_extracted": {
                "timepoints": len(extracted_data.get("timepoints", [])),
                "variables": len(extracted_data.get("variables", [])),
                "analyses": len(extracted_data.get("analyses", [])),
            },
            "format_valid": True,
            "issues": [],
        }

        try:
            timepoints = extracted_data.get("timepoints", [])
            if timepoints:
                values = [tp["value"] for tp in timepoints]
                # They don't *have* to be sequential, but it's a nice check
                if sorted(values) != values:
                    metrics["issues"].append("Timepoint values not sorted ascending")

            variables = extracted_data.get("variables", [])
            valid_timepoint_values = {tp["value"] for tp in timepoints}
            for var in variables:
                for tp_val in var.get("timepoints", []):
                    if tp_val not in valid_timepoint_values:
                        metrics["issues"].append(
                            f"Variable '{var['variable_name']}' references invalid timepoint {tp_val}"
                        )

            analyses = extracted_data.get("analyses", [])
            valid_var_names = {var["variable_name"] for var in variables}
            for analysis in analyses:
                if analysis["outcome"] not in valid_var_names:
                    metrics["issues"].append(
                        f"Analysis '{analysis['name']}' references invalid variable '{analysis['outcome']}'"
                    )

        except Exception as e:
            metrics["format_valid"] = False
            metrics["issues"].append(f"Format validation error: {e}")

        if validation_result:
            metrics["validation"] = {
                "completeness_score": validation_result.get("completeness_score", 0),
                "accuracy_score": validation_result.get("accuracy_score", 0),
                "llm_issues": validation_result.get("issues", []),
                "missing_elements": validation_result.get("missing_elements", []),
            }

        return metrics


# ============================================================
# CONVERSATIONAL WRAPPER
# ============================================================

class AutoCodeConversation:
    """
    Wraps an AutoCodePipeline result and allows conversational edits
    to timepoints / variables / analyses.
    """

    def __init__(
        self,
        chat_bot,
        pipeline: AutoCodePipeline,
        content_dictionary: Dict[str, str],
        initial_result: Dict[str, Any],
    ):
        self.chat_bot = chat_bot
        self.pipeline = pipeline
        self.content_dictionary = content_dictionary
        self.result: Dict[str, Any] = initial_result
        self.history: List[Dict[str, str]] = []  # simple text history

    # ---------------------------- internal helpers ----------------------------

    def _edit_section_with_llm(self, section_name: str, user_message: str) -> Any:
        """
        Ask the model to edit the JSON for a single section (timepoints/variables/analyses)
        based on a free-text user request.
        """

        current_section = self.result.get(section_name, [])
        current_json = json.dumps(current_section, indent=2)

        system_message = (
            "You are helping a statistician edit a structured JSON representation of a "
            "Statistical Analysis Plan. You MUST:\n"
            "- Respect the JSON schema already in use for that section.\n"
            "- Keep field names identical.\n"
            "- Only modify what the user asks you to change.\n"
            "- Return ONLY valid JSON (no comments, no markdown).\n"
        )

        prompt = f"""We are editing the '{section_name}' section.

Current JSON for {section_name}:
{current_json}

User request:
\"\"\"{user_message}\"\"\"


Update ONLY the JSON for this section to satisfy the user's request.
Return ONLY the updated JSON (no explanation, no markdown)."""

        try:
            response = self.chat_bot.get_response(prompt=prompt, system_message=system_message)
            raw = (response.get("content", "") or "").strip()
        except Exception as e:
            print(f"Edit error for section '{section_name}': {e}")
            return current_section

        # Clean potential fences
        cleaned = raw
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            updated_section = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"⚠ Failed to parse edited JSON for {section_name}: {e}")
            print(f"   Raw response (first 300 chars): {cleaned[:300]}")
            return current_section

        return updated_section

    def _infer_section_from_message(self, user_message: str) -> str:
        """
        Very simple heuristic to decide which section the user is referring to.
        """

        text = user_message.lower()

        # Obvious keywords
        if any(k in text for k in ["timepoint", "time point", "month", "visit", "follow-up", "follow up"]):
            return "timepoints"
        if any(k in text for k in ["variable", "outcome", "endpoint", "measure"]):
            return "variables"
        if any(k in text for k in ["analysis", "model", "cox", "ancova", "mixed model", "regression"]):
            return "analyses"

        # Fallback: if they mention '6 months', '12 months', etc, assume timepoints
        if any(m in text for m in ["6 months", "12 months", "18 months", "24 months", "30 months", "36 months"]):
            return "timepoints"

        # Default to timepoints (safest for manual tweaking)
        return "timepoints"

    # ---------------------------- public API ----------------------------------

    def apply_user_edit(self, section_name: str, user_message: str) -> Dict[str, Any]:
        """
        Explicitly edit one section based on a free-text instruction.
        section_name ∈ {"timepoints", "variables", "analyses"}.
        Returns the full updated result dict.
        """
        if section_name not in {"timepoints", "variables", "analyses"}:
            raise ValueError(f"Unknown section_name '{section_name}'")

        updated = self._edit_section_with_llm(section_name, user_message)
        self.result[section_name] = updated

        # Log to simple history
        self.history.append(
            {
                "role": "user",
                "section": section_name,
                "message": user_message,
            }
        )
        self.history.append(
            {
                "role": "assistant",
                "section": section_name,
                "message": f"Updated {section_name} JSON.",
            }
        )

        return self.result

    def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Chatty interface: infer which section the user is talking about,
        apply the edit, return updated result.
        """
        section = self._infer_section_from_message(user_message)
        print(f"(AutoCodeConversation) Interpreting this as an edit to '{section}'")
        return self.apply_user_edit(section, user_message)


# ============================================================
# CONVENIENCE ENTRY POINT
# ============================================================

def run_autocode_with_conversation(
    chat_bot,
    content_dictionary: Dict[str, str],
    validate: bool = False,
) -> AutoCodeConversation:
    """
    Convenience function that:
      1) Runs the AutoCodePipeline on content_dictionary
      2) Wraps the result in an AutoCodeConversation
      3) Returns the conversation object for interactive editing
    """
    pipeline = AutoCodePipeline(chat_bot=chat_bot, validate=validate)
    result = pipeline.extract_all(content_dictionary)
    convo = AutoCodeConversation(
        chat_bot=chat_bot,
        pipeline=pipeline,
        content_dictionary=content_dictionary,
        initial_result=result,
    )
    return convo
