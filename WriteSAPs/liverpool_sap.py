from auto_sap.generate_templates.generate_liverpool_template import liverpool_template as template
from pathlib import Path
import dotenv
dotenv.load_dotenv()
import os

saps_path = Path(os.getenv("SAPAI_SHARED_PATH")) / "SAPs" /"Liverpool"
protocols_path = Path(os.getenv("SAPAI_SHARED_PATH")) / "Protocols" / "Liverpool"


protocl_folder = 'Protocols/Liverpool'

protocol_paths = [
    ('gothic2', f'{protocols_path}/GOTHIC2 Protocol_V4.0_03.05.2024.pdf'),
    ('stopem', f'{protocols_path}/STOPEM Protocol v4.0.pdf')
]

for sap_name, protocol_path in protocol_paths:
    print(f"Generating SAP for {sap_name}...")
    template.write_sap(
        protocol_path=protocol_path,  
        sap_folder_path=saps_path,
        sap_name=f"{sap_name}_sap"
    )