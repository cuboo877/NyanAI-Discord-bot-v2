from google import genai
import os
from dotenv import load_dotenv
from helper.config_sql_helper import ConfigSQLHelper
from helper.memory_sql_helper import MemorySqlHelper
import tiktoken

load_dotenv()
#-------------

apiKey = os.getenv('gemini-apiKey')
client = genai.Client(api_key=apiKey)
model_name = ConfigSQLHelper.default_model
role_prompt = ConfigSQLHelper.default_role

async def request(prompt:str,channelId:int): #memory powered
    enc = tiktoken.get_encoding("cl100k_base")
    try:
        histories = await MemorySqlHelper().get_history_list(channel_id=channelId)
        full_prompt = ""
        total_tokens = 0
        for h in histories:
            time = h.time
            author = h.author
            content = h.content
            if total_tokens + len(enc.encode(content)) > 3000:
                break
            full_prompt += f"\n[{time}] {author}: {content}"
            total_tokens += len(enc.encode(content))

        full_prompt += role_prompt + "\n" + prompt

        response = client.models.generate_content(
            model = model_name,
            contents = full_prompt,
        )
        return response.text
    except Exception as e:
        print(f"Error in Gemini API request: {e}")
        return f"嗚嗚嗚...人家不知道欸QQ"
