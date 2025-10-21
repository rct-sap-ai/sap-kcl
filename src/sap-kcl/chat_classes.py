import os
from openai import OpenAI
import google.genai as genai
from google.genai import types
from anthropic import Anthropic
from dotenv import load_dotenv, find_dotenv

class OpenAIChat:
    def __init__(self, model_name: str = "gpt-4o-mini-2024-07-18", temperature: float = 0.7, system_message: str = "you are a chatBot", ):
        self.model_name = model_name
        self.temperature = temperature
        self.system_message = system_message

        _ = load_dotenv(find_dotenv())
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def get_response(self, prompt):
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": prompt}
        ],
            temperature=self.temperature,
        )
        content = response.choices[0].message.content.strip()
        usage = response.usage
        return {"content": content, "usage": usage}
         



class GoogleChat:
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature = 1, system_message: str = "you are a chatBot", ):
        self.model_name = model_name
        self.system_message = system_message
        self.temperature = temperature


      #  _ = load_dotenv(find_dotenv())
      #  print("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


    def get_response(self, prompt):


        response = self.client.models.generate_content(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=self.system_message,
                temperature=self.temperature),
            contents=prompt,
        )
        content = response.text.strip()
        usage = ""
        return {"content": content, "usage": usage}


# claude-3-5-haiku-20241022 (probabaly the cheapest model)

class ClaudeChat:
    def __init__(self, model_name: str = "claude-3-5-haiku-20241022", temperature: float = 0.7, system_message: str = "you are a chatBot"):
        self.model_name = model_name
        self.temperature = temperature
        self.system_message = system_message
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def get_response(self, prompt):
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=1024,
            temperature=self.temperature,
            system=self.system_message,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.content[0].text.strip()
        usage = response.usage  # Optional: Claude usage stats (if needed)
        return {"content": content, "usage": usage}
