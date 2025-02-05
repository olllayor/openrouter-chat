# groq_client.py

import os
from groq import Groq
from dotenv import load_dotenv
from .prompt import SYSTEM_PROMPT
load_dotenv()

# Create the Groq client using the GROQ_API_KEY from environment variables
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def get_groq_chat_completion(chat_history, model="llama-3.2-11b-vision-preview", max_tokens=100, temperature=1.2):
    """
    Get a chat completion from the Groq API.

    Parameters:
        chat_history (list): List of dictionaries representing the conversation history.
        model (str): The model to use for the completion.
        max_tokens (int): Maximum tokens to generate.
        temperature (float): Sampling temperature.

    Returns:
        str: The assistant's reply.
    """
    # Ensure the system prompt is included as the first message.
    if not chat_history or chat_history[0].get("role") != "system":
        chat_history.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    
    # Call the Groq API to get the chat completion.
    response = client.chat.completions.create(
        messages=chat_history,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature
    )
    # Extract the assistant's reply from the response.
    assistant_reply = response.choices[0].message.content
    return assistant_reply

