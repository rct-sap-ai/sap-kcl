from auto_sap.classes.protocol_classes import Protocol
from auto_sap.generate_templates.generate_kcl_template import kcl_template_v02 as template
from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator
from pathlib import Path
import dotenv
dotenv.load_dotenv()
import os


api = AutoCodeAPI(dev = False)

protocols_path = Path(os.getenv("SAPAI_SHARED_PATH")) / "Protocols"
saps_folder = "SAPs/Validation"

protocol_folder = protocols_path / "Validation"

protocol_paths = [
    ('star', f'{protocol_folder}/STAR_PROTOCOL_3.06 15.05.25 (CLEAN).pdf'),
    ('reach-asd', f'{protocol_folder}/REACH-ASD Trial Protocol v8 24.02.2022 - CLEAN.pdf'),
    ('rapid', f'{protocol_folder}/RAPID Trial Protocol v9.0 07 JUN 2024 clean.pdf'),
    ('home', f'{protocol_folder}/Protocol_HOME_344318_v1_230725.pdf'),
    ('promise', f'{protocol_folder}/PROMISE Protocol_V3.1_11.pdf'),
    ('attens', f'{protocol_folder}/ATTENS.pdf'),
    ('attend', f'{protocol_folder}/ATTEND WP3+4 Protocol v1.6 08.05.25 CLEAN.pdf'),
    ('actissist', f'{protocol_folder}/ACTISSIST Protocol-v10-11.04.2019_trackchange accepted.pdf'),
    ('diz_ai', f'{protocol_folder}/Manuscript_Stage_1_Registered_Report.pdf'),
    ('eden', f'{protocol_folder}/340838_EDEN+Protocol+v3.0_05.08.2025.pdf'),
]

for sap_name, protocol_path in protocol_paths:
    print(f"Generating SAP for {sap_name}...")

    protocol = Protocol(protocol_path)
    template.get_sap_content(protocol.protocol_txt)
    sap_content = template.sap_content

    acronym = sap_content.get("trial_acronym", "")
    title = sap_content.get("title", "")
    trial_creator = TrialCreator(api, acronym, title)
    trial_creator.add_sap_json(sap_content)

