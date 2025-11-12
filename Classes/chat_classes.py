import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# Load .env once when the module is imported
load_dotenv(find_dotenv())


class OpenAIChat:
    def __init__(
        self,
        model_name: str = "gpt-4o-mini-2024-07-18",
        system_message: str = "You are a helpful chatbot."
    ):
        self.model_name = model_name
        self.system_message = system_message
        # If OPENAI_API_KEY is in env, this works without passing api_key explicitly
        self.client = OpenAI()
        
    def get_response(self, prompt: str, reasoning_effort="low", verbosity="low"):
        response = self.client.responses.create(
            model=self.model_name,
            instructions=self.system_message,
            input=prompt,
            reasoning={ "effort": reasoning_effort},
            text={ "verbosity": verbosity}
        )
        content = response.output_text.strip()
        return {"content": content}
         

