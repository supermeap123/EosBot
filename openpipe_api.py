# openpipe_api.py
import aiohttp
from config import OPENPIPE_API_KEY, logger

API_URL = 'https://api.openpipe.ai/v1/chat/completions'

async def get_openpipe_response(messages, model_string, temperature=0.7):
    headers = {
        'Authorization': f'Bearer {OPENPIPE_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': model_string,
        'messages': messages,
        'temperature': temperature,
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json=payload, headers=headers) as response:
                response_text = await response.text()
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                else:
                    logger.error(f"OpenPipe API Error {response.status}: {response_text}")
                    return None
        except Exception as e:
            logger.exception(f"Exception occurred while calling OpenPipe API: {e}")
            return None
