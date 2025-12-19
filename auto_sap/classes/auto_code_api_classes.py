import requests
import os
import dotenv

dotenv.load_dotenv()

class auto_code_api:
    def __init__(self, dev = False):
        if dev:
            self.api_url = "http://127.0.0.1:8000/api/"
            self.TOKEN = os.getenv("AUTOCODE_API_TOKEN_DEV")
        else:
            self.api_url = "https://autocodeapi.example.com/api/"
            self.TOKEN = os.getenv("AUTOCODE_API_TOKEN_PROD")

        self.headers = {
            "Authorization": f"Token {self.TOKEN}",
            "Content-Type": "application/json"
        }
    def post_timepoint(self, value: int, label:str):
        url = self.api_url + "timepoint/"
        data = {
            "value": value,
            "label": label
        }
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status() 
    
        return response.json()
    
