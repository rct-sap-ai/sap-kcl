from pathlib import Path
from docxtpl import DocxTemplate
from Classes.chat_classes import OpenAIChat
import asyncio


class Template:
    def __init__(
        self,
        template_path: str | Path,
        system_message_function,
        prompt_register,
    ) -> None:

        self.template_path = template_path
        self.system_message_function = system_message_function # a function of protocol text
        self.prompt_register = prompt_register

    
    def get_sap_content(self, protocol_text, model = "gpt-5-2025-08-07"):
        chat_bot = OpenAIChat(
            model_name = model, 
            system_message = self.system_message_function(protocol_text))
        self.sap_content = asyncio.run(
            chat_bot.run_prompts_register_async(prompt_register=self.prompt_register)
        )
        
    def save_content_as_text(self, path):
        sap_content = self.sap_content
        with open(path, "w") as f:
            for key, value in sap_content.items():
                f.write(f"{key}: {value}\n")
        print(f"raw SAP content saved to {path}")
            

    def populate(self, sap_folder, sap_name = 'SAP.docx'):
        if getattr(self, "sap_content", None) is not None:
            sap_content = self.sap_content
            template = DocxTemplate(self.template_path)
            template.render(sap_content)
            output_path = Path(sap_folder) / sap_name
            template.save(output_path)
            print(f"SAP saved to {output_path}")
        else:
             raise ValueError("sap_content must be set before populating template.")
