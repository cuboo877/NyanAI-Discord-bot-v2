from google import genai
import os
from dotenv import load_dotenv
from utils.config_controller import ConfigController

load_dotenv()
#-------------

apiKey = os.getenv('gemini-apiKey')
client = genai.Client(api_key=apiKey)
model_name = ConfigController.get(key = "model")
role_prompt = ConfigController.get(key = "role")

async def request(prompt:str):
    prompt = role_prompt + prompt
    try:
        response = client.models.generate_content(
            model = model_name,
            contents = prompt
        )
        return response.text
    except Exception as e:
        print(e)
        return f"嗚嗚嗚...人家不知道欸QQ"
