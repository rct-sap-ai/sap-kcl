import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GenerateTemplates.generate_kcl_template import kcl_template_v02 as template

template.write_sap(
    protocol_path="Protocols/feeling_safer.pdf",  
    sap_folder_path = "SAPs",
    sap_name = "feeling_safer_v0.2",
)
