import time
from pathlib import Path
from docxtpl import DocxTemplate
from Classes.chat_classes import OpenAIChat

class Template:
    def __init__(
        self,
        template_path: str | Path,
        prompts_file,
        prompt_register,
        *,
        delay_sec: float = 0.01
    ) -> None:

        self.template_path = template_path
        self.delay_sec = delay_sec # the delay used between calls to AI to prevent rate limits being exceeded.
        self.prompts_file = prompts_file
        self.prompt_register = prompt_register

    
    def get_sap_content(self, protocol_text):
        chat_bot = OpenAIChat(
            model_name = "gpt-5-2025-08-07", 
            system_message = self.prompts_file.system_message(protocol_text))

        results = {}
        for var_name, prompt_func,  in self.prompt_register:
            prompt = prompt_func()

            print(f"Running {var_name}")
            try:
                response = chat_bot.get_response(prompt=prompt)
                response_content = (response.get("content", "") or "").strip()
                if not response_content:
                    response_content = "ERROR"
            except Exception as e:
                print(f"An error occurred: {e}")
                response_content = "ERROR"
            results[var_name] = response_content
            
            time.sleep(self.delay_sec)
        
        self.sap_content = results

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
