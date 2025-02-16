Context windows
The models available through the Gemini API have context windows that are measured in tokens. The context window defines how much input you can provide and how much output the model can generate. You can determine the size of the context window using the API or by looking in the models documentation.

In the following example, you can see that the gemini-1.0-pro-001 model has an input limit of about 30K tokens and an output limit of about 2K tokens, which means a context window of about 32K tokens.


import google.generativeai as genai

model_info = genai.get_model("models/gemini-1.5-flash")

# Returns the "context window" for the model,
# which is the combined input and output token limits.
print(f"{model_info.input_token_limit=}")
print(f"{model_info.output_token_limit=}")
# ( input_token_limit=30720, output_token_limit=2048 )

As another example, if you instead requested the token limits for a model like gemini-1.5-flash-001, you'd see that it has a 2M context window.

Count tokens
All input to and output from the Gemini API is tokenized, including text, image files, and other non-text modalities.

You can count tokens in the following ways:

Call count_tokens with the input of the request.
This returns the total number of tokens in the input only. You can make this call before sending the input to the model to check the size of your requests.

Use the usage_metadata attribute on the response object after calling generate_content.
This returns the total number of tokens in both the input and the output: total_token_count.
It also returns the token counts of the input and output separately: prompt_token_count (input tokens) and candidates_token_count (output tokens).

Count text tokens
If you call count_tokens with a text-only input, it returns the token count of the text in the input only (total_tokens). You can make this call before calling generate_content to check the size of your requests.

Another option is calling generate_content and then using the usage_metadata attribute on the response object to get the following:

The separate token counts of the input (prompt_token_count) and the output (candidates_token_count)
The total number of tokens in both the input and the output (total_token_count)

import google.generativeai as genai

model = genai.GenerativeModel("models/gemini-1.5-flash")

prompt = "The quick brown fox jumps over the lazy dog."

# Call `count_tokens` to get the input token count (`total_tokens`).
print("total_tokens: ", model.count_tokens(prompt))
# ( total_tokens: 10 )

response = model.generate_content(prompt)

# On the response for `generate_content`, use `usage_metadata`
# to get separate input and output token counts
# (`prompt_token_count` and `candidates_token_count`, respectively),
# as well as the combined token count (`total_token_count`).
print(response.usage_metadata)
# ( prompt_token_count: 11, candidates_token_count: 73, total_token_count: 84 )

Count multi-turn (chat) tokens
If you call count_tokens with the chat history, it returns the total token count of the text from each role in the chat (total_tokens).

Another option is calling send_message and then using the usage_metadata attribute on the response object to get the following:

The separate token counts of the input (prompt_token_count) and the output (candidates_token_count)
The total number of tokens in both the input and the output (total_token_count)
To understand how big your next conversational turn will be, you need to append it to the history when you call count_tokens.


import google.generativeai as genai

model = genai.GenerativeModel("models/gemini-1.5-flash")

chat = model.start_chat(
    history=[
        {"role": "user", "parts": "Hi my name is Bob"},
        {"role": "model", "parts": "Hi Bob!"},
    ]
)
# Call `count_tokens` to get the input token count (`total_tokens`).
print(model.count_tokens(chat.history))
# ( total_tokens: 10 )

response = chat.send_message(
    "In one sentence, explain how a computer works to a young child."
)

# On the response for `send_message`, use `usage_metadata`
# to get separate input and output token counts
# (`prompt_token_count` and `candidates_token_count`, respectively),
# as well as the combined token count (`total_token_count`).
print(response.usage_metadata)
# ( prompt_token_count: 25, candidates_token_count: 21, total_token_count: 46 )

from google.generativeai.types.content_types import to_contents

# You can call `count_tokens` on the combined history and content of the next turn.
print(model.count_tokens(chat.history + to_contents("What is the meaning of life?")))
# ( total_tokens: 56 )

Count multimodal tokens
All input to the Gemini API is tokenized, including text, image files, and other non-text modalities. Note the following high-level key points about tokenization of multimodal input during processing by the Gemini API:

Images are considered to be a fixed size, so they consume a fixed number of tokens (currently 258 tokens), regardless of their display or file size.

Video and audio files are converted to tokens at the following fixed rates: video at 263 tokens per second and audio at 32 tokens per second.

Image files
During processing, the Gemini API considers images to be a fixed size, so they consume a fixed number of tokens (currently 258 tokens), regardless of their display or file size.

If you call count_tokens with a text-and-image input, it returns the combined token count of the text and the image in the input only (total_tokens). You can make this call before calling generate_content to check the size of your requests. You can also optionally call count_tokens on the text and the file separately.

Another option is calling generate_content and then using the usage_metadata attribute on the response object to get the following:

The separate token counts of the input (prompt_token_count) and the output (candidates_token_count)
The total number of tokens in both the input and the output (total_token_count)
Note: You'll get the same token count if you use a file uploaded using the File API or you provide the file as inline data.
Example that uses an uploaded image from the File API:


import google.generativeai as genai

model = genai.GenerativeModel("models/gemini-1.5-flash")

prompt = "Tell me about this image"
your_image_file = genai.upload_file(path=media / "organ.jpg")

# Call `count_tokens` to get the input token count
# of the combined text and file (`total_tokens`).
# An image's display or file size does not affect its token count.
# Optionally, you can call `count_tokens` for the text and file separately.
print(model.count_tokens([prompt, your_image_file]))
# ( total_tokens: 263 )

response = model.generate_content([prompt, your_image_file])
response.text
# On the response for `generate_content`, use `usage_metadata`
# to get separate input and output token counts
# (`prompt_token_count` and `candidates_token_count`, respectively),
# as well as the combined token count (`total_token_count`).
print(response.usage_metadata)
# ( prompt_token_count: 264, candidates_token_count: 80, total_token_count: 345 )

Example that provides the image as inline data:


import google.generativeai as genai

import PIL.Image

model = genai.GenerativeModel("models/gemini-1.5-flash")

prompt = "Tell me about this image"
your_image_file = PIL.Image.open(media / "organ.jpg")

# Call `count_tokens` to get the input token count
# of the combined text and file (`total_tokens`).
# An image's display or file size does not affect its token count.
# Optionally, you can call `count_tokens` for the text and file separately.
print(model.count_tokens([prompt, your_image_file]))
# ( total_tokens: 263 )

response = model.generate_content([prompt, your_image_file])

# On the response for `generate_content`, use `usage_metadata`
# to get separate input and output token counts
# (`prompt_token_count` and `candidates_token_count`, respectively),
# as well as the combined token count (`total_token_count`).
print(response.usage_metadata)
# ( prompt_token_count: 264, candidates_token_count: 80, total_token_count: 345 )

Video or audio files
Audio and video are each converted to tokens at the following fixed rates:

Video: 263 tokens per second
Audio: 32 tokens per second
If you call count_tokens with a text-and-video/audio input, it returns the combined token count of the text and the video/audio file in the input only (total_tokens). You can make this call before calling generate_content to check the size of your requests. You can also optionally call count_tokens on the text and the file separately.

Another option is calling generate_content and then using the usage_metadata attribute on the response object to get the following:

The separate token counts of the input (prompt_token_count) and the output (candidates_token_count)
The total number of tokens in both the input and the output (total_token_count)
Note: You'll get the same token count if you use a file uploaded using the File API or you provide the file as inline data.

import google.generativeai as genai

import time

model = genai.GenerativeModel("models/gemini-1.5-flash")

prompt = "Tell me about this video"
your_file = genai.upload_file(path=media / "Big_Buck_Bunny.mp4")

# Videos need to be processed before you can use them.
while your_file.state.name == "PROCESSING":
    print("processing video...")
    time.sleep(5)
    your_file = genai.get_file(your_file.name)

# Call `count_tokens` to get the input token count
# of the combined text and video/audio file (`total_tokens`).
# A video or audio file is converted to tokens at a fixed rate of tokens per second.
# Optionally, you can call `count_tokens` for the text and file separately.
print(model.count_tokens([prompt, your_file]))
# ( total_tokens: 300 )

response = model.generate_content([prompt, your_file])

# On the response for `generate_content`, use `usage_metadata`
# to get separate input and output token counts
# (`prompt_token_count` and `candidates_token_count`, respectively),
# as well as the combined token count (`total_token_count`).
print(response.usage_metadata)
# ( prompt_token_count: 301, candidates_token_count: 60, total_token_count: 361 )

System instructions and tools
System instructions and tools also count towards the total token count for the input.

If you use system instructions, the total_tokens count increases to reflect the addition of system_instruction.


import google.generativeai as genai

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

prompt = "The quick brown fox jumps over the lazy dog."

print(model.count_tokens(prompt))
# total_tokens: 10

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", system_instruction="You are a cat. Your name is Neko."
)

# The total token count includes everything sent to the `generate_content` request.
# When you use system instructions, the total token count increases.
print(model.count_tokens(prompt))
# ( total_tokens: 21 )

If you use function calling, the total_tokens count increases to reflect the addition of tools.


import google.generativeai as genai

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

prompt = "I have 57 cats, each owns 44 mittens, how many mittens is that in total?"

print(model.count_tokens(prompt))
# ( total_tokens: 22 )

def add(a: float, b: float):
    """returns a + b."""
    return a + b

def subtract(a: float, b: float):
    """returns a - b."""
    return a - b

def multiply(a: float, b: float):
    """returns a * b."""
    return a * b

def divide(a: float, b: float):
    """returns a / b."""
    return a / b

model = genai.GenerativeModel(
    "models/gemini-1.5-flash-001", tools=[add, subtract, multiply, divide]
)

# The total token count includes everything sent to the `generate_content` request.
# When you use tools (like function calling), the total token count increases.
print(model.count_tokens(prompt))
# ( total_tokens: 206 )