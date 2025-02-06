# groq_client.py

import os
from groq import Groq
from dotenv import load_dotenv
from .prompt import SYSTEM_PROMPT

load_dotenv()

# Create the Groq client using the GROQ_API_KEY from environment variables
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def stream_groq_chat_completion(chat_history, model="llama3-70b-8192", temperature=1.2):
    """
    Get a chat completion from the Groq API and yield tokens one by one.
    This function simulates streaming by splitting the full reply into tokens.

    Parameters:
        chat_history (list): Conversation history as a list of message dicts.
        model (str): The model to use.
        temperature (float): Sampling temperature.

    Yields:
        str: The next token (or a small chunk) in the assistant's reply.
    """
    # Ensure the system prompt is the first message.
    if not chat_history or chat_history[0].get("role") != "system":
        chat_history.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    # Call the Groq API without specifying max_tokens.
    response = client.chat.completions.create(
        messages=chat_history, model=model, temperature=temperature
    )
    # Retrieve the complete reply.
    full_reply = response.choices[0].message.content
    # Optional: Debug print the full reply for verification.
    # print("Full reply received:", full_reply)

    # Split the reply into tokens (using whitespace splitting; adjust as needed)
    tokens = full_reply.split()
    for token in tokens:
        yield token + " "  # Yield each token followed by a space

