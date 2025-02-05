#set GROQ_API_KEY in the secrets

import os
from groq import Groq

# Create the Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

# Set the system prompt
system_prompt = {
    "role": "system",
    "content":
    "You are a helpful assistant. You reply with very short answers."
}

# Initialize the chat history
chat_history = [system_prompt]

while True:
  # Get user input from the console
  user_input = input("You: ")

  # Append the user input to the chat history
  chat_history.append({"role": "user", "content": user_input})

  response = client.chat.completions.create(model="llama3-70b-8192",
                                            messages=chat_history,
                                            max_tokens=100,
                                            temperature=1.2)
  # Append the response to the chat history
  chat_history.append({
      "role": "assistant",
      "content": response.choices[0].message.content
  })
  # Print the response
  print("Assistant:", response.choices[0].message.content)


Playground
Documentation
API Reference
Metrics
API Keys
Settings
Status
discord logoDiscord
Chat with us

Olloyor Maxammatnabiyev
Personal
Documentation
endpoints
Chat
Create chat completion
Audio
Models
Batches
Files
Chat
Create chat completion
POST
https://api.groq.com/openai/v1/chat/completions

Creates a model response for the given chat conversation.

Request Body
frequency_penalty
number or null
Optional
Defaults to 0
Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.

function_call
Deprecated
string / object or null
Optional
Deprecated in favor of tool_choice.

Controls which (if any) function is called by the model. none means the model will not call a function and instead generates a message. auto means the model can pick between generating a message or calling a function. Specifying a particular function via {"name": "my_function"} forces the model to call that function.

none is the default when no functions are present. auto is the default if functions are present.

Show possible types
functions
Deprecated
array or null
Optional
Deprecated in favor of tools.

A list of functions the model may generate JSON inputs for.

Show properties
logit_bias
object or null
Optional
This is not yet supported by any of our models. Modify the likelihood of specified tokens appearing in the completion.

logprobs
boolean or null
Optional
Defaults to false
This is not yet supported by any of our models. Whether to return log probabilities of the output tokens or not. If true, returns the log probabilities of each output token returned in the content of message.

max_completion_tokens
integer or null
Optional
The maximum number of tokens that can be generated in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length.

max_tokens
Deprecated
integer or null
Optional
Deprecated in favor of max_completion_tokens. The maximum number of tokens that can be generated in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length.

messages
array
Required
A list of messages comprising the conversation so far.

Show possible types
model
string
Required
ID of the model to use. For details on which models are compatible with the Chat API, see available models

n
integer or null
Optional
Defaults to 1
How many chat completion choices to generate for each input message. Note that the current moment, only n=1 is supported. Other values will result in a 400 response.

parallel_tool_calls
boolean or null
Optional
Defaults to true
Whether to enable parallel function calling during tool use.

presence_penalty
number or null
Optional
Defaults to 0
Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.

reasoning_format
string or null
Optional
Specifies how to output reasoning tokens

response_format
object or null
Optional
An object specifying the format that the model must output.

Setting to { "type": "json_object" } enables JSON mode, which guarantees the message the model generates is valid JSON.

Important: when using JSON mode, you must also instruct the model to produce JSON yourself via a system or user message.

Show properties
seed
integer or null
Optional
If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same seed and parameters should return the same result. Determinism is not guaranteed, and you should refer to the system_fingerprint response parameter to monitor changes in the backend.

service_tier
string or null
Optional
The service tier to use for the request. Defaults to on_demand.

auto will automatically select the highest tier available within the rate limits of your organization.
flex uses the flex tier, which will succeed or fail quickly.
stop
string / array or null
Optional
Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.

Show possible types
stream
boolean or null
Optional
Defaults to false
If set, partial message deltas will be sent. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. Example code.

stream_options
object or null
Optional
Options for streaming response. Only set this when you set stream: true.

Show properties
temperature
number or null
Optional
Defaults to 1
What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or top_p but not both

tool_choice
string / object or null
Optional
Controls which (if any) tool is called by the model. none means the model will not call any tool and instead generates a message. auto means the model can pick between generating a message or calling one or more tools. required means the model must call one or more tools. Specifying a particular tool via {"type": "function", "function": {"name": "my_function"}} forces the model to call that tool.

none is the default when no tools are present. auto is the default if tools are present.

Show possible types
tools
array or null
Optional
A list of tools the model may call. Currently, only functions are supported as a tool. Use this to provide a list of functions the model may generate JSON inputs for. A max of 128 functions are supported.

Show properties
top_logprobs
integer or null
Optional
This is not yet supported by any of our models. An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability. logprobs must be set to true if this parameter is used.

top_p
number or null
Optional
Defaults to 1
An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or temperature but not both.

user
string or null
Optional
A unique identifier representing your end-user, which can help us monitor and detect abuse.

Returns
Returns a chat completion object, or a streamed sequence of chat completion chunk objects if the request is streamed.

Python

import os

from groq import Groq

client = Groq(
    # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "you are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)

{
  "id": "chatcmpl-f51b2cd2-bef7-417e-964e-a08f0b513c22",
  "object": "chat.completion",
  "created": 1730241104,
  "model": "llama3-8b-8192",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Fast language models have gained significant attention in recent years due to their ability to process and generate human-like text quickly and efficiently. The importance of fast language models can be understood from their potential applications and benefits:\n\n1. **Real-time Chatbots and Conversational Interfaces**: Fast language models enable the development of chatbots and conversational interfaces that can respond promptly to user queries, making them more engaging and useful.\n2. **Sentiment Analysis and Opinion Mining**: Fast language models can quickly analyze text data to identify sentiments, opinions, and emotions, allowing for improved customer service, market research, and opinion mining.\n3. **Language Translation and Localization**: Fast language models can quickly translate text between languages, facilitating global communication and enabling businesses to reach a broader audience.\n4. **Text Summarization and Generation**: Fast language models can summarize long documents or even generate new text on a given topic, improving information retrieval and processing efficiency.\n5. **Named Entity Recognition and Information Extraction**: Fast language models can rapidly recognize and extract specific entities, such as names, locations, and organizations, from unstructured text data.\n6. **Recommendation Systems**: Fast language models can analyze large amounts of text data to personalize product recommendations, improve customer experience, and increase sales.\n7. **Content Generation for Social Media**: Fast language models can quickly generate engaging content for social media platforms, helping businesses maintain a consistent online presence and increasing their online visibility.\n8. **Sentiment Analysis for Stock Market Analysis**: Fast language models can quickly analyze social media posts, news articles, and other text data to identify sentiment trends, enabling financial analysts to make more informed investment decisions.\n9. **Language Learning and Education**: Fast language models can provide instant feedback and adaptive language learning, making language education more effective and engaging.\n10. **Domain-Specific Knowledge Extraction**: Fast language models can quickly extract relevant information from vast amounts of text data, enabling domain experts to focus on high-level decision-making rather than manual information gathering.\n\nThe benefits of fast language models include:\n\n* **Increased Efficiency**: Fast language models can process large amounts of text data quickly, reducing the time and effort required for tasks such as sentiment analysis, entity recognition, and text summarization.\n* **Improved Accuracy**: Fast language models can analyze and learn from large datasets, leading to more accurate results and more informed decision-making.\n* **Enhanced User Experience**: Fast language models can enable real-time interactions, personalized recommendations, and timely responses, improving the overall user experience.\n* **Cost Savings**: Fast language models can automate many tasks, reducing the need for manual labor and minimizing costs associated with data processing and analysis.\n\nIn summary, fast language models have the potential to transform various industries and applications by providing fast, accurate, and efficient language processing capabilities."
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "queue_time": 0.037493756,
    "prompt_tokens": 18,
    "prompt_time": 0.000680594,
    "completion_tokens": 556,
    "completion_time": 0.463333333,
    "total_tokens": 574,
    "total_time": 0.464013927
  },
  "system_fingerprint": "fp_179b0f92c9",
  "x_groq": { "id": "req_01jbd6g2qdfw2adyrt2az8hz4w" }
}
Audio
Create transcription
POST
https://api.groq.com/openai/v1/audio/transcriptions

Transcribes audio into the input language.

Request Body
file
string
Required
The audio file object (not file name) to transcribe, in one of these formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.

language
string
Optional
The language of the input audio. Supplying the input language in ISO-639-1 format will improve accuracy and latency.

model
string
Required
ID of the model to use. Only whisper-large-v3 is currently available.

prompt
string
Optional
An optional text to guide the model's style or continue a previous audio segment. The prompt should match the audio language.

response_format
string
Optional
Defaults to json
The format of the transcript output, in one of these options: json, text, or verbose_json.

temperature
number
Optional
Defaults to 0
The sampling temperature, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. If set to 0, the model will use log probability to automatically increase the temperature until certain thresholds are hit.

timestamp_granularities[]
array
Optional
Defaults to segment
The timestamp granularities to populate for this transcription. response_format must be set verbose_json to use timestamp granularities. Either or both of these options are supported: word, or segment. Note: There is no additional latency for segment timestamps, but generating word timestamps incurs additional latency.

Returns
Returns an audio transcription object

curl

curl https://api.groq.com/openai/v1/audio/transcriptions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@./sample_audio.m4a" \
  -F model="whisper-large-v3"

{
  "text": "Your transcribed text appears here...",
  "x_groq": {
    "id": "req_unique_id"
  }
}
Create translation
POST
https://api.groq.com/openai/v1/audio/translations

Translates audio into English.

Request Body
file
string
Required
The audio file object (not file name) translate, in one of these formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.

model
string
Required
ID of the model to use. Only whisper-large-v3 is currently available.

prompt
string
Optional
An optional text to guide the model's style or continue a previous audio segment. The prompt should be in English.

response_format
string
Optional
Defaults to json
The format of the transcript output, in one of these options: json, text, or verbose_json.

temperature
number
Optional
Defaults to 0
The sampling temperature, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. If set to 0, the model will use log probability to automatically increase the temperature until certain thresholds are hit.

Returns
Returns an audio translation object

curl

curl https://api.groq.com/openai/v1/audio/translations \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@./sample_audio.m4a" \
  -F model="whisper-large-v3"

{
  "text": "Your translated text appears here...",
  "x_groq": {
    "id": "req_unique_id"
  }
}
Models
List models
GET
https://api.groq.com/openai/v1/models

List models

Returns
A list of models

curl

curl https://api.groq.com/openai/v1/models \
-H "Authorization: Bearer $GROQ_API_KEY"

{
  "object": "list",
  "data": [
    {
      "id": "llama3-groq-70b-8192-tool-use-preview",
      "object": "model",
      "created": 1693721698,
      "owned_by": "Groq",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "gemma2-9b-it",
      "object": "model",
      "created": 1693721698,
      "owned_by": "Google",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "llama3-8b-8192",
      "object": "model",
      "created": 1693721698,
      "owned_by": "Meta",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "llama-3.2-90b-vision-preview",
      "object": "model",
      "created": 1727226914,
      "owned_by": "Meta",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "llama3-70b-8192",
      "object": "model",
      "created": 1693721698,
      "owned_by": "Meta",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "llama-3.2-11b-vision-preview",
      "object": "model",
      "created": 1727226869,
      "owned_by": "Meta",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "llama-3.2-11b-text-preview",
      "object": "model",
      "created": 1727283005,
      "owned_by": "Meta",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "whisper-large-v3-turbo",
      "object": "model",
      "created": 1728413088,
      "owned_by": "OpenAI",
      "active": true,
      "context_window": 448,
      "public_apps": null
    },
    {
      "id": "llava-v1.5-7b-4096-preview",
      "object": "model",
      "created": 1725402373,
      "owned_by": "Other",
      "active": true,
      "context_window": 4096,
      "public_apps": null
    },
    {
      "id": "llama-3.1-70b-versatile",
      "object": "model",
      "created": 1693721698,
      "owned_by": "Meta",
      "active": true,
      "context_window": 32768,
      "public_apps": null
    },
    {
      "id": "llama-3.2-3b-preview",
      "object": "model",
      "created": 1727224290,
      "owned_by": "Meta",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "whisper-large-v3",
      "object": "model",
      "created": 1693721698,
      "owned_by": "OpenAI",
      "active": true,
      "context_window": 448,
      "public_apps": null
    },
    {
      "id": "llama-guard-3-8b",
      "object": "model",
      "created": 1693721698,
      "owned_by": "Meta",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "mixtral-8x7b-32768",
      "object": "model",
      "created": 1693721698,
      "owned_by": "Mistral AI",
      "active": true,
      "context_window": 32768,
      "public_apps": null
    },
    {
      "id": "gemma-7b-it",
      "object": "model",
      "created": 1693721698,
      "owned_by": "Google",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "distil-whisper-large-v3-en",
      "object": "model",
      "created": 1693721698,
      "owned_by": "Hugging Face",
      "active": true,
      "context_window": 448,
      "public_apps": null
    },
    {
      "id": "llama-3.2-1b-preview",
      "object": "model",
      "created": 1727224268,
      "owned_by": "Meta",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "llama-3.2-90b-text-preview",
      "object": "model",
      "created": 1727285716,
      "owned_by": "Meta",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "llama3-groq-8b-8192-tool-use-preview",
      "object": "model",
      "created": 1693721698,
      "owned_by": "Groq",
      "active": true,
      "context_window": 8192,
      "public_apps": null
    },
    {
      "id": "llama-3.1-8b-instant",
      "object": "model",
      "created": 1693721698,
      "owned_by": "Meta",
      "active": true,
      "context_window": 131072,
      "public_apps": null
    }
  ]
}
Retrieve model
GET
https://api.groq.com/openai/v1/models/{model}

Get model

Returns
A model object

curl

curl https://api.groq.com/openai/v1/models/llama-3.3-70b-versatile \
-H "Authorization: Bearer $GROQ_API_KEY"

{
  "id": "llama3-8b-8192",
  "object": "model",
  "created": 1693721698,
  "owned_by": "Meta",
  "active": true,
  "context_window": 8192,
  "public_apps": null
}
Batches
Create batch
POST
https://api.groq.com/openai/v1/batches

Creates and executes a batch from an uploaded file of requests

Request Body
completion_window
string
Required
The time frame within which the batch should be processed. Currently only 24h is supported.

endpoint
string
Required
The endpoint to be used for all requests in the batch. Currently /v1/chat/completions is supported.

input_file_id
string
Required
The ID of an uploaded file that contains requests for the new batch.

See upload file for how to upload a file.

Your input file must be formatted as a JSONL file, and must be uploaded with the purpose batch. The file can be up to 100 MB in size.

metadata
object or null
Optional
Optional custom metadata for the batch.

Returns
A created batch object

curl

curl https://api.groq.com/openai/v1/batches \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input_file_id": "file_01jh6x76wtemjr74t1fh0faj5t",
    "endpoint": "/v1/chat/completions",
    "completion_window": "24h"
  }'

{
  "id": "batch_01jh6xa7reempvjyh6n3yst2zw",
  "object": "batch",
  "endpoint": "/v1/chat/completions",
  "errors": null,
  "input_file_id": "file_01jh6x76wtemjr74t1fh0faj5t",
  "completion_window": "24h",
  "status": "validating",
  "output_file_id": null,
  "error_file_id": null,
  "finalizing_at": null,
  "failed_at": null,
  "expired_at": null,
  "cancelled_at": null,
  "request_counts": {
    "total": 0,
    "completed": 0,
    "failed": 0
  },
  "metadata": null,
  "created_at": 1736472600,
  "expires_at": 1736559000,
  "cancelling_at": null,
  "completed_at": null,
  "in_progress_at": null
}
Retrieve batch
GET
https://api.groq.com/openai/v1/batches/{batch_id}

Retrieves a batch.

Returns
A batch object

curl

curl https://api.groq.com/openai/v1/batches/batch_01jh6xa7reempvjyh6n3yst2zw \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json"

{
  "id": "batch_01jh6xa7reempvjyh6n3yst2zw",
  "object": "batch",
  "endpoint": "/v1/chat/completions",
  "errors": null,
  "input_file_id": "file_01jh6x76wtemjr74t1fh0faj5t",
  "completion_window": "24h",
  "status": "validating",
  "output_file_id": null,
  "error_file_id": null,
  "finalizing_at": null,
  "failed_at": null,
  "expired_at": null,
  "cancelled_at": null,
  "request_counts": {
    "total": 0,
    "completed": 0,
    "failed": 0
  },
  "metadata": null,
  "created_at": 1736472600,
  "expires_at": 1736559000,
  "cancelling_at": null,
  "completed_at": null,
  "in_progress_at": null
}
List batches
GET
https://api.groq.com/openai/v1/batches

List your organization's batches.

Returns
A list of batches

curl

curl https://api.groq.com/openai/v1/batches \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json"

{
  "object": "list",
  "data": [
    {
      "id": "batch_01jh6xa7reempvjyh6n3yst2zw",
      "object": "batch",
      "endpoint": "/v1/chat/completions",
      "errors": null,
      "input_file_id": "file_01jh6x76wtemjr74t1fh0faj5t",
      "completion_window": "24h",
      "status": "validating",
      "output_file_id": null,
      "error_file_id": null,
      "finalizing_at": null,
      "failed_at": null,
      "expired_at": null,
      "cancelled_at": null,
      "request_counts": {
        "total": 0,
        "completed": 0,
        "failed": 0
      },
      "metadata": null,
      "created_at": 1736472600,
      "expires_at": 1736559000,
      "cancelling_at": null,
      "completed_at": null,
      "in_progress_at": null
    }
  ]
}
Files
Upload file
POST
https://api.groq.com/openai/v1/files

Upload a file that can be used across various endpoints.

The Batch API only supports .jsonl files up to 100 MB in size. The input also has a specific required format.

Please contact us if you need to increase these storage limits.

Request Body
file
string
Required
The File object (not file name) to be uploaded.

purpose
string
Required
The intended purpose of the uploaded file. Use "batch" for Batch API.

Returns
The uploaded File object.

curl

curl https://api.groq.com/openai/v1/files \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -F purpose="batch" \
  -F "file=@batch_file.jsonl"

{
  "id": "file_01jh6x76wtemjr74t1fh0faj5t",
  "object": "file",
  "bytes": 966,
  "created_at": 1736472501,
  "filename": "batch_file.jsonl",
  "purpose": "batch"
}
List files
GET
https://api.groq.com/openai/v1/files

Returns a list of files.

Returns
A list of File objects.

curl

curl https://api.groq.com/openai/v1/files \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json"

{
  "object": "list",
  "data": [
    {
      "id": "file_01jh6x76wtemjr74t1fh0faj5t",
      "object": "file",
      "bytes": 966,
      "created_at": 1736472501,
      "filename": "batch_file.jsonl",
      "purpose": "batch"
    }
  ]
}
Delete file
DELETE
https://api.groq.com/openai/v1/files/{file_id}

Delete a file.

Returns
A deleted file response object

curl

curl -X DELETE https://api.groq.com/openai/v1/files/file_01jh6x76wtemjr74t1fh0faj5t \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json"

{
  "id": "file_01jh6x76wtemjr74t1fh0faj5t",
  "object": "file",
  "deleted": true
}
Retrieve file
GET
https://api.groq.com/openai/v1/files/{file_id}

Returns information about a file.

Returns
A file object

curl

curl https://api.groq.com/openai/v1/files/file_01jh6x76wtemjr74t1fh0faj5t \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json"

{
  "id": "file_01jh6x76wtemjr74t1fh0faj5t",
  "object": "file",
  "bytes": 966,
  "created_at": 1736472501,
  "filename": "batch_file.jsonl",
  "purpose": "batch"
}
Download file
GET
https://api.groq.com/openai/v1/files/{file_id}/content

Returns the contents of the specified file.

Returns
The file content

curl

curl https://api.groq.com/openai/v1/files/file_01jh6x76wtemjr74t1fh0faj5t/content \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json"
GroqCloud
