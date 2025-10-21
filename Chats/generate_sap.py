import os
import sys
import glob
import time
from dotenv import load_dotenv

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Classes.protocol_classes import Protocol
from chat_setup import get_chat
from Prompts import prompts_05 as prompts_file

load_dotenv()

# -----------------------
# Configuration
# -----------------------
# Single model configuration
MODEL_NAME = "gpt-4o-mini-2024-07-18"
REQUEST_DELAY_SEC = 1.0  # small delay to avoid rate limits
OUTPUT_DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), "SAP")

# -----------------------
# Prompt task list
# -----------------------
prompt_tasks = [
    ("admin_info", prompts_file.generate_admin_prompt),
    ("introduction", prompts_file.generate_introduction_prompt),
    ("study_design", prompts_file.generate_study_design_prompt),
    ("randomisation", prompts_file.generate_randomisation_prompt),
    ("sample_size", prompts_file.generate_sample_size_prompt),
    ("interim_analysis", prompts_file.generate_interim_analysis_prompt),
    ("timing", prompts_file.generate_timing_prompt),
    ("analysis_considerations", prompts_file.generate_analysis_considerations_prompt),
    ("trial_population", prompts_file.generate_trial_population_prompt),
    ("outcome_definitions", prompts_file.generate_endpoint_prompt),
    ("analysis_methods", prompts_file.generate_inferential_analysis_prompt),
    ("assumptions_and_sensitivity_analysis", prompts_file.generate_assumptions_sensitivity_analysis_prompt),
    ("subgroup_analysis", prompts_file.generate_subgroup_analysis_prompt),
    ("missing_data", prompts_file.generate_missing_data_prompt),
    ("additional_analysis", prompts_file.generate_additional_analysis),
    ("harms", prompts_file.generate_harms),
    ("software", prompts_file.generate_statistical_software),
]

# -----------------------
# Core functions
# -----------------------
def list_protocol_pdfs(protocols_dir: str):
    pattern = os.path.join(protocols_dir, "**", "*.pdf")
    return sorted(glob.glob(pattern, recursive=True))

def generate_sap_text(prompt_tasks, chat):
    """Run each prompt and build a simple text document of the SAP sections using a single chat."""
    sections = []
    for var_name, prompt_func in prompt_tasks:
        prompt = prompt_func()

        print(f"Running {var_name}")
        try:
            response = chat.get_response(prompt=prompt)
            response_content = (response.get("content", "") or "").strip()
            if not response_content:
                response_content = "ERROR"
        except Exception as e:
            print(f"An error occurred: {e}")
            response_content = "ERROR"

        title = var_name.replace("_", " ").title()
        sections.append(f"=== {title} ===\n\n{response_content}\n")
        time.sleep(REQUEST_DELAY_SEC)

    return "\n".join(sections)

def run_for_protocol(file_path: str):
    name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\n\n****** Trial: {name} ******\n")

    # Read protocol
    protocol = Protocol(file_path)
    protocol_txt = protocol.protocol_txt

    # Build system message using prompts_05
    system_message = prompts_file.system_message(protocol_txt)

    # Build chat
    chat = get_chat(system_message=system_message, model_name=MODEL_NAME)

    # Run prompts and build text
    sap_text = generate_sap_text(prompt_tasks, chat)

    # Save TXT
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Use the model name in the filename for clarity
    out_path = os.path.join(OUTPUT_DIR, f"{MODEL_NAME}_{name}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(sap_text)
    print(f"Wrote: {out_path}")

# -----------------------
# Main
# -----------------------
def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    protocols_dir = os.path.join(root_dir, "Protocols")

    pdf_paths = list_protocol_pdfs(protocols_dir)
    # Optionally restrict to a single filename by setting SAP_TARGET_PROTOCOL=boppp.pdf
    target = os.getenv("SAP_TARGET_PROTOCOL", "").strip().lower()
    if target:
        pdf_paths = [p for p in pdf_paths if os.path.basename(p).lower() == target]
    if not pdf_paths:
        if target:
            print(f"{target} not found under: {protocols_dir}")
        else:
            print(f"No PDF protocols found in: {protocols_dir}")
        return

    print(f"Found {len(pdf_paths)} protocol(s).")
    for file_path in pdf_paths:
        run_for_protocol(file_path)

if __name__ == "__main__":
    main()