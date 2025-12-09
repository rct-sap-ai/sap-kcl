from typing import Any
import json
import time


class AutoCodePipeline:
    """Complete pipeline using full document for each extraction step"""

    def __init__(self, chat_bot, validate = False):
        self.timepoint_bot = TimepointExtractor(chat_bot)
        self.variable_bot = VariableExtractor(chat_bot)
        self.analysis_bot = AnalysisExtractor(chat_bot)
        self.validation_bot = ValidationBot(chat_bot)
        self.evaluator = ExtractionEvaluator()
        self.errors: list[tuple[str, str]] = []
        self.validate = validate

    def extract_all(self, content_dictionary: dict) -> dict[str, Any]:
        """Extract all data with validation - uses FULL document for each step"""

        print("=" * 60)
        print("EXTRACTION PHASE")
        print("=" * 60)

        timepoint_content = content_dictionary.get("timepoint_content", "")
        variables_content = content_dictionary.get("variables_content", "")
        analysis_content = content_dictionary.get("analysis_content", "")

        input_content = timepoint_content + variables_content +  analysis_content

        # Step 1: Extract timepoints from FULL document
        print("[1/3] Extracting timepoints...")
        timepoints, timepoint_error = self.timepoint_bot.extract_timepoints(timepoint_content)
        if timepoint_error:
            self.errors.append(("timepoints", timepoint_error))
            print(f"\n    💬 {timepoint_error}\n")


        # Step 2: Extract variables from FULL document
        print("\n[2/3] Extracting variables...")
        variables, variable_error = self.variable_bot.extract_variables(variables_content, timepoints)
        if variable_error:
            self.errors.append(("variables", variable_error))
            print(f"\n    💬 {variable_error}\n")


        # Step 3: Extract analyses from FULL document
        print("\n[3/3] Extracting analyses...")
        analyses, analysis_error = self.analysis_bot.extract_analyses(analysis_content, variables)
        if analysis_error:
            self.errors.append(("analyses", analysis_error))
            print(f"\n    💬 {analysis_error}\n")

        result = {
            "timepoints": timepoints,
            "variables": variables,
            "analyses": analyses
        }

        # Check if everything failed
        if not timepoints and not variables and not analyses:
            print("\n" + "=" * 60)
            print("⚠️  EXTRACTION INCOMPLETE")
            print("=" * 60)
            print("\nI tried my best using the FULL document, but couldn't extract")
            print("anything useful. This might happen if:")
            print("  - The document is not a Statistical Analysis Plan")
            print("  - The format is very unusual or non-standard")
            print("  - Key sections are missing or poorly labeled")
            print("\nYou might want to:")
            print("  - Check that you uploaded the right document")
            print("  - Try a different document format")
            print("  - Contact support if this keeps happening")
            return None

        # Step 4: Validate
        validation_result = None
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

        # Add metadata
        result['metadata'] = {
            "extraction_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            # "model_used": Config.MODEL,
            # "document_size_chars": len(sap_text),
            # "truncation_used": False,
            # "validation_enabled": Config.ENABLE_VALIDATION,
            # "metrics": metrics,
            # "api_calls": (
            #     self.timepoint_bot.call_count
            #     + self.variable_bot.call_count
            #     + self.analysis_bot.call_count
            #     + self.validation_bot.call_count
            # ),
            # "total_tokens_used": (
            #     self.timepoint_bot.total_tokens
            #     + self.variable_bot.total_tokens
            #     + self.analysis_bot.total_tokens
            #     + self.validation_bot.total_tokens
            # ),
            # "errors": [{"type": err_type, "message": err_msg} for err_type, err_msg in self.errors]
        }

        if validation_result:
            result['metadata']['validation'] = validation_result

        # Final summary message
        if self.errors:
            print("\n" + "=" * 60)
            print("⚠️  PARTIAL SUCCESS")
            print("=" * 60)
            print(f"\nI managed to extract some information, but had trouble with {len(self.errors)} section(s).")
            print("Check the output file for what I found!")

        return result

    def save_to_json(self, data: dict[str, Any], output_path: str):
        """Save extracted data to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(data, indent=2, fp=f)
        print(f"\n✓ Saved to {output_path}")


class AutoCodeExtractor:
    """Base class for autoCode format extraction with retry logic"""

    def __init__(self, chat_bot, nax_retries: int = 1):
        self.chat_bot = chat_bot
        self.max_retries = nax_retries

    def get_response(self, prompt: str) -> str:
        instructions=(
            "You are a helpful assistant that extracts structured data from "
            "statistical analysis plans. Always respond with valid JSON only."
        )
        try:
            response = self.chat_bot.get_response(prompt = prompt, system_message = instructions)
        except Exception as e:
            print(f"An error occurred while getting response: {e}")
            response["content"] = ""
        return response.get("content", "")


class TimepointExtractor(AutoCodeExtractor):
    """Bot 1: Extract timepoints from FULL SAP text"""

    def extract_timepoints(self, sap_text: str) -> tuple[list[dict[str, Any]], str | None]:
        """Extract timepoints with retry logic using FULL document"""

        print(f"    Using full document: {len(sap_text):,} chars")

        prompt = f"""Extract all timepoints mentioned in this Statistical Analysis Plan.

        SAP Text (COMPLETE DOCUMENT):
        {sap_text}

        Your task: Find all time measurements mentioned (baseline, followup visits, etc.)

        Return a JSON array in this EXACT format:
        [
        {{"value": 0, "label": "Baseline"}},
        {{"value": 1, "label": "6 weeks"}}
        ]

        Rules:
        - value 0 = baseline, value 1 = first followup, value 2 = second followup, etc.
        - label = exact description from SAP
        - Include ALL timepoints you find
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
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            try:
                timepoints = json.loads(response)

                # Validate format
                if not isinstance(timepoints, list):
                    last_error = "Response was not a list format"
                    raise ValueError("Response is not a list")

                if len(timepoints) == 0:
                    last_error = "No timepoints found in the document"
                    print(f"    ⚠ Warning: AI found 0 timepoints")
                    return [], (
                        "Sorry, I couldn't find any timepoints mentioned in your document. "
                        "The SAP might not clearly specify when measurements are taken, or they "
                        "might be described in an unusual way."
                    )

                for tp in timepoints:
                    if not isinstance(tp, dict) or 'value' not in tp or 'label' not in tp:
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
                    print(f"    Response preview: {response[:300]}")
                    break

        # Fallback message
        error_msg = (
            f"Sorry friend, I tried {self.max_retries} times but couldn't extract timepoints. "
            f"{last_error if last_error else 'Unknown error'}. This might mean:\n"
            "- The timepoints aren't clearly labeled in the document\n"
            "- The document format is unusual\n"
            "- The SAP doesn't contain explicit timepoint information"
        )
        return [], error_msg


class VariableExtractor(AutoCodeExtractor):
    """Bot 2: Extract variables from FULL SAP text"""

    def extract_variables(self, sap_text: str, timepoints: list[dict]) -> tuple[list[dict[str, Any]], str]:
        """Extract variables with retry logic using FULL document"""

        print(f"    Using full document: {len(sap_text):,} chars")

        timepoints_str = json.dumps(timepoints, indent=2) if timepoints else "[]"

        prompt = f"""Extract all outcome variables from this Statistical Analysis Plan.

SAP Text (COMPLETE DOCUMENT):
{sap_text}

Available timepoints:
{timepoints_str}

Return a JSON array in this EXACT format:
[
  {{
    "label": "Primary outcome: Depression score (PHQ-9)",
    "variable_name": "phq9_total",
    "timepoints": [0, 1, 2],
    "type": "continuous"
  }}
]

Rules:
- label = human readable description
- variable_name = valid Python/R name (lowercase, underscores)
- timepoints = list of timepoint values from above
- type = one of: continuous, binary, categorical, count, time_to_event
- Output ONLY the JSON array
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
                    print(f"    ✗ Failed: Empty response")
                    break

            # Clean response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            try:
                variables = json.loads(response)

                # Validate format
                if not isinstance(variables, list):
                    last_error = "Response was not a list format"
                    raise ValueError("Response is not a list")

                if len(variables) == 0:
                    last_error = "No variables found in the document"
                    print(f"    ⚠ Warning: AI found 0 variables")
                    return [], (
                        "Sorry, I couldn't find any outcome variables in your document. "
                        "The SAP might not clearly define primary/secondary outcomes, or they might "
                        "be described differently than expected."
                    )

                valid_types = {"continuous", "binary", "categorical", "count", "time_to_event"}
                for var in variables:
                    if not isinstance(var, dict):
                        last_error = "Variables were not in the correct format"
                        raise ValueError("Invalid variable format")
                    required = ['label', 'variable_name', 'timepoints', 'type']
                    if not all(k in var for k in required):
                        last_error = "Variables missing required fields"
                        raise ValueError("Missing required fields")
                    if var['type'] not in valid_types:
                        last_error = f"Invalid variable type: {var['type']}"
                        raise ValueError(f"Invalid type: {var['type']}")

                print(f"    ✓ Extracted {len(variables)} variables")
                return variables, None

            except (json.JSONDecodeError, ValueError) as e:
                last_error = f"Could not parse the AI's response: {str(e)}"
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Parse error, retry {attempt + 1}/{self.max_retries}: {e}")
                    time.sleep(2)
                    continue
                else:
                    print(f"    ✗ Failed: {e}")
                    print(f"    Response preview: {response[:300]}")
                    break

        # Fallback message
        error_msg = (
            f"Sorry homie, I tried {self.max_retries} times but couldn't extract variables. "
            f"{last_error if last_error else 'Unknown error'}. This might mean:\n"
            "- The outcome variables aren't clearly defined\n"
            "- The document uses non-standard terminology\n"
            "- The SAP doesn't have a clear outcomes section"
        )
        return [], error_msg


class AnalysisExtractor(AutoCodeExtractor):
    """Bot 3: Extract analyses from FULL SAP text"""

    def extract_analyses(self, sap_text: str, variables: list[dict]) -> tuple[list[dict[str, Any]], str | None]:
        """Extract analyses with retry logic using FULL document"""

        print(f"    Using full document: {len(sap_text):,} chars")

        variables_str = json.dumps(variables, indent=2) if variables else "[]"

        prompt = f"""Extract all planned statistical analyses from this Statistical Analysis Plan.

SAP Text (COMPLETE DOCUMENT):
{sap_text}

Available variables:
{variables_str}

Return a JSON array in this EXACT format:
[
  {{
    "name": "Primary analysis: Depression at 6 weeks",
    "model": "linear_mixed_model",
    "outcome": "phq9_total",
    "covariates": ["baseline_phq9", "age"],
    "comparison": "treatment vs control"
  }}
]

Rules:
- name = descriptive name
- model = statistical model type
- outcome = must match a variable_name from variables list
- covariates = list of covariate names (can be empty)
- comparison = what is being compared
- Output ONLY the JSON array
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
                    print(f"    ✗ Failed: Empty response")
                    break

            # Clean response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            try:
                analyses = json.loads(response)

                # Validate format
                if not isinstance(analyses, list):
                    last_error = "Response was not a list format"
                    raise ValueError("Response is not a list")

                if len(analyses) == 0:
                    last_error = "No analyses found in the document"
                    print(f"    ⚠ Warning: AI found 0 analyses")
                    return [], (
                        "Sorry, I couldn't find any statistical analyses described in your document. "
                        "The analysis plan section might be missing or described in a way I don't recognize."
                    )

                variable_names = {v['variable_name'] for v in variables} if variables else set()
                for analysis in analyses:
                    if not isinstance(analysis, dict):
                        last_error = "Analyses were not in the correct format"
                        raise ValueError("Invalid analysis format")
                    required = ['name', 'model', 'outcome']
                    if not all(k in analysis for k in required):
                        last_error = "Analyses missing required fields"
                        raise ValueError("Missing required fields")

                    if variable_names and analysis['outcome'] not in variable_names:
                        print(f"      ⚠ Warning: outcome '{analysis['outcome']}' not in variables")

                print(f"    ✓ Extracted {len(analyses)} analyses")
                return analyses, None

            except (json.JSONDecodeError, ValueError) as e:
                last_error = f"Could not parse the AI's response: {str(e)}"
                if attempt < self.max_retries - 1:
                    print(f"    ⚠ Parse error, retry {attempt + 1}/{self.max_retries}: {e}")
                    time.sleep(2)
                    continue
                else:
                    print(f"    ✗ Failed: {e}")
                    print(f"    Response preview: {response[:300]}")
                    break

        # Fallback message
        error_msg = (
            f"Sorry buddy, I tried {self.max_retries} times but couldn't extract analyses. "
            f"{last_error if last_error else 'Unknown error'}. This might mean:\n"
            "- The statistical analysis plan isn't clearly described\n"
            "- The methods section is incomplete\n"
            "- The document uses unusual statistical terminology"
        )
        return [], error_msg

# ============================================================
# VALIDATION BOT
# ============================================================

class ValidationBot(AutoCodeExtractor):
    """Validates extracted data against the SAP"""

    def validate_extraction(self, sap_text: str, extracted_data: dict) -> dict:
        """Validate the complete extraction - uses first 15k chars for efficiency"""

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
                "suggestions": []
            }

        # Clean response
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        try:
            validation = json.loads(response)
            return validation
        except json.JSONDecodeError as e:
            return {
                "completeness_score": 0,
                "accuracy_score": 0,
                "issues": [f"Validation parse error: {e}"],
                "missing_elements": [],
                "suggestions": []
            }

# ============================================================
# EVALUATION
# ============================================================

class ExtractionEvaluator:
    """Evaluate extraction quality with metrics"""

    @staticmethod
    def evaluate(sap_text: str, extracted_data: dict, validation_result: dict| None) -> dict:
        """Calculate metrics for the extraction"""

        metrics = {
            "items_extracted": {
                "timepoints": len(extracted_data.get('timepoints', [])),
                "variables": len(extracted_data.get('variables', [])),
                "analyses": len(extracted_data.get('analyses', []))
            },
            "format_valid": True,
            "issues": []
        }

        try:
            timepoints = extracted_data.get('timepoints', [])
            if timepoints:
                values = [tp['value'] for tp in timepoints]
                if values != list(range(len(values))):
                    metrics['issues'].append("Timepoint values not sequential")

            variables = extracted_data.get('variables', [])
            valid_timepoint_values = {tp['value'] for tp in timepoints}
            for var in variables:
                for tp_val in var.get('timepoints', []):
                    if tp_val not in valid_timepoint_values:
                        metrics['issues'].append(
                            f"Variable '{var['variable_name']}' references invalid timepoint {tp_val}"
                        )

            analyses = extracted_data.get('analyses', [])
            valid_var_names = {var['variable_name'] for var in variables}
            for analysis in analyses:
                if analysis['outcome'] not in valid_var_names:
                    metrics['issues'].append(
                        f"Analysis '{analysis['name']}' references invalid variable '{analysis['outcome']}'"
                    )

        except Exception as e:
            metrics['format_valid'] = False
            metrics['issues'].append(f"Format validation error: {e}")

        if validation_result:
            metrics['validation'] = {
                "completeness_score": validation_result.get('completeness_score', 0),
                "accuracy_score": validation_result.get('accuracy_score', 0),
                "llm_issues": validation_result.get('issues', []),
                "missing_elements": validation_result.get('missing_elements', [])
            }

        return metrics
    

