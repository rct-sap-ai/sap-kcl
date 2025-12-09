import asyncio
import time
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
        
    def get_response(self, prompt: str, reasoning_effort="minimal", verbosity="low", system_message=None):
        if system_message is  None:
            system_message = self.system_message
        response = self.client.responses.create(
            model=self.model_name,
            instructions=system_message,
            input=prompt,
            reasoning={ "effort": reasoning_effort},
            text={ "verbosity": verbosity}
        )
        content = response.output_text.strip()
        return {"content": content}
    
    def run_prompts_register(self, prompt_register, system_message):
        results = {}
        for item  in prompt_register:
            prompt = item.prompt_function()
            var_name = item.variable
       

            print(f"Running {var_name}")
            try:
                response = self.get_response(
                    prompt=prompt, 
                    reasoning_effort=item.reasoning_effort, 
                    verbosity = item.verbosity
                )
                response_content = (response.get("content", "") or "").strip()
                if not response_content:
                    response_content = "ERROR"
            except Exception as e:
                print(f"An error occurred: {e}")
                response_content = "ERROR"
            results[var_name] = response_content
            
        return(results)
    

    




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
            reasoning={ "effort": reasoning_effort},
            text={ "verbosity": verbosity}
        )
        content = response.output_text.strip()
        return {"content": content}
    
    async def run_prompts_register(self, prompt_register, prompt_dictionary):
        print("running prompts async for \u26A1 speed")
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

