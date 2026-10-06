import os

from dotenv import load_dotenv
from openai import OpenAI


def get_openai_client():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError("Empty API KEY")

    client = OpenAI(api_key=openai_api_key)
    return client
