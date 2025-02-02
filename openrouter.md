  Quick Start
  OpenRouter provides an OpenAI-compatible completion API to 305 models & providers that you can call directly, or using the OpenAI SDK. Additionally, some third-party SDKs are available.
  In the examples below, the OpenRouter-specific headers are optional. Setting them allows your app to appear on the OpenRouter leaderboards.
  Using the OpenAI SDK
  typescript
  python

  Copy
  import OpenAI from "openai"

  const openai = new OpenAI({
    baseURL: "https://openrouter.ai/api/v1",
    apiKey: "<OPENROUTER_API_KEY>",
    defaultHeaders: {
      "HTTP-Referer": "<YOUR_SITE_URL>", // Optional. Site URL for rankings on openrouter.ai.
      "X-Title": "<YOUR_SITE_NAME>", // Optional. Site title for rankings on openrouter.ai.
    } // we dont need it so we don need use it
  })

  async function main() {
    const completion = await openai.chat.completions.create({
      model: "openai/gpt-3.5-turbo",
      messages: [
        {
          "role": "user",
          "content": "What is the meaning of life?"
        }
      ]
    })

    console.log(completion.choices[0].message)
  }
  main()
  Using the OpenRouter API directly
  typescript
  python
  shell

  Copy
  fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": "Bearer <OPENROUTER_API_KEY>",
      "HTTP-Referer": "<YOUR_SITE_URL>", // Optional. Site URL for rankings on openrouter.ai.
      "X-Title": "<YOUR_SITE_NAME>", // Optional. Site title for rankings on openrouter.ai.
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "model": "openai/gpt-3.5-turbo",
      "messages": [
        {
          "role": "user",
          "content": "What is the meaning of life?"
        }
      ]
    })
  });





  Models


  GET
  /api/v1/models/count
  Get total count of available models


  GET
  /api/v1/models (we can search free models in here)
  List all models and their properties

  Note: Different models tokenize text in different ways. Some models break up text into chunks of multiple characters (GPT, Claude, Llama, etc) while others tokenize by character (PaLM). This means that token counts (and therefore costs) will vary between models, even when inputs and outputs are the same. Costs are displayed and billed according to the tokenizer for the model in use.


  Provider Routing
  OpenRouter routes requests to the best available providers for your model, given your preferences, including prompt size and output length. By default, requests are load balanced across the top providers to maximize uptime, but you can customize how this works using the provider object in the request body.
  Load Balancing
  For each model in your request, OpenRouter's default behavior is to load balance requests across providers with the following strategy:
  Prioritize providers that have not seen significant outages in the last 30 seconds.
  For the stable providers, look at the lowest-cost candidates and select one weighted by inverse square of the price (example below).
  Use the remaining providers as fallbacks.
  Here's an example. Let's say Provider A is $1/million tokens, Provider B is $2/million, and Provider C is $3/million. Provider B recently saw a few outages.
  Your request is 9x more likely to be first routed to Provider A than Provider C.
  If Provider A is tried first and fails, then Provider C will be tried next.
  If both providers fail, Provider B will be tried last.
  If you have sort or order set in your provider preferences, load balancing will be disabled.
  Provider Sorting
  As described above, OpenRouter tries to strike a balance between price and uptime by default.
  If you instead want to prioritize throughput, you can include the sort field in the provider preferences, set to "throughput". Load balancing will be disabled, and the router will prioritize providers that have the lowest median throughput over the last day.
  typescript

  Copy
  fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": "Bearer <OPENROUTER_API_KEY>",
      "HTTP-Referer": "<YOUR_SITE_URL>", // Optional. Site URL for rankings on openrouter.ai.
      "X-Title": "<YOUR_SITE_NAME>", // Optional. Site title for rankings on openrouter.ai.
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "model": "meta-llama/llama-3.1-70b-instruct",
      "messages": [
        {"role": "user", "content": "Hello"}
      ],
      "provider": {
        "sort": "throughput"
      }
    })
  });
  To always prioritize low prices, and not apply any load balancing, set sort to "price".
  Custom Routing
  You can set the providers that OpenRouter will prioritize for your request using the order field. The router will prioritize providers in this list, and in this order, for the model you're using. If you don't set this field, the router will load balance across the top providers to maximize uptime.
  OpenRouter will try try them one at a time and proceed to other providers if none are operational. If you don't want to allow any other providers, you should disable fallbacks as well.
  Here's an example, which will end up skipping over OpenAI (which doesn't host Mixtral), try Together, and then fall back to the normal list of providers on OpenRouter:
  typescript

  Copy
  fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": "Bearer <OPENROUTER_API_KEY>",
      "HTTP-Referer": "<YOUR_SITE_URL>", // Optional. Site URL for rankings on openrouter.ai.
      "X-Title": "<YOUR_SITE_NAME>", // Optional. Site title for rankings on openrouter.ai.
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "model": "mistralai/mixtral-8x7b-instruct",
      "messages": [
        {"role": "user", "content": "Hello"}
      ],
      "provider": {
        "order": [
          "OpenAI",
          "Together"
        ]
      }
    })
  });
  Here's an example that will end up skipping over OpenAI, try Together, and then fail if Together fails:
  typescript

  Copy
  fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": "Bearer <OPENROUTER_API_KEY>",
      "HTTP-Referer": "<YOUR_SITE_URL>", // Optional. Site URL for rankings on openrouter.ai.
      "X-Title": "<YOUR_SITE_NAME>", // Optional. Site title for rankings on openrouter.ai.
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "model": "mistralai/mixtral-8x7b-instruct",
      "messages": [
        {"role": "user", "content": "Hello"}
      ],
      "provider": {
        "order": [
          "OpenAI",
          "Together"
        ],
        "allow_fallbacks": false
      }
    })
  });
  Required Parameters (beta)
  By default, providers that don't support a given LLM parameter will ignore them. But you can change this and only filter for providers that support the parameters in your request.
  For example, to only use providers that support JSON formatting:
  typescript

  Copy
  fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": "Bearer <OPENROUTER_API_KEY>",
      "HTTP-Referer": "<YOUR_SITE_URL>", // Optional. Site URL for rankings on openrouter.ai.
      "X-Title": "<YOUR_SITE_NAME>", // Optional. Site title for rankings on openrouter.ai.
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "model": "mistralai/mixtral-8x7b-instruct",
      "messages": [
        {"role": "user", "content": "Hello"}
      ],
      "provider": {
        "require_parameters": true
      },
      "response_format": {
        "type": "json_object"
      }
    })
  });
  Tool Use (beta)
  When you send a request with tools or tool_choice, OpenRouter will only route to providers that natively support tool use.
  Data Privacy
  Some model providers may log prompts, so we display them with a Data Policy tag on model pages. This is not a definitive source of third party data policies, but represents our best knowledge.
  OpenRouter's data policy is managed in your privacy settings. You can disable third party model providers that store inputs for training. Alternatively, you can skip or allow them on a per-request basis:
  typescript

  Copy
  fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": "Bearer <OPENROUTER_API_KEY>",
      "HTTP-Referer": "<YOUR_SITE_URL>", // Optional. Site URL for rankings on openrouter.ai.
      "X-Title": "<YOUR_SITE_NAME>", // Optional. Site title for rankings on openrouter.ai.
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "model": "mistralai/mixtral-8x7b-instruct",
      "messages": [
        {"role": "user", "content": "Hello"}
      ],
      "provider": {
        "data_collection": "deny"
      }
    })
  });
  Disabling a provider causes the router to skip over it and proceed to the next best one.
  Disabling Fallbacks
  To guarantee that your request is only served by the top (lowest-cost) provider, you can disable fallbacks.
  You can also combine this with the order field from Custom Routing to restrict the providers that OpenRouter will prioritize to just your chosen list.
  typescript

  Copy
  fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": "Bearer <OPENROUTER_API_KEY>",
      "HTTP-Referer": "<YOUR_SITE_URL>", // Optional. Site URL for rankings on openrouter.ai.
      "X-Title": "<YOUR_SITE_NAME>", // Optional. Site title for rankings on openrouter.ai.
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "model": "mistralai/mixtral-8x7b-instruct",
      "messages": [
        {"role": "user", "content": "Hello"}
      ],
      "provider": {
        "allow_fallbacks": false
      }
    })
  });
  Ignoring Providers
  Ignore Providers for a Request
  You can ignore providers for a request by setting the ignore field in the provider object.
  Here's an example that will ignore Azure for a request calling GPT-4 Omni:
  typescript

  Copy
  fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": "Bearer <OPENROUTER_API_KEY>",
      "HTTP-Referer": "<YOUR_SITE_URL>", // Optional. Site URL for rankings on openrouter.ai.
      "X-Title": "<YOUR_SITE_NAME>", // Optional. Site title for rankings on openrouter.ai.
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "model": "openai/gpt-4o",
      "messages": [
        {"role": "user", "content": "Hello"}
      ],
      "provider": {
        "ignore": [
          "Azure"
        ]
      }
    })
  });
  Ignore Providers for Account-Wide Requests
  You can ignore providers for all account requests by configuring your preferences. This configuration applies to all API requests and chatroom messages.
  Warning: Ignoring multiple providers may significantly reduce fallback options and limit request recovery.
  When you ignore providers for a request, the list of ignored providers is merged with your account-wide ignored providers.
  Quantization
  Quantization reduces model size and computational requirements while aiming to preserve performance. However, quantized models may exhibit degraded performance for certain prompts, depending on the method used.
  Providers can support various quantization levels for open-weight models.
  Quantization Levels
  By default, requests are load-balanced across all available providers, ordered by price. To filter providers by quantization level, specify the quantizations field in the provider parameter with the following values:
  int4: Integer (4 bit)
  int8: Integer (8 bit)
  fp6: Floating point (6 bit)
  fp8: Floating point (8 bit)
  fp16: Floating point (16 bit)
  bf16: Brain floating point (16 bit)
  fp32: Floating point (32 bit)
  unknown: Unknown
  Example Request with Quantization
  typescript

  Copy
  fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": "Bearer <OPENROUTER_API_KEY>",
      "HTTP-Referer": "<YOUR_SITE_URL>", // Optional. Site URL for rankings on openrouter.ai.
      "X-Title": "<YOUR_SITE_NAME>", // Optional. Site title for rankings on openrouter.ai.
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "model": "meta-llama/llama-3.1-8b-instruct",
      "messages": [
        {"role": "user", "content": "Hello"}
      ],
      "provider": {
        "quantizations": [
          "fp8"
        ]
      }
    })
  });
  JSON Schema for Provider Preferences
  For a complete list of options, see this JSON schema:
  javascript

  Copy
  {
    "$ref": "#/definitions/ProviderPreferences",
    "definitions": {
      "ProviderPreferences": {
        "type": "object",
        "properties": {
          "allow_fallbacks": {
            "type": [
              "boolean",
              "null"
            ],
            "description": "Whether to allow backup providers to serve requests\n- true: (default) when the primary provider (or your custom providers in \"order\") is unavailable, use the next best provider.\n- false: use only the primary/custom provider, and return the upstream error if it's unavailable.\n"
          },
          "require_parameters": {
            "type": [
              "boolean",
              "null"
            ],
            "description": "Whether to filter providers to only those that support the parameters you've provided. If this setting is omitted or set to false, then providers will receive only the parameters they support, and ignore the rest."
          },
          "data_collection": {
            "anyOf": [
              {
                "type": "string",
                "enum": [
                  "deny",
                  "allow"
                ]
              },
              {
                "type": "null"
              }
            ],
            "description": "Data collection setting. If no available model provider meets the requirement, your request will return an error.\n- allow: (default) allow providers which store user data non-transiently and may train on it\n- deny: use only providers which do not collect user data.\n"
          },
          "order": {
            "anyOf": [
              {
                "type": "array",
                "items": {
                  "type": "string",
                  "enum": [
                    "OpenAI",
                    "Anthropic",
                    "Google",
                    "Google AI Studio",
                    "Amazon Bedrock",
                    "Groq",
                    "SambaNova",
                    "Cohere",
                    "Mistral",
                    "Together",
                    "Together 2",
                    "Fireworks",
                    "DeepInfra",
                    "Lepton",
                    "Novita",
                    "Avian",
                    "Lambda",
                    "Azure",
                    "Modal",
                    "AnyScale",
                    "Replicate",
                    "Perplexity",
                    "Recursal",
                    "OctoAI",
                    "DeepSeek",
                    "Infermatic",
                    "AI21",
                    "Featherless",
                    "Inflection",
                    "xAI",
                    "Cloudflare",
                    "SF Compute",
                    "Minimax",
                    "Nineteen",
                    "Liquid",
                    "Chutes",
                    "01.AI",
                    "HuggingFace",
                    "Mancer",
                    "Mancer 2",
                    "Hyperbolic",
                    "Hyperbolic 2",
                    "Lynn 2",
                    "Lynn",
                    "Reflection"
                  ]
                }
              },
              {
                "type": "null"
              }
            ],
            "description": "An ordered list of provider names. The router will attempt to use the first provider in the subset of this list that supports your requested model, and fall back to the next if it is unavailable. If no providers are available, the request will fail with an error message."
          },
          "ignore": {
            "anyOf": [
              {
                "type": "array",
                "items": {
                  "type": "string",
                  "enum": [
                    "OpenAI",
                    "Anthropic",
                    "Google",
                    "Google AI Studio",
                    "Amazon Bedrock",
                    "Groq",
                    "SambaNova",
                    "Cohere",
                    "Mistral",
                    "Together",
                    "Together 2",
                    "Fireworks",
                    "DeepInfra",
                    "Lepton",
                    "Novita",
                    "Avian",
                    "Lambda",
                    "Azure",
                    "Modal",
                    "AnyScale",
                    "Replicate",
                    "Perplexity",
                    "Recursal",
                    "OctoAI",
                    "DeepSeek",
                    "Infermatic",
                    "AI21",
                    "Featherless",
                    "Inflection",
                    "xAI",
                    "Cloudflare",
                    "SF Compute",
                    "Minimax",
                    "Nineteen",
                    "Liquid",
                    "Chutes",
                    "01.AI",
                    "HuggingFace",
                    "Mancer",
                    "Mancer 2",
                    "Hyperbolic",
                    "Hyperbolic 2",
                    "Lynn 2",
                    "Lynn",
                    "Reflection"
                  ]
                }
              },
              {
                "type": "null"
              }
            ],
            "description": "List of provider names to ignore. If provided, this list is merged with your account-wide ignored provider settings for this request."
          },
          "quantizations": {
            "anyOf": [
              {
                "type": "array",
                "items": {
                  "type": "string",
                  "enum": [
                    "int4",
                    "int8",
                    "fp6",
                    "fp8",
                    "fp16",
                    "bf16",
                    "fp32",
                    "unknown"
                  ]
                }
              },
              {
                "type": "null"
              }
            ],
            "description": "A list of quantization levels to filter the provider by."
          },
          "sort": {
            "anyOf": [
              {
                "type": "string",
                "enum": [
                  "price",
                  "throughput"
                ]
              },
              {
                "type": "null"
              }
            ],
            "description": "The sorting strategy to use for this request, if \"order\" is not specified. When set, no load balancing is performed."
          }
        },
        "additionalProperties": false
      }
    },
    "$schema": "http://json-schema.org/draft-07/schema#"
  }



  Prompt Caching
  To save on inference costs, you can enable prompt caching on supported providers and models.
  Most providers automatically enable prompt caching, but note that some (see Anthropic below) require you to enable it on a per-message basis. Note that prompt caching does not work when switching between providers. In order to cache the prompt, LLM engines must store a memory snapshot of the processed prompt, which is not shared with other providers.
  Inspecting cache usage
  To see how much caching saved on each generation, you click the detail button on the Activity page, or you can use the /api/v1/generation API, documented here.
  The cache_discount field in the response body will tell you how much the response saved on cache usage. Some providers, like Anthropic, will have a negative discount on cache writes, but a positive discount (which reduces total cost) on cache reads.
  OpenAI
  Caching price changes:
  Cache writes: no cost
  Cache reads: charged at 0.5x the price of the original input pricing
  Prompt caching with OpenAI is automated and does not require any additional configuration. There is a minimum prompt size of 1024 tokens.
  Click here to read more about OpenAI prompt caching and its limitation.
  Anthropic Claude
  Caching price changes:
  Cache writes: charged at 1.25x the price of the original input pricing
  Cache reads: charged at 0.1x the price of the original input pricing
  Prompt caching with Anthropic requires the use of cache_control breakpoints. There is a limit of four breakpoints, and the cache will expire within five minutes. Therefore, it is recommended to reserve the cache breakpoints for large bodies of text, such as character cards, CSV data, RAG data, book chapters, etc.
  Click here to read more about Anthropic prompt caching and its limitation.
  The cache_control breakpoint can only be inserted into the text part of a multipart message.
  System message caching example:
  json

  Copy
  {
    "messages": [
      {
        "role": "system",
        "content": [
          {
            "type": "text",
            "text": "You are a historian studying the fall of the Roman Empire. You know the following book very well:"
          },
          {
            "type": "text",
            "text": "HUGE TEXT BODY",
            "cache_control": {
              "type": "ephemeral"
            }
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What triggered the collapse?"
          }
        ]
      }
    ]
  }
  User message caching example:
  json

  Copy
  {
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Given the book below:"
          },
          {
            "type": "text",
            "text": "HUGE TEXT BODY",
            "cache_control": {
              "type": "ephemeral"
            }
          },
          {
            "type": "text",
            "text": "Name all the characters in the above book"
          }
        ]
      }
    ]
  }
  DeepSeek
  Caching price changes:
  Cache writes: charged at the same price as the original input pricing
  Cache reads: charged at 0.1x the price of the original input pricing
  Prompt caching with DeepSeek is automated and does not require any additional configuration.


  Web Search
  OpenRouter provides model-agnostic grounding for any model.
  Getting Started
  You can incorporate relevant web search results by activating and customizing the web plugin, or by simply appending :online to any model:
  json

  {
    "model": "openai/gpt-4o:online",
    "messages": [{
      "role": "user",
      "content": "What happened in the news today?"
    }]
  }
  This is a shortcut for using the web plugin:
  json

  {
    "model": "openrouter/auto", // Works with any model or router
    "plugins": [{ "id": "web" }] // See configuration options below
  }
  Conversations
  When using the web plugin, the web search results are sent to the model as a system message right above the most recent user message. That user message is used to make prompt for querying the web (which we currently do using Exa.ai).
  For each result, OpenRouter loads the title, URL, date, and a five-sentence summary (relevant to your user message) into context.
  You can use the search_prompt to change the prefix used when the search results are summarized and listed.
  Customizing the Web Plugin
  The maximum results allowed by the web plugin and the prompt used to attach them to your message stream can be customized:
  json

  {
    "model": "openrouter/auto",
    "plugins": [
      {
        "id": "web",
        "max_results": 1, // Defaults to 5
        "search_prompt": "Some relevant web results:" // See default below
      }
    ]
  }
  By default, the web plugin uses the following search prompt, using the current date:
  A web search was conducted on 2025-01-29T08:34:27.996Z. Incorporate the following web search results into your response. IMPORTANT: Cite them using markdown links named using the domain of the source. Example: [nytimes.com](https://nytimes.com/some-page).
  Pricing
  The web plugin uses your OpenRouter credits and charges $4 per 1000 results. By default, max_results is set to 5, so this comes out to a maximum of $0.02 per request, in addition to the LLM usage for the search result prompt tokens.
  The number of results and the total cost of the web plugin are visible in the generation detail view on your Activity page.