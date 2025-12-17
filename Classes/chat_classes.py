import asyncio
import time
import json
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv, find_dotenv

# Load .env once when the module is imported
load_dotenv(find_dotenv())


class OpenAIChat:
    def __init__(
        self,
        model_name: str = "gpt-5-nano",
        system_message: str = "You are a helpful chatbot.",
    ):
        self.model_name = model_name
        self.system_message = system_message
        # If OPENAI_API_KEY is in env, this works without passing api_key explicitly
        self.client = OpenAI()
        
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
                # NOTE: we're currently ignoring the `system_message` arg here;
                # if you want, you can pass it down to get_response.
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

    # >>> NEW METHOD FOR AUTOCODE CONVERSATIONAL EDITING <<<
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
        """
        Use the model to revise a JSON list (timepoints/variables/analyses)
        according to a natural-language user instruction.

        Parameters
        ----------
        item_type : str
            "timepoints", "variables", or "analyses" (only used in instructions).
        sap_context : str
            Relevant chunk of the SAP text (can be empty, or truncated).
        current_json : str
            JSON string representing the current list (e.g. result['timepoints']).
        user_instruction : str
            Free-text feedback from the user, e.g.:
            "No, you've added an extra timepoint at 6 months, can you take it out."

        Returns
        -------
        str
            JSON string with the UPDATED list (no markdown, no extra text).
        """

        if system_message is None:
            system_message = (
                "You are helping to revise a JSON list of "
                f"{item_type} extracted from a Statistical Analysis Plan (SAP).\n"
                "You will be given:\n"
                "1) Optional SAP context\n"
                "2) The current JSON list\n"
                "3) A natural-language instruction from the user\n\n"
                "Apply ONLY the requested edits while keeping everything else unchanged.\n"
                "Do NOT add explanations or comments.\n"
                "Always return VALID JSON ONLY (a JSON array) with no markdown fences."
            )

        prompt = f"""
SAP context (may be empty):
{sap_context}

Current JSON list for {item_type}:
{current_json}

User instruction:
\"\"\"{user_instruction}\"\"\"

Now return ONLY the updated JSON array for {item_type}.
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
    ):
        self.model_name = model_name
        self.system_message = system_message
        # If OPENAI_API_KEY is in env, this works without passing api_key explicitly
        self.client = AsyncOpenAI()

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
                print(f"No prompt in prompt dictionary for {var_name}")
                response_content = "ERROR: tag not in prompt dictionary"
            else:
                try:
                    response = await self.get_response(
                        prompt=prompt,
                        reasoning_effort=item.reasoning_effort,
                        verbosity=item.verbosity,
                    )
                    response_content = (response.get("content", "") or "").strip()
                    if not response_content:
                        response_content = "ERROR"
                except Exception as e:
                    print(f"An error occurred for {var_name}: {e}")
                    response_content = "ERROR"

            return var_name, response_content

        tasks = [run_one(item) for item in prompt_register]

        for var_name, value in await asyncio.gather(*tasks):
            results[var_name] = value

        return results
