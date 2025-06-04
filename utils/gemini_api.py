import json
from google import genai
import os
from dotenv import load_dotenv
from helper.config_sql_helper import ConfigSQLHelper
from helper.history_sql_helper import HistorySqlHelper
import tiktoken

load_dotenv()
#-------------

apiKey = os.getenv('gemini-apiKey')
client = genai.Client(api_key=apiKey)
model_name = ConfigSQLHelper.default_model


async def request(prompt:str): #memory powered
    try:
        response = client.models.generate_content(
            model = model_name,
            contents = prompt,
        )
        return str(response.text).strip()
    except Exception as e:
        print(f"Error in Gemini API request: {e}")
        return ""
