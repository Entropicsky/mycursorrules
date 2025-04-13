# OpenAI Python SDK – Responses API and Agents SDK Documentation

## OpenAI Responses API

The **OpenAI Responses API** is a high-level API for conversational AI that supports tool usage. It combines the simplicity of Chat Completions with the tool-using capabilities of the older Assistants API ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=The%20Responses%20API%20is%20our,of%20Chat%20Completions%20with%20the)). With a single `responses.create` call, an AI can handle multi-step tasks using multiple tools and model turns, making it easier to build agent-like applications ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=evolve%2C%20we%20believe%20the%20Responses,multiple%20tools%20and%20model%20turns)). The Responses API is backwards-compatible with Chat Completions (you can use it for plain Q&A or chat), but it also allows the model to invoke **built-in tools** such as web search and file search, as well as call **custom functions** during generation ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=To%20start%2C%20the%20Responses%20API,improvements%20including%20a%20unified%20item)). This unified approach is the recommended path for new integrations, as it supersedes older chat and assistant endpoints ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=match%20at%20L204%20depend%20on,starting%20with%20the%20Responses%20API)).

### Basic Usage

To use the Responses API with Python, install the latest OpenAI Python SDK (`pip install openai`). Then create an OpenAI API client and call the `responses.create` method:

```python
import openai
openai.api_key = "OPENAI_API_KEY"  # or use openai.OpenAI(api_key=...) to create a client

# Basic prompt without tools
response = openai.Client().responses.create(
    model="gpt-4o", 
    input="Hello, can you assist me with a task?"
)
print(response.output_text)  # Assistant's reply as plain text
```

This sends a user query to the model (here `"gpt-4o"` – a GPT-4 model variant supporting tools) and prints the assistant's response text. The `input` can be a **string** (for a single-turn prompt) or a **list of messages** (for multi-turn conversations). For example, to include context or system instructions, supply `input` as a list of message dicts: 

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, who won the World Cup in 2018?"}
]
response = openai.Client().responses.create(model="gpt-4o", input=messages)
print(response.output_text)
```

The Responses API returns a **Response** object. Important properties include: 

- `response.output_text`: The final generated text answer from the assistant ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=4,property)).  
- `response.output`: A list of **output items** (messages or tool invocations). If the assistant used tools, `response.output` will include those tool call entries. If it directly answered, `output` may contain just an assistant message. For convenience, `output_text` is the concatenated text of all assistant messages in the output ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=4,property)).

Each output item has a `type` field (e.g. `"assistant"`, `"function_call"`, etc.) and relevant data. For instance, a function call tool invocation will appear as an item with `type="function_call"` (and include fields like `name` and `arguments`).

**Generation parameters:** You can control response generation with parameters similar to the Chat API. Key options include `temperature` (creativity vs. determinism), `top_p` (nucleus sampling cutoff), and `max_output_tokens` (the maximum tokens in the generated answer). For example: 

```python
response = openai.Client().responses.create(
    model="gpt-4o", 
    input="Tell me a short story about a robot",
    temperature=0.7,
    max_output_tokens=200
)
```

### Streaming Responses

The Responses API supports streaming output. Set `stream=True` to receive an iterator of events instead of waiting for the full completion. For example:

```python
stream = openai.Client().responses.create(
    model="gpt-4o", 
    input="Summarize this text in real-time...", 
    stream=True
)
for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="")  # print incremental text
    elif event.type == "response.error":
        print(f"\nError: {event.error}")
```

This will stream the assistant's answer token-by-token (or in chunks). We check `event.type`: for text, it's `"response.output_text.delta"` with a `delta` field containing the latest text fragment ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=print%28,nError%20occurred%3A%20%7Bevent.error)) ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=The%20streaming%20implementation%20works%20by%3A)). We accumulate or display these fragments as they arrive. If an error occurs during generation, an event with `type=="response.error"` provides the error info ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=print%28,nError%20occurred%3A%20%7Bevent.error)). Streaming allows building responsive UIs that show the answer as it's being generated ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=In%20a%20real%20application%2C%20you,their%20request%20is%20being%20processed)).

### Using Tools with the Responses API

A major feature of the Responses API is the ability to use **tools**. Tools enable the model to perform actions like searching the web, retrieving document information, running code, or calling your own functions. You specify tools by passing a `tools` list to `responses.create`. Each tool is described by a dictionary with at least a `"type"` key, and additional fields depending on the tool type.

**Built-in tool types:** The currently supported built-in tools are:
- `"web_search"` – Internet search for real-time information.
- `"file_search"` – Search within developer-uploaded files/documents.
- `"code_interpreter"` – Execute Python code in a sandbox environment.
- `"function"` – Call a custom function defined by the developer (function calling).

You can combine multiple tools in one request. The model will decide if and when to use them (it can even use multiple tools in sequence within one `responses.create` call as needed ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=evolve%2C%20we%20believe%20the%20Responses,multiple%20tools%20and%20model%20turns))). Below we cover each tool type with usage examples.

#### Web Search Tool

The **web_search** tool allows the assistant to fetch up-to-date information from the internet ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=The%20web%20search%20tool%20enables,restricted%20to%20their%20training%20data)). This helps overcome the limitation of static training data by retrieving current data (news, facts, etc.) with sources. When enabled, the model can issue a search query; the API will perform the search and return results which the model can incorporate into its answer (with citations).

**Usage:** To enable web search, include `{"type": "web_search"}` in the `tools` list. For example:

```python
response = openai.Client().responses.create(
    model="gpt-4o",  # (gpt-4o or gpt-4o-mini are required for web_search) ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=match%20at%20L226%20citations%20from,other%20tools%20or%20function%20calls))
    input="What are the latest headlines in tech?",
    tools=[{"type": "web_search"}]
)
print(response.output_text)
```

**Output:** The assistant’s response will include information found online, typically with references. For example, a response might say: *"Today’s tech headlines include a major breakthrough in quantum computing and a new AI model release (source: Reuters)..."*, followed by a list of citation links to the sources ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=Output%3A)) ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=%23%23%20Escalating%20US,the%20stock%20market%20this%20week)). The web search tool automatically provides proper citations for transparency ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=The%20web%20search%20tool%20performs,core%20content%20with%20current%20research)).

Under the hood, the sequence is: the model decides to search, the API performs the search and returns results, the model reads those results and then produces the final answer. This all happens within the single `responses.create` call. You don’t need to manually handle the search results; the Responses API integrates them. Web search is useful for questions about current events, up-to-date facts, or any query where the answer isn't in the model's training data ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=The%20web%20search%20tool%20enables,restricted%20to%20their%20training%20data)) ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=A%20key%20benefit%20of%20this,maintain%20transparency%20about%20information%20sources)).

#### File Search Tool

The **file_search** tool lets the assistant search your uploaded documents for relevant information ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=While%20web%20search%20brings%20external,have%20been%20uploaded%20to%20OpenAI)). This is great for retrieval-augmented generation (RAG) use cases, where the model can draw on private knowledge bases, PDFs, manuals, etc., that you provide.

Before using file search, you need to **upload documents** to OpenAI and organize them in a **Vector Store**. A vector store is a semantic index of your documents – the content is chunked and embedded so the model can perform similarity search. (See the **Files API and Vector Store** section below for how to upload files and create a vector store.)

**Enabling file_search:** In your `responses.create` call, include a tool dict with `"type": "file_search"`, and specify which vector store to search. For example:

```python
# Assume we have created a vector store and have its ID
VECTOR_STORE_ID = "vs_1234567890"
response = openai.Client().responses.create(
    model="gpt-4o",
    input="Summarize the key points from our company policy document.",
    tools=[{
        "type": "file_search",
        "vector_store_ids": [VECTOR_STORE_ID],
        "max_num_results": 3
    }]
)
print(response.output_text)
```

Here we set `vector_store_ids` to the ID of the vector store containing our uploaded documents, so the tool knows where to search ([File search - OpenAI API](https://platform.openai.com/docs/guides/tools-file-search#:~:text=,1%202%203)). We also set `max_num_results`: this limits how many document chunks to retrieve (in this case, up to 3 relevant chunks). The assistant’s answer will be based on content from those documents and will usually include citations pointing to the source file and section ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=The%20file%20search%20tool%20enables,several%20key%20capabilities)). For instance, the answer might quote the policy and cite the document name or a file identifier.

**How it works:** The model can trigger a file search when it needs information beyond the prompt. The Responses API will then search the specified vector store for passages relevant to the model’s query. The results (document excerpts and references) are provided to the model, which can integrate them into the final answer ([Unleash the Power of OpenAI's Responses API: Building a Robust RAG System](https://www.funfun.ai/he/ai-news/unleash-the-power-of-open-ais-responses-api-building-a-robust-rag-system-bQL-yok_0qw#:~:text=If%20we%20want%20to%20generate,and%20return%20the%20generated%20response)). This allows the model to accurately retrieve facts from your files, such as product documentation or research papers, and include them with source citations for verification ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=,reference%20information%20across%20multiple%20files)). Using file search, the assistant can handle questions about lengthy documents or multiple files, performing analysis and synthesis across them ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=,reference%20information%20across%20multiple%20files)).

*(Note: You can attach at most one vector store per response call; that store can hold up to 10,000 files for search ([Modify Assistant - Portkey Docs](https://portkey.ai/docs/api-reference/inference-api/assistants-api/assistants/modify-assistant#:~:text=Show%20child%20attributes)). Make sure to upload your files and build the vector store beforehand. Also, `vector_store_ids` expects the **ID** of the store, not individual file IDs.)*

#### Code Interpreter Tool

The **code_interpreter** tool allows the assistant to run Python code in a sandboxed environment during the conversation. This tool is similar to ChatGPT's Code Interpreter – it enables data analysis, calculations, file manipulations, and even plotting, all under the model’s control. The model can write and execute code to fulfill the user’s request, then use the results to form its answer.

**Attaching files:** You can optionally provide the code interpreter with files (e.g. data files or images) that the code can use. For instance, if a user asks the assistant to analyze `"data.csv"`, you would upload `data.csv` via the Files API and then enable the code interpreter tool with that file attached. You specify this by including `"file_ids"` in the tool definition.

**Usage example:** Suppose we have a CSV file of sales data that we want the AI to analyze. First, upload the file (see Files API section) and get its file ID. Then call:

```python
DATA_FILE_ID = "file_abc123..."  # the ID of an uploaded CSV or other file
response = openai.Client().responses.create(
    model="gpt-4o",
    input="Calculate the total sales per category from the data file.",
    tools=[{
        "type": "code_interpreter",
        "file_ids": [DATA_FILE_ID]
    }]
)
print(response.output_text)
```

In this call, we allowed the model to use the code interpreter with the file we attached. The model might respond by writing Python code to read the CSV and compute the totals, execute that code, and then return the results. The `output_text` would then contain the analysis, e.g., a summary of sales per category, possibly including any tables or figures as needed.

**How it works:** When the model decides to use the code tool, the API executes the code and captures its output or any files it produces. The model can then incorporate those results into its final answer. You can attach up to **20 files** for the code interpreter to use ([Modify Assistant - Portkey Docs](https://portkey.ai/docs/api-reference/inference-api/assistants-api/assistants/modify-assistant#:~:text=tool_resources)). Typically, the assistant will first produce a code execution step (which might appear as an output item of type `"tool_call"` or similar), then the API runs it, and the final answer is given. All of this is abstracted away in a single `responses.create` call – once you provide the `code_interpreter` tool and files, the model and API handle the rest.

*(Note: The code runs in a restricted sandbox with no internet. It's useful for data science tasks, math, file format conversions, etc. Always review the code or set appropriate guardrails, as the model-generated code executes with certain privileges.)*

#### Function Calling (Custom "function" Tools)

The Responses API also supports **custom function calling**, enabling the model to call developer-defined functions. This is done by exposing a function as a tool of type `"function"`. You provide the function’s name, description, and a JSON schema for its parameters. The model can then decide to invoke this function with arguments during the conversation. This mechanism lets you extend the AI with arbitrary operations (database queries, external API calls, business logic, etc.) in a controlled way ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=response%20%3D%20client.responses.create%28%20model%3D%22gpt,tools%3Dtools%2C)).

**Defining a function tool:** Create a dictionary with `"type": "function"`, the function’s `name`, a `description`, and a `parameters` schema (following the JSON Schema format). For example, suppose we have a Python function `convert_currency(amount, from_currency, to_currency)` that converts currency using up-to-date rates:

```python
# Define the schema for the function tool
tools = [{
    "type": "function",
    "name": "convert_currency",
    "description": "Convert an amount from one currency to another using current exchange rates",
    "parameters": {
        "type": "object",
        "properties": {
            "amount": {"type": "number", "description": "Amount of money to convert"},
            "from_currency": {"type": "string", "description": "Currency code to convert from (e.g. USD)"},
            "to_currency":   {"type": "string", "description": "Currency code to convert to (e.g. JPY)"}
        },
        "required": ["amount", "from_currency", "to_currency"],
        "additionalProperties": False
    },
    "strict": True  # model must adhere strictly to this schema
}]
```

Here we declared a tool named `"convert_currency"` with the required parameters ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=,number)) ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=,)). The `strict: True` flag tells the model it must supply parameters exactly matching the schema (no extras) ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=,True)).

Now, we call the Responses API with this tool:

```python
# Initial user question
user_question = {"role": "user", "content": "How much is 100 euros in Japanese yen?"}
response = openai.Client().responses.create(
    model="gpt-4o",
    input=[user_question],
    tools=tools
)
```

When the model sees the question, it recognizes it should use the function tool. Instead of answering directly, the `response.output` will contain a **function call request**. For example, `response.output[0]` might be an item with `type="function_call"`, `name="convert_currency"`, and `arguments='{"amount": 100, "from_currency": "EUR", "to_currency": "JPY"}'` ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=When%20the%20model%20sees%20this,It%20automatically%20identifies%20that)). The model has essentially asked your function to run with those arguments.

**Executing the function:** The Python SDK does **not** automatically run your Python function – you must handle that. You’ll detect the function call in the response and then execute the actual function in your code:

```python
if response.output and response.output[0].type == "function_call":
    tool_call = response.output[0]
    args = json.loads(tool_call.arguments)       # parse the JSON arguments
    result = convert_currency(**args)            # call the actual Python function
    print(f"Function returned: {result}")
```

Now `result` holds the output of `convert_currency`, e.g. `16473.12` (yen). We need to send this result back to the model so it can finish answering the user. We do that by appending two messages to the conversation: the function call itself (as the assistant’s action) and the function’s result (as a special message of type `"function_call_output"`), then calling `responses.create` again:

```python
conversation = [user_question]                # start with the original user question
conversation.append(tool_call)                # the assistant's function call message
conversation.append({
    "type": "function_call_output",
    "call_id": tool_call.call_id,             # link to the function call
    "output": json.dumps(result)              # the function's return value (JSON string)
})
# Now ask the model to produce the final answer, given it has the function result
final_response = openai.Client().responses.create(
    model="gpt-4o",
    input=conversation,
    tools=tools
)
print(final_response.output_text)
```

In this second call, the model receives the information that the function was called and what it returned. It will then continue the conversation and produce a user-friendly answer using that data. For example: *"100 euros is approximately **16,473.12 Japanese yen** based on current rates."* ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=tools%3Dtools%2C%20%29%20print%28response_2)). 

This multi-step flow (model requests function → your code executes function → model uses result) is handled in two `responses.create` calls. In practice, you can wrap this logic in a loop or function to automate the detect-execute-respond cycle, as shown in the above example. The key steps are: check `response.output` for a `"function_call"`, run the function, and provide a `"function_call_output"` message for the model’s follow-up call ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=,tool_call%20%3D%20response.output%5B0)) ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=conversation_history.append%28tool_call%29%20conversation_history.append%28%7B%20,json.dumps%28result%29)).

**Multi-turn and memory:** The Responses API can maintain context through the `input` list. By keeping a `conversation_history` list of messages (as we did with `conversation` above), you can handle follow-up questions seamlessly. Continue appending user messages and the assistant’s function call interactions to this list for subsequent calls. The model will remember prior exchanges and results, enabling complex multi-turn dialogues that mix conversation and tool use ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=,response)) ([OpenAI Responses API: The Ultimate Developer Guide | DataCamp](https://www.datacamp.com/tutorial/openai-responses-api#:~:text=1,conversations%20where%20previous%20context%20matters)).

**Summary:** Function calling tools allow you to extend the assistant’s capabilities arbitrarily. The model will decide when to invoke the function based on the user’s request and the function’s description/schema. You retain control by executing the actual function in your environment. This bridges the gap between natural language and your backend logic, all within the structured interface of the Responses API.

### Files API (Uploading and Managing Files)

Using the file search or code interpreter tools requires you to upload files to OpenAI first. The Python SDK provides a **Files API** for uploading and managing these files. Each uploaded file gets a unique `file_id` which you use later in tools or vector stores.

**Uploading a file:** Use `openai.File.create` (or `client.files.create`) to upload a file. You need to pass a file-like object and a `purpose`. For example:

```python
file_obj = open("policies.pdf", "rb")
uploaded_file = openai.File.create(file=file_obj, purpose="assistants")
print(uploaded_file.id, uploaded_file.filename, uploaded_file.status)
```

This will upload the PDF to your OpenAI file storage. The `purpose="assistants"` indicates the file will be used with the Responses/Assistants APIs (for search or code tools) ([LLM By Examples — Get started with OpenAI GPT-4o (part 3 of 3) | by MB20261 | Medium](https://medium.com/@mb20261/llm-by-examples-get-started-with-openai-part-3-of-3-ab5a511ff98c#:~:text=file%20%3D%20client.files.create%28%20file%3Dopen%28file_path%2C%20,purpose%3D%27assistants%27)). The returned object contains the `id` (e.g. `"file_XXXXXXXX"`), the filename, size, and processing status. The file’s contents are processed asynchronously (for large files, this might involve scanning or chunking); usually, `status` will transition to `"processed"` when ready.

**Listing and retrieving files:** You can list your files with `openai.File.list()`, retrieve metadata with `openai.File.retrieve(file_id)`, and download content with `openai.File.download(file_id)` or `client.files.content(file_id)`. For example:

```python
files = openai.File.list()
for f in files.data:
    print(f.id, f.filename, f.purpose)
# Get file content
file_content = openai.File.download(uploaded_file.id)
with open("downloaded_copy.pdf", "wb") as out:
    out.write(file_content)
```

The file content is returned as bytes (for binary files) or text for text files ([LLM By Examples — Get started with OpenAI GPT-4o (part 3 of 3) | by MB20261 | Medium](https://medium.com/@mb20261/llm-by-examples-get-started-with-openai-part-3-of-3-ab5a511ff98c#:~:text=def%20__assist_save_output_file,as%20file%3A%20file.write%28data_bytes)). You can also delete files with `openai.File.delete(file_id)` when they are no longer needed.

**Note:** Uploaded files count toward your storage and are private to your API key. You should upload only data you need for your application (e.g., knowledge base documents, data files) and handle any sensitive data appropriately.

### Vector Store API (Document Indexing for File Search)

To use the `file_search` tool effectively, raw file uploads are not enough – they must be indexed in a **vector store**. The vector store is a semantic search index of your documents that the file_search tool queries. The OpenAI SDK provides endpoints to create and manage vector stores and to add your files to them.

**Creating a Vector Store:** Use `client.vector_stores.create(name=...)` to create a new store. For example:

```python
vector_store = openai.Client().vector_stores.create(name="MyDocumentIndex")
print(vector_store.id, vector_store.name, vector_store.num_files)
```

This returns a VectorStore object with a unique `id` (e.g. `"vs_abcdefgh"`). Initially, `num_files` will be 0. You can list existing stores with `client.vector_stores.list()` and retrieve or delete them by ID (`retrieve()` / `delete()`).

**Adding files to a vector store:** Once you have uploaded files (via `openai.File.create` as shown above), you need to add them to the vector store so they get chunked and embedded. There are a couple of ways to do this:

- **Batch add multiple files:** The SDK provides a convenience method to upload and index files in one go. For example, to attach several uploaded files to the store and wait for indexing to complete:

  ```python
  file_ids = ["file_ABC...", "file_XYZ..."]  # IDs of files already uploaded
  batch = openai.Client().vector_stores.file_batches.create_and_poll(
      vector_store_id=vector_store.id,
      file_ids=file_ids
  )
  print(batch.status)  # e.g. "succeeded"
  ```

  This will take the files with those IDs, add them to the vector store, and poll until the embedding process is finished. After completion, the store’s `num_files` will reflect the new files, and the documents are ready for searching ([LLM By Examples — Get started with OpenAI GPT-4o (part 3 of 3) | by MB20261 | Medium](https://medium.com/@mb20261/llm-by-examples-get-started-with-openai-part-3-of-3-ab5a511ff98c#:~:text=%29%20vector_store%20%3D%20client,create_and_poll)).

- **Upload directly to store:** Alternatively, you can upload file data directly into a vector store. For instance, to add a single file:

  ```python
  with open("report.pdf", "rb") as f:
      vs_file = openai.Client().vector_stores.files.upload_and_poll(
          vector_store_id=vector_store.id,
          file=f,
          filename="report.pdf"
      )
  print(vs_file.id, vs_file.status)  # file now in store
  ```

  This call will upload the file and attach it to the store in one step, waiting for processing to complete. Under the hood it creates a file and a file batch for you. You can also use `vector_stores.files.create()` and then `files.poll()` if you prefer a manual approach.

After adding files, the vector store automatically handles splitting documents into chunks and creating embeddings ([Unleash the Power of OpenAI's Responses API: Building a Robust RAG System](https://www.funfun.ai/he/ai-news/unleash-the-power-of-open-ais-responses-api-building-a-robust-rag-system-bQL-yok_0qw#:~:text=If%20we%20want%20to%20generate,and%20return%20the%20generated%20response)). Now the store is ready for queries via the `file_search` tool.

**Searching the Vector Store directly:** In some cases, you might want to query the vector store yourself (without involving the LLM) to see what documents are most relevant. You can use `client.vector_stores.search`:

```python
results = openai.Client().vector_stores.search(
    vector_store_id=vector_store.id,
    query="deep research"
)
for doc in results.documents:
    print(f"Document excerpt: {doc.page_content[:100]}... (Score: {doc.score})")
```

This returns a list of document chunks (`results.documents`) ordered by relevance to the query, each with its content and a relevance score ([Unleash the Power of OpenAI's Responses API: Building a Robust RAG System](https://www.funfun.ai/he/ai-news/unleash-the-power-of-open-ais-responses-api-building-a-robust-rag-system-bQL-yok_0qw#:~:text=3,a%20given%20query)) ([Unleash the Power of OpenAI's Responses API: Building a Robust RAG System](https://www.funfun.ai/he/ai-news/unleash-the-power-of-open-ais-responses-api-building-a-robust-rag-system-bQL-yok_0qw#:~:text=4,document)). You might use this to preview what the file_search tool would retrieve. Typically, though, you’ll rely on the Responses API to call the search and incorporate results automatically.

**Summary:** The Vector Store API allows you to turn raw files into a searchable knowledge base. Key steps are: create a vector store, upload or add files to it (embedding them), then reference that store by ID in your `file_search` tool calls. This abstracts away the complexities of chunking and embedding – the OpenAI platform handles those, so with a single call the assistant can find relevant info across thousands of documents ([Unleash the Power of OpenAI's Responses API: Building a Robust RAG System](https://www.funfun.ai/he/ai-news/unleash-the-power-of-open-ais-responses-api-building-a-robust-rag-system-bQL-yok_0qw#:~:text=If%20we%20want%20to%20generate,and%20return%20the%20generated%20response)).

## OpenAI Agents SDK (Python)

While the Responses API handles single-call tool usage, the **OpenAI Agents SDK** is an open-source Python framework for orchestrating more complex, multi-step agent workflows. It provides higher-level abstractions to design agents (with roles, tools, and behaviors), manage multi-agent systems, and incorporate features like tool delegation (handoffs) and guardrails ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=The%20OpenAI%20Agents%20SDK%20enables,very%20small%20set%20of%20primitives)). The Agents SDK works *on top of* the OpenAI API (it uses the Responses API or Chat API under the hood) to simplify building autonomous agents that can use tools in a loop until a task is completed ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=%2A%20Agent%20loop%3A%20Built,a%20tool%2C%20with%20automatic%20schema)).

### Installation

Install the Agents SDK via pip:

```bash
pip install openai-agents
```

This provides the `agents` Python package (and related `openai.tools` if using the unified import style). You will also need an OpenAI API key configured, as the agents will call the OpenAI API internally.

### Core Concepts

- **Agent:** In this SDK, an Agent represents an AI entity (backed by an LLM) with a goal or role, plus a set of tools it can use. You configure an Agent with instructions (like a system prompt or role definition) and attach tools and optional guardrails/handoffs ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=,to%20agents%20to%20be%20validated)).
- **Tool:** A capability that an agent can use. Tools can be custom Python functions (converted to tools via a decorator) or built-in ones like web search or file search. In the Agents SDK, a tool is essentially a function the agent can call; the SDK handles formatting the tool call for the LLM and validating inputs ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=,tuning%20and%20distillation%20tools)).
- **Handoff:** A mechanism for an agent to delegate to another agent. This is implemented as a special tool call that transfers control. It allows complex workflows with multiple specialized agents (e.g. a main agent that hands off a subtask to another expert agent) ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=23)) ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=26)).
- **Guardrail:** Validation checks that run alongside agent steps to enforce constraints. For example, a guardrail can validate the agent’s output against a schema or policy and stop the agent loop if the output is invalid ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=,tuning%20and%20distillation%20tools)).
- **Runner:** The Agents SDK provides a Runner to execute the agent loop. The runner will send the agent’s prompt to the model, observe if a tool is called, execute the tool, feed the result back to the agent, and repeat until the agent signals it is done. This loop of LLM <-> Tool continues automatically via the Runner.

### Creating and Running an Agent

To create an agent, import the core classes and any tool classes you need. For example:

```python
from agents import Agent, Runner, WebSearchTool

# Define an agent with a role and (optional) tools
research_agent = Agent(
    name="ResearchAssistant",
    instructions="You are an assistant that can search the web to answer questions.",
    tools=[WebSearchTool()]  # give it web search capability
)

# Run the agent on a user query
result = Runner.run_sync(research_agent, "What's the latest on climate change policy?")
print(result.final_output)
```

In this snippet, we created an `Agent` named "ResearchAssistant" with a simple instruction and the `WebSearchTool` enabled. `WebSearchTool()` is a built-in tool class in the SDK that uses the OpenAI web search under the hood (requires an OpenAI key, and uses the Responses API’s web_search) ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=instructions%3D,can%20search%20the%20web)). We then call `Runner.run_sync(agent, input)` to execute the agent loop synchronously and retrieve the final result. The `result` (of type `AgentResult`) contains the `final_output` (the final answer text) and other info like intermediate steps. In this case, the agent will likely use the web search tool internally to gather information before producing the answer.

**Agent loop:** When `Runner.run_sync` is invoked, the SDK handles iterating with the model. It will send the agent’s instructions + user query to the LLM. If the LLM’s response indicates a tool use (e.g. it decides to call `WebSearchTool`), the SDK will catch that, execute `WebSearchTool` (performing the search), get the results, and feed them back into the LLM on the next loop iteration. This continues until the LLM produces a final answer (not calling any more tools). You do not have to manually call the OpenAI API for each step – the SDK abstracts the entire chain. The built-in agent loop ensures the agent uses tools as needed and stops when done ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=%2A%20Agent%20loop%3A%20Built,a%20tool%2C%20with%20automatic%20schema)).

**Asynchronous usage:** There is also `Runner.run` for async usage (which returns a coroutine). Internally, the Agents SDK uses asynchronous I/O for tool calls, so you can integrate it into an async application if needed. For simple scripts, `run_sync` is convenient.

### Using Tools in Agents SDK

**Built-in tools:** The SDK comes with some ready-made tools for common needs:
- `WebSearchTool` – allows web searches (similar to Responses API web_search).
- `FileSearchTool` – allows searching an OpenAI vector store (similar to file_search tool; you provide the vector store IDs and options when constructing it) ([OpenAI Agents SDK -II - Medium](https://medium.com/@danushidk507/openai-agents-sdk-ii-15a11d48e718#:~:text=OpenAI%20Agents%20SDK%20,tool%20for%20searching%20within%20files)).
- (If available) `CodeExecutionTool` or similar – if code interpreter integration exists, it would be a tool class.
- Additional utilities for voice (if using the `[voice]` extra) for speech-to-text or text-to-speech, etc.

To use a built-in tool, simply instantiate it and include it in the agent’s `tools` list. For example, to enable file searching:

```python
from agents import FileSearchTool
agent = Agent(
    name="DocsQA",
    instructions="You answer questions using the company documents.",
    tools=[FileSearchTool(vector_store_ids=[VECTOR_STORE_ID], max_num_results=5)]
)
```

This attaches a file search tool configured to use a specific vector store and limit results to 5 ([Intermittent 500 Error on the New Agents SDK + Retrieving Metadata ...](https://community.openai.com/t/intermittent-500-error-on-the-new-agents-sdk-retrieving-metadata-with-filesearchtool/1154789#:~:text=,vector_store_id%5D)). When this agent runs, it can call the FileSearchTool to retrieve info from that vector store as part of its reasoning.

**Custom function tools:** The SDK makes it easy to turn your own Python functions into tools. Use the `@function_tool` decorator on any function to automatically generate a schema and make it invokable by the agent ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=%40function_tool)) ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=,tuning%20and%20distillation%20tools)). For example:

```python
from agents import function_tool

@function_tool
def lookup_order_status(order_id: str) -> str:
    """Check order status by order ID in the database."""
    # (Your code to lookup order_id)
    return "Order status: Shipped"
```

By decorating `lookup_order_status` with `@function_tool`, it becomes a Tool that the agent can use. The SDK will infer the function name, description (from the docstring), and parameter schema from the type hints automatically ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=%40function_tool)). You can then include `lookup_order_status` in an agent’s tools list:

```python
support_agent = Agent(
    name="CustomerSupport",
    instructions="You are a customer support assistant who can lookup order info.",
    tools=[lookup_order_status]  # function_tool decorated function
)
```

Now the agent can call `lookup_order_status` during its conversation when appropriate. The SDK handles formatting a function call for the LLM and validating the arguments with Pydantic (ensuring the model provides `order_id` as a string, for example) ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=,tuning%20and%20distillation%20tools)).

**Tool invocation and schema:** In the Agents SDK, when the LLM chooses to use a tool, the SDK matches the tool name and validates the arguments. If the model’s proposed arguments don’t validate against the function’s schema, the SDK can reject that step or ask the model to retry (this is part of built-in guardrails for tools). If valid, the SDK will execute the tool function and capture its return. The return value is then given back to the LLM in the next loop iteration as if it were the result of a function call.

### Handoffs (Delegating to other Agents)

Handoffs allow an agent to pass control to another agent. This is useful in multi-agent systems – e.g., a triage agent that decides whether a user query should be handled by a sales agent or a support agent. In the SDK, a handoff is implemented by listing other agents in an agent’s `handoffs` parameter. Essentially, the agent can "call" one of those sub-agents as a tool.

For example, imagine we have two specialized agents:

```python
# Define two specialized agents
shopping_agent = Agent(
    name="ShoppingAssistant",
    instructions="You are a shopping assistant who helps with product queries.",
    tools=[WebSearchTool()]  # can use web search to find product info
)
support_agent = Agent(
    name="SupportAssistant",
    instructions="You are a support agent who handles returns and refunds.",
    tools=[submit_refund_request]  # a custom function tool for refunds
)
```

Now we create a **triage agent** that will route user requests:

```python
triage_agent = Agent(
    name="TriageAgent",
    instructions="You are a triage agent. Decide which assistant (shopping or support) should handle the user’s request, then hand it off.",
    handoffs=[shopping_agent, support_agent]
)
```

By putting `shopping_agent` and `support_agent` in `triage_agent.handoffs`, we allow the triage agent to transfer the conversation to one of them ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=instructions%3D,correct%20agent)). Running the triage agent works similarly:

```python
result = Runner.run_sync(triage_agent, "I need to return a pair of shoes I bought.")
print(result.final_output)
```

In this scenario, the `TriageAgent` will analyze the query about returning shoes and decide it's a support query. It will then issue a **handoff** to the SupportAssistant. The Agents SDK handles this by pausing the triage agent and invoking the support_agent with the same user query (and possibly a brief handoff instruction automatically) ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=26)). The support_agent then goes through its own loop (maybe using its refund tool), and produces a result (e.g. confirming a refund). That result is then returned as the final output of the triage_agent’s run. From the developer’s perspective, you just called `Runner.run_sync` once – the SDK orchestrated the multi-agent interaction internally. 

Handoffs can chain or nest, but typically a handoff is used for one level of delegation to specialized sub-agents.

### Guardrails and Validation

The Agents SDK includes **guardrails** to ensure the agent’s behavior and outputs meet certain criteria. Guardrails can be thought of as background checks that run each time through the loop. For example, you could set a guardrail that verifies the assistant’s final answer contains no PII or that intermediate tool outputs meet a format.

To use guardrails, you can pass a list of guardrail functions or objects to the agent (or define them via decorators). A guardrail is essentially a function that takes the agent’s input or output and returns a validation result (pass/fail). If a guardrail fails, the agent can stop or take corrective action. The SDK’s documentation provides patterns for guardrails (often using Pydantic for output validation).

One common use is to enforce the format of the final answer. For instance:

```python
from agents import Guardrail

# Define a simple guardrail that ensures the final answer is under 100 words
def length_check(output: str) -> bool:
    return len(output.split()) < 100

short_answer_guardrail = Guardrail(check=length_check, on_fail="cut_off")

agent = Agent(
    name="BriefAssistant",
    instructions="Provide a brief answer.",
    tools=[WebSearchTool()],
    guardrails=[short_answer_guardrail]
)
```

In this pseudocode, `Guardrail` wraps our `length_check` function. If the final output is too long, `on_fail="cut_off"` might tell the agent to cut off the answer or try again (depending on implementation). The Agents SDK can run these guardrails either on each loop iteration or just on final output, as configured. This is a more advanced feature – the key takeaway is that you can enforce constraints or safety rules on the agent's behavior without manually checking after the fact ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=,tuning%20and%20distillation%20tools)).

### Tracing and Debugging

By default, the Agents SDK has built-in **tracing** capabilities. It can record each step of the agent’s reasoning, tool calls, and results. This trace can be output to the console or visualized via tools (OpenAI may provide a web UI for viewing agent runs). When developing agents, tracing is extremely useful for understanding what the model is doing at each step and for debugging issues. 

If you want to capture traces programmatically, the SDK provides a `Tracer` or you can inspect the `AgentResult` which contains a log of `steps`. Each step might include the prompt, the model’s output, any tool invoked, and the tool’s result. 

For example, after running an agent:

```python
result = Runner.run_sync(agent, "Example query")
for step in result.steps:
    print(step)
```

This would print a structured record of each turn in the agent’s loop. The trace might show: *LLM decided to call tool X with arguments Y; tool X returned Z; LLM then produced final answer.* Tracing and the debugging UI (if enabled) help fine-tune agent prompts, improve tool definitions, and ensure the workflow is correct ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=world%20applications%20without%20a%20steep,tune%20models%20for%20your%20application)) ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=Here%20are%20the%20main%20features,of%20the%20SDK)).

### Practical Usage Patterns

With the Agents SDK, you can compose complex behaviors:

- **Single-agent with tools:** e.g. a coding assistant that can use a `CodeInterpreterTool` to run code and a `WebSearchTool` for documentation lookup.
- **Multi-agent delegation:** e.g. an email assistant that hands off to a calendar scheduling agent for meeting requests, or a main agent that breaks a task into parts and delegates to specialized sub-agents (research, writing, verification).
- **Long-running processes:** The agent loop can iterate many times (though be mindful of token limits and costs). For instance, an agent could loop through a planning task, call multiple APIs, gather data, and only stop when a certain condition is met.
- **Integration with external systems:** By writing custom function tools, you can connect agents to databases, third-party APIs, or even control devices. The function_tool decorator generates the JSON schema, and you implement the actual logic. The agent will call the function when needed, and you have full control over what it does (ensuring safety and correctness).

**Example – Multi-step workflow:** Consider an agent that needs to book travel. It might use web search to find flights, a custom function tool to reserve a ticket (via some API), and another function tool to send a confirmation email. The agent’s loop would be: search for flights → parse results → call booking function → upon success, call email function → return final confirmation to user. All these steps can be orchestrated with one agent equipped with those tools, or with multiple agents (one focused on searching, one on booking, etc., coordinated via handoffs). The Agents SDK’s flexibility lets you choose the design that fits your application.

### Agents SDK vs. Direct API Usage

The Agents SDK is built on top of the Responses (and Chat Completions) APIs ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=New%20tools%20for%20building%20agents,into%20their%20Python%20codebases%2C)) ([Models - OpenAI Agents SDK](https://openai.github.io/openai-agents-python/models/#:~:text=The%20Agents%20SDK%20comes%20with,APIs%20using%20the%20new)). If your use case is relatively straightforward (one or two tool uses in a single turn), you might directly use the Responses API as shown earlier. But if you need an agent that autonomously decides on multiple tool calls and possibly interacts over multiple turns with complex control flow, the SDK simplifies that logic. It abstracts away the manual steps of checking for function calls, calling tools, and feeding back results.

In summary, the **OpenAI Python SDK** now offers powerful capabilities for building AI assistants:
- The **Responses API** provides a unified interface for prompt-completion with tool use (web, file, code, function) in a single API call, ideal for one-off questions or tasks where the model can internally decide to use tools ([New tools for building agents | OpenAI](https://openai.com/index/new-tools-for-building-agents/#:~:text=To%20start%2C%20the%20Responses%20API,improvements%20including%20a%20unified%20item)).
- The **Agents SDK** builds on this to allow persistent, multi-step agents with an event loop, making it easier to create autonomous agents that can plan and execute complex sequences of actions ([Mastering OpenAI’s new Agents SDK & Responses API [Part 1] - DEV Community](https://dev.to/bobbyhalljr/mastering-openais-new-agents-sdk-responses-api-part-1-2al8#:~:text=Then%20OpenAI%20dropped%20their%20Agents,APIs%20without%20constant%20human%20input)) ([Mastering OpenAI’s new Agents SDK & Responses API [Part 1] - DEV Community](https://dev.to/bobbyhalljr/mastering-openais-new-agents-sdk-responses-api-part-1-2al8#:~:text=What%20is%20OpenAI%E2%80%99s%20Agents%20SDK%3F)).

By using these APIs, developers can create AI systems that not only chat, but take actions — searching information, running code, calling APIs, and coordinating with each other — all through Python code with clear abstractions. The combination of the Responses API for model intelligence and tools, plus the Agents SDK for orchestration, provides a comprehensive toolkit for building advanced AI-driven applications. 

