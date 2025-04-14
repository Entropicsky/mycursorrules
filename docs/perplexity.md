<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Perplexity API Documentation: Sonar API

This detailed documentation covers the Perplexity Sonar API, its capabilities, models, and integration protocols. The Sonar API enables you to power your products with real-time, web-wide research and Q\&A capabilities through a simple yet powerful interface.

## Introduction to Sonar by Perplexity

Sonar by Perplexity is a developer API that provides unparalleled real-time, web-wide research and Q\&A capabilities for integration into various applications and workflows[^1][^5]. The API allows developers to leverage Perplexity's advanced AI models to retrieve, synthesize, and analyze information efficiently through a chat-based interface.

### Core Capabilities

- Real-time information retrieval and synthesis
- Web-wide search with contextual understanding
- Advanced AI-powered reasoning and analysis
- Support for various specialized models for different use cases


## API Reference: Chat Completions

### Endpoint

```
POST https://api.perplexity.ai/chat/completions
```


### Authentication

Authentication uses a Bearer token approach:

```
Authorization: Bearer &lt;your_token&gt;
```

Your authentication token must be included in the request header[^2][^4].

### Request Format

Requests to the Chat Completions endpoint require a JSON payload with the following parameters:

#### Required Parameters

- `model`: The name of the model to use (e.g., "sonar")[^2][^4]
- `messages`: An array of message objects representing the conversation history, each with:
    - `role`: The speaker role ("system", "user", or "assistant")
    - `content`: The message content


#### Optional Parameters

- `max_tokens`: Maximum number of tokens in the response
- `temperature`: Controls randomness (0-2); lower values for factual queries, higher for creative applications
- `top_p`: Nucleus sampling threshold (0-1); affects output diversity
- `search_domain_filter`: List of domains to limit search results to (max 3)
- `return_images`: Boolean indicating whether search results should include images
- `return_related_questions`: Boolean for returning related questions
- `search_recency_filter`: Filters results by time (e.g., "week", "day")
- `top_k`: Number of tokens to keep for top-k filtering
- `stream`: Boolean for streaming the response incrementally
- `presence_penalty`: Penalty for token repetition (0-2)
- `frequency_penalty`: Penalty based on frequency of token appearance (0-2)
- `response_format`: Options for structured output formatting
- `web_search_options`: Configuration for web search, including:
    - `search_context_size`: Amount of search context retrieved ("low", "medium", "high")[^2][^4]


### Example Request

```json
{
  "model": "sonar",
  "messages": [
    {
      "role": "system",
      "content": "Be precise and concise."
    },
    {
      "role": "user",
      "content": "How many stars are there in our galaxy?"
    }
  ],
  "max_tokens": 123,
  "temperature": 0.2,
  "top_p": 0.9,
  "search_domain_filter": ["&lt;any&gt;"],
  "return_images": false,
  "return_related_questions": false,
  "search_recency_filter": "&lt;string&gt;",
  "top_k": 0,
  "stream": false,
  "presence_penalty": 0,
  "frequency_penalty": 1,
  "web_search_options": {
    "search_context_size": "high"
  }
}
```


### Response

The API response is of type `any`, containing the generated completion based on the provided parameters[^2][^4].

## Available Models

Perplexity offers several specialized models categorized by their primary functions[^3][^6]:

### Search Models

These models are designed to retrieve and synthesize information efficiently:

- **sonar-pro**: Advanced search offering with grounding, supporting complex queries and follow-ups
- **sonar**: Lightweight, cost-effective search model with grounding


### Research Models

Models that conduct in-depth analysis and generate detailed reports:

- **sonar-deep-research**: Expert-level research model conducting exhaustive searches and generating comprehensive reports


### Reasoning Models

Models that excel at complex, multi-step tasks:

- **sonar-reasoning-pro**: Premier reasoning offering powered by DeepSeek R1 with Chain of Thought (CoT)
- **sonar-reasoning**: Fast, real-time reasoning model designed for quick problem-solving with search


### Offline Models

Chat models that do not use Perplexity's search subsystem:

- **r1-1776**: A version of DeepSeek R1 post-trained for uncensored, unbiased, and factual information


### Context Length per Model

| Model | Context Length | Model Type |
| :-- | :-- | :-- |
| `sonar-deep-research` | 128k | Chat Completion |
| `sonar-reasoning-pro` | 128k | Chat Completion |
| `sonar-reasoning` | 128k | Chat Completion |
| `sonar-pro` | 200k | Chat Completion |
| `sonar` | 128k | Chat Completion |
| `r1-1776` | 128k | Chat Completion |

Special notes:

- `sonar-pro` has a max output token limit of 8k
- The reasoning models output Chain of Thought (CoT) responses
- `r1-1776` is an offline chat model that does not use the search subsystem[^3][^6]


## Parameter Details

### Temperature

The temperature parameter controls the randomness in the model's responses, valued between 0 and 2:

- Lower values (e.g., 0.1): More focused, deterministic, and less creative responses
- Higher values (e.g., 1.5): More random and creative outputs
- Recommendation: Use lower values for factual/information retrieval tasks and higher values for creative applications[^2][^4]


### Top_p

The nucleus sampling threshold, valued between 0 and 1, controls the diversity of generated text:

- Lower values (e.g., 0.5): More focused and deterministic outputs
- Higher values (e.g., 0.95): More diverse outputs
- Often used as an alternative to temperature[^2][^4]


### Search Domain Filter

A list of domains to limit search results to, with the following characteristics:

- Currently limited to only 3 domains for whitelisting and blacklisting
- For blacklisting, add a `-` at the beginning of the domain string[^2][^4]


### Web Search Options

Configuration options for controlling how web search integrates with model responses:

- `search_context_size`: Determines the amount of search context retrieved
    - `low`: Minimizes context for cost savings but less comprehensive answers
    - `medium`: Balanced approach suitable for most queries
    - `high`: Maximizes context for comprehensive answers but at higher cost[^2][^4]


## Additional Resources

Perplexity provides several additional resources to help users effectively utilize the Sonar API:

- **Quickstart Guide**: Start using the API in minutes
- **Pricing Information**: Explore API pricing options
- **Rate Limits and Usage Tiers**: Understand API limits, features, and restrictions
- **System Status**: Track the status of Perplexity's services including the API
- **Additional Guides**:
    - Structured Outputs Guide
    - Search Domain Filter Guide
    - Prompt Guide
    - Sonar Cookbook
    - Perplexity Crawlers Guide
    - Integrating MCP with Perplexity's Sonar API[^1][^5][^3][^6]


## Conclusion

The Perplexity Sonar API provides developers with a powerful set of tools to integrate AI-powered search, research, and reasoning capabilities into their applications. With its variety of specialized models and configurable parameters, the API can be tailored to a wide range of use cases, from simple factual queries to complex multi-step reasoning tasks and in-depth research reports.

By leveraging Perplexity's web-wide search capabilities alongside advanced AI models, developers can create applications that provide users with accurate, up-to-date information and insights across virtually any domain.

<div>⁂</div>

[^1]: https://docs.perplexity.ai/home

[^2]: https://docs.perplexity.ai/api-reference/chat-completions

[^3]: https://docs.perplexity.ai/guides/model-cards

[^4]: https://docs.perplexity.ai/api-reference/chat-completions

[^5]: https://docs.perplexity.ai/home

[^6]: https://docs.perplexity.ai/guides/model-cards

