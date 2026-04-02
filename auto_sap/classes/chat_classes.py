import asyncio
import time
import json
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class OpenAIChat:
    def __init__(
        self,
        model_name: str = "gpt-5-nano",
        system_message: str = "You are a helpful chatbot.",
        api_key: str | None = None,
    ):
        self.model_name = model_name
        self.system_message = system_message
        self.client = OpenAI(api_key=api_key)

    def get_response(
        self,
        prompt: str,
        reasoning_effort: str = "minimal",
        verbosity: str = "low",
        system_message: str | None = None,
    ):
        if system_message is None:
            system_message = self.system_message
        response = self.client.responses.create(
            model=self.model_name,
            instructions=system_message,
            input=prompt,
            reasoning={"effort": reasoning_effort},
            text={"verbosity": verbosity},
        )
        content = response.output_text.strip()
        return {"content": content}

    def run_prompts_register(self, prompt_register, system_message):
        results = {}
        for item in prompt_register:
            prompt = item.prompt_function()
            var_name = item.variable
            print(f"Running {var_name}")
            try:
                response = self.get_response(
                    prompt=prompt,
                    reasoning_effort=item.reasoning_effort,
                    verbosity=item.verbosity,
                    system_message=system_message,
                )
                response_content = (response.get("content", "") or "").strip()
                if not response_content:
                    response_content = "ERROR"
            except Exception as e:
                print(f"An error occurred: {e}")
                response_content = "ERROR"
            results[var_name] = response_content
        return results

    def edit_json_items(
        self,
        *,
        item_type: str,
        sap_context: str,
        current_json: str,
        user_instruction: str,
        reasoning_effort: str = "minimal",
        verbosity: str = "low",
        system_message: str | None = None,
    ) -> str:
        if system_message is None:
            system_message = (
                "You are helping to revise a JSON list of "
                f"{item_type} extracted from a Statistical Analysis Plan (SAP).\n"
                "Apply ONLY the requested edits. Return VALID JSON ONLY with no markdown fences."
            )
        prompt = f"""
SAP context (may be empty):\n{sap_context}\n\nCurrent JSON list for {item_type}:\n{current_json}\n\nUser instruction:\n\"\"\"{user_instruction}\"\"\"\n\nReturn ONLY the updated JSON array.
"""
        response = self.get_response(
            prompt=prompt,
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
            system_message=system_message,
        )
        return (response.get("content", "") or "").strip()


class OpenAIChatAsync:
    def __init__(
        self,
        model_name: str = "gpt-5-nano",
        system_message: str = "You are a helpful chatbot.",
        api_key: str | None = None,
    ):
        self.model_name = model_name
        self.system_message = system_message
        self.client = AsyncOpenAI(api_key=api_key)

    async def get_response(self, prompt: str, reasoning_effort="minimal", verbosity="low"):
        response = await self.client.responses.create(
            model=self.model_name,
            instructions=self.system_message,
            input=prompt,
            reasoning={"effort": reasoning_effort},
            text={"verbosity": verbosity},
        )
        content = response.output_text.strip()
        return {"content": content}

    async def run_prompts_register(self, prompt_register, prompt_dictionary):
        print("running prompts async for ⚡ speed")
        results = {}

        async def run_one(item):
            var_name = item.variable
            prompt = prompt_dictionary.get(var_name, "")
            print(f"Running {var_name}")
            if prompt == "":
                return var_name, "ERROR: tag not in prompt dictionary"
            try:
                response = await self.get_response(
                    prompt=prompt,
                    reasoning_effort=item.reasoning_effort,
                    verbosity=item.verbosity,
                )
                response_content = (response.get("content", "") or "").strip() or "ERROR"
            except Exception as e:
                print(f"An error occurred for {var_name}: {e}")
                response_content = "ERROR"
            return var_name, response_content

        for var_name, value in await asyncio.gather(*[run_one(i) for i in prompt_register]):
            results[var_name] = value
        return results
