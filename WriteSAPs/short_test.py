from auto_sap.generate_templates.generate_kcl_template import kcl_template_v02 as template
from pathlib import Path
import dotenv
dotenv.load_dotenv()
import os

saps_path = Path(os.getenv("SAPAI_SHARED_PATH")) / "SAPs"
protocols_path = Path(os.getenv("SAPAI_SHARED_PATH")) / "Protocols"


template.get_sap_content(protocol_text = "This is a test protocol. It is only being used to test the SAP generation process, so it does not contain any real information about a trial.", model = "gpt-5-nano")

rendered_template = template.render_template()
bytes_io = template.populate_to_bytes()