OpenAI Responses API – Full Documentation
==================================================

This document provides an exhaustive reference for OpenAI's Responses API, including endpoint specifications, request/response schemas, usage patterns, examples in multiple languages, and migration notes from Chat Completions and Assistants.

Table of Contents
-----------------
1. Overview
2. Key Concepts
3. Endpoint Reference
4. Request Body Schema
5. Response Object
6. Pagination and Filtering
7. Streaming Protocol
8. Tools and Function Calling
9. Rate Limits and Error Codes
10. Security and Data Retention
11. Migration Guide
12. Language Examples
13. Appendix: JSON Schemas

1. Overview
-----------
The Responses API is OpenAI's stateful, agent‑oriented primitive that unifies the strengths of Chat Completions and Assistants. Each call can either create a new conversational thread or continue a prior one, letting the model maintain context without the developer resending the entire transcript. Threads are identified by server‑generated IDs; responses are versioned objects that can be fetched, streamed, or deleted.

Major capabilities:
* **Persistent context** – chain calls using `previous_response_id`.
* **Built‑in tools** – `web_search_preview`, `file_search`, `code_interpreter`, `computer_use_preview`.
* **Function calling** – define JSON‑schema functions and handle tool invocations.
* **Structured outputs** – optional JSON schema enforcement.
* **Multimodal** – text, vision, and base64 images supported.
* **Streaming** – server‑sent events with semantic event types (`response.output_text.delta`, etc.).

2. Key Concepts
----------------
**Thread** – Implicit conversation container inferred from the first response ID chain.
**Response** – An immutable object containing assistant output, tool calls, usage, and metadata.
**Input Items** – Array elements inside the `input` array: `input_text`, `input_image`, `function_call_output`, etc.
**Output Items** – Elements inside the `output` array: `output_text`, `function_call`, `computer_call`, `reasoning`.

3. Endpoint Reference
---------------------
### 3.1 Create / Continue a Response
`POST /v1/responses`
Body parameters:
```
{
  "model": "gpt-4o",            // required
  "input": [ ... ],             // required unless `previous_response_id` present
  "tools": [ ... ],             // optional
  "temperature": 0.7,           // optional
  "top_p": 1,
  "max_output_tokens": 1024,
  "previous_response_id": null, // string
  "metadata": {
     "session": "marketing-demo"
  },
  "stream": false               // bool
}
```
Returns `201 Created` with a Response object.

### 3.2 Retrieve a Response
`GET /v1/responses/{response_id}`

### 3.3 List Responses in a Thread
`GET /v1/responses?thread_id={thread_id}&limit=20&after={cursor}`

### 3.4 Delete a Response
`DELETE /v1/responses/{response_id}` – hard‑deletes the payload but keeps a tombstone.

### 3.5 List Input Items
`GET /v1/responses/{response_id}/input_items`

4. Request Body Schema
----------------------
`input` is an array whose elements are discriminated unions by `type`:
* `input_text` – `{ "type": "input_text", "text": "...", "annotations": [] }`
* `input_image` – base64 or URL as `image_url`.
* `function_call_output` – echo response after executing a prior function call.

5. Response Object
------------------
```
{
  "id": "resp_abc123",
  "object": "response",
  "created_at": 1741369938,
  "model": "gpt-4o-2024-11-20",
  "thread_id": "thread_xyz",
  "output": [ ... ],
  "usage": { "input_tokens": 20, "output_tokens": 11, "total_tokens": 31 },
  "status": "completed" | "in_progress" | "failed" | "cancelled",
  "error": null,
  "metadata": {}
}
```

Each element of `output` follows:
* **output_text** – assistant natural language.
* **function_call** – JSON with `name`, `arguments`, `call_id`.
* **computer_call** – when using `computer_use_preview`.
* **reasoning** – chain‑of‑thought visible only if `reasoning` models used.

6. Pagination and Filtering
---------------------------
`List` endpoints use cursor pagination: `first_id`, `last_id`, `has_more`. Pass `after` or `before` cursors.

7. Streaming Protocol
---------------------
Set `stream=true` in create call. Server returns an SSE stream whose `event` field encodes semantic deltas:
```
event: response.output_text.delta
data: { "delta": "Hello" }

event: response.done
data: { "id": "resp_abc123" }
```
Use `EventSource` or `openai.beta.chat.completions.create(..., stream=True)` helpers.

8. Tools and Function Calling
-----------------------------
Tools array supports built‑ins and your own functions. Function schema identical to Chat Completions. When model decides to call, you will receive `function_call` output. After executing, pass its JSON result in a subsequent call via `input` array element `function_call_output`.

9. Rate Limits and Error Codes
------------------------------
Refer to account dashboard for per‑model TPM and RPM. Errors follow standard JSON envelope:
* `400` – validation error
* `401` – invalid auth
* `429` – rate limit
* `500` – server

10. Security and Data Retention
--------------------------------
* Requests must include bearer Authorization.
* Responses are retained 30 days; `DELETE` sooner if needed.
* Sensitive inputs should be encrypted at rest.

11. Migration Guide
-------------------
* Replace `chat.completions` with `responses` endpoint.
* Collapse system+user+assistant roles into `input` array.
* Replace thread logic with `previous_response_id`.
* `tools` semantics unchanged.

12. Language Examples
---------------------
### 12.1 Python
```python
from openai import OpenAI
client = OpenAI()

resp = client.responses.create(
    model="gpt-4o",
    input=[{"role": "user", "content": "Explain stochastic gradient descent."}],
    temperature=0.5,
    stream=True
)
for event in resp:
    if event.type == "response.output_text.delta":
        print(event.delta, end="")
```

### 12.2 cURL
```bash
curl https://api.openai.com/v1/responses   -H "Authorization: Bearer $OPENAI_API_KEY"   -H "Content-Type: application/json"   -d '{
        "model": "gpt-4o", 
        "input": [{"role": "user", "content": "List three uses of graph neural networks."}]
      }'
```

### 12.3 Node.js (OpenAI SDK v4)
```js
import OpenAI from "openai";
const openai = new OpenAI();
const resp = await openai.responses.create({
  model: "gpt-4o",
  input: [{ role: "user", content: "Generate a haiku about ocean" }]
});
console.log(resp.output_text);
```

13. Appendix: JSON Schemas
--------------------------
See `schemas/response.json`, `schemas/input_item.json`, and `schemas/output_item.json` for exhaustive field definitions.
