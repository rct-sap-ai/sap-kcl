from pathlib import Path
from io import BytesIO
from docxtpl import DocxTemplate
from auto_sap.classes.chat_classes import OpenAIChat, OpenAIChatAsync
from auto_sap.classes.protocol_classes import Protocol
from auto_sap.classes.auto_code_classes import AutoCodePipeline
import asyncio
from datetime import date
import time


class Template:
    def __init__(self, template_path, system_message_function, prompt_register,
                 prompts_dictionary, template_name, prompts_name):
        self.template_path = template_path
        self.system_message_function = system_message_function
        self.prompt_register = prompt_register
        self.prompts_dictionary = prompts_dictionary
        self.template_name = template_name
        self.prompts_name = prompts_name

    async def get_sap_content_async(self, protocol_text, model="gpt-5-2025-08-07", api_key=None):
        chat_bot = OpenAIChatAsync(
            model_name=model,
            system_message=self.system_message_function(protocol_text),
            api_key=api_key,
        )
        self.sap_content = await chat_bot.run_prompts_register(
            prompt_register=self.prompt_register,
            prompt_dictionary=self.prompts_dictionary,
        )
        today = date.today()
        self.sap_content.update({"todays_date": today.strftime("%d/%m/%y")})
        self.sap_content.update(
            {"template_prompt_version": f"{self.template_name} with prompts {self.prompts_name}"}
        )

    def get_sap_content(self, protocol_text, model="gpt-5-2025-08-07", api_key=None):
        asyncio.run(self.get_sap_content_async(protocol_text, model, api_key))

    def save_content_as_text(self, path):
        with open(path, "w", encoding="utf-8") as f:
            for key, value in self.sap_content.items():
                f.write(f"{key}: {value}\n")
        print(f"raw SAP content saved to {path}")

    def populate(self, sap_folder, sap_name="SAP.docx"):
        if getattr(self, "sap_content", None) is None:
            raise ValueError("sap_content must be set before populating template.")
        tpl = DocxTemplate(self.template_path)
        tpl.render(self.sap_content)
        output_path = Path(sap_folder) / sap_name
        tpl.save(output_path)
        print(f"SAP saved to {output_path}")

    def populate_to_bytes(self) -> bytes:
        if getattr(self, "sap_content", None) is None:
            raise ValueError("sap_content must be set before populating template.")
        buf = BytesIO()
        tpl = DocxTemplate(self.template_path)
        tpl.render(self.sap_content)
        tpl.save(buf)
        buf.seek(0)
        return buf.read()

    def write_sap(self, protocol_path, sap_name, sap_folder_path="SAPs", test=False, api_key=None):
        t0 = time.time()
        protocol = Protocol(protocol_path)
        model = "gpt-5-nano" if test else "gpt-5-2025-08-07"
        if test:
            print("Test enabled - running with gpt5 nano")
        self.get_sap_content(protocol.protocol_txt, model=model, api_key=api_key)
        self.save_content_as_text(path=f"{sap_folder_path}/{sap_name}_content.txt")
        self.populate(sap_folder=sap_folder_path, sap_name=f"{sap_name}.docx")
        print(f"SAP written in {round(time.time() - t0)} seconds")

    def get_autocode_json(self, output_path=None, model="gpt-5-2025-08-07", api_key=None):
        if getattr(self, "sap_content", None) is None:
            raise ValueError("sap_content must be set before creating autocode json.")
        chat_bot = OpenAIChat(model_name=model, system_message="", api_key=api_key)
        pipeline = AutoCodePipeline(chat_bot)
        content_for_autocode = {
            "timepoint_content": self.sap_content.get("primary_outcome_measures", "") + "\n" + self.sap_content.get("secondary_outcome_measures", ""),
            "variables_content": self.sap_content.get("primary_outcome_measures", "") + "\n" + self.sap_content.get("secondary_outcome_measures", ""),
            "analysis_content": self.sap_content.get("primary_analysis_model", "") + "\n" + self.sap_content.get("secondary_analysis", ""),
        }
        result = pipeline.extract_all(content_for_autocode)
        if output_path:
            pipeline.save_to_json(result, output_path)
        return result
