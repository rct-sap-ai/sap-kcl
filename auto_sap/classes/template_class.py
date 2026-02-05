from io import BytesIO
from pathlib import Path
from tempfile import template
from docxtpl import DocxTemplate
from auto_sap.classes.chat_classes import OpenAIChat, OpenAIChatAsync
from auto_sap.classes.protocol_classes import Protocol
from auto_sap.classes.auto_code_classes import AutoCodePipeline
import asyncio
from datetime import date
import time 
import json



class Template:
    def __init__(
        self,
        template_path: str | Path,
        system_message_function,
        prompt_register,
        prompts_dictionary,
        template_name,
        prompts_name
    ) -> None:

        self.template_path = template_path
        self.system_message_function = system_message_function # a function of protocol text
        self.prompt_register = prompt_register
        self.prompts_dictionary = prompts_dictionary
        self.template_name = template_name
        self.prompts_name = prompts_name

    
    async def get_sap_content_async(self, protocol_text, model="gpt-5-2025-08-07"):
        chat_bot = OpenAIChatAsync(
            model_name=model, 
            system_message=self.system_message_function(protocol_text))
        
        self.sap_content = await chat_bot.run_prompts_register(
            prompt_register=self.prompt_register, 
            prompt_dictionary=self.prompts_dictionary
        )

        today = date.today()
        str_today = today.strftime("%d/%m/%y")
        self.sap_content.update({"todays_date": str_today})
        self.sap_content.update(
            {"template_prompt_version": f"{self.template_name} with prompts {self.prompts_name}"}
        )
    
    def get_sap_content(self, protocol_text, model="gpt-5-2025-08-07"):
        asyncio.run(self.get_sap_content_async(protocol_text, model))

        
    def save_content_as_text(self, path):
        sap_content = self.sap_content
        with open(path, "w", encoding="utf-8") as f:
            for key, value in sap_content.items():
                f.write(f"{key}: {value}\n")
        print(f"raw SAP content saved to {path}")

    def save_content_as_json(self, path):
        sap_content = self.sap_content
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sap_content, f, indent=4)
            

    def render_template(self):
        if getattr(self, "sap_content", None) is not None:
            sap_content = self.sap_content
            template = DocxTemplate(self.template_path)
            template.render(sap_content)
            return(template)
        else:
             raise ValueError("sap_content must be set before populating template.")

    def populate(self, sap_folder, sap_name = 'SAP.docx'):
        rendered_template = self.render_template()
        output_path = Path(sap_folder) / sap_name
        template.save(output_path)
        print(f"SAP saved to {output_path}")

        
    def populate_to_bytes(self):
        """Generate document and return as BytesIO for download"""
        rendered_template = self.render_template()
        # Save to BytesIO instead of file
        doc_io = BytesIO()
        template.save(doc_io)
        doc_io.seek(0) 
        return doc_io
     
    def write_sap(self, protocol_path, sap_name, sap_folder_path = "SAPs", test = False):
        t0 = time.time()

        protocol = Protocol(protocol_path)
        if not test:
            self.get_sap_content(protocol.protocol_txt)
        else:
            print("Test enabled - running with gpt5 nano")
            self.get_sap_content(protocol.protocol_txt, model = "gpt-5-nano")
        self.save_content_as_json(path = f"{sap_folder_path}/{sap_name}.json")
        self.save_content_as_text(path = f"{sap_folder_path}/{sap_name}_content.txt")
        self.populate(sap_folder = sap_folder_path, sap_name = f"{sap_name}.docx")

        t1 = time.time()
        total_time = round(t1- t0)
        print(f"SAP written in {total_time} seconds")

    def get_autocode_json(self, output_path = None, model = "gpt-5-2025-08-07"):
        if getattr(self, "sap_content", None) is not None:
            chat_bot = OpenAIChat(
                model_name = model, 
                system_message = ""
            )
            pipeline = AutoCodePipeline(chat_bot)
            
            # TODO: This may need to be adjusted based on how sap_content is structured for a specific tempalte
            # could let a set of strings be passed to the template class init specifying which sections of sap content to use.
            content_for_autocode = {
                "timepoint_content": self.sap_content.get("primary_outcome_measures", "") + "\n" + self.sap_content.get("secondary_outcome_measures", ""),
                "variables_content": self.sap_content.get("primary_outcome_measures", "") + "\n" + self.sap_content.get("secondary_outcome_measures", ""),
                "analysis_content": self.sap_content.get("primary_analysis_model", "") + "\n" + self.sap_content.get("secondary_analysis", "")
            }

            result = pipeline.extract_all(content_for_autocode)
            if output_path:
                pipeline.save_to_json(result, output_path)
            return result
        else:
            raise ValueError("sap_content must be set before creating autocode json.")
