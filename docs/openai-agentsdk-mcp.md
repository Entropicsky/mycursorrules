# Using MCP with the OpenAI Agents SDK: A Practical Guide (v0.0.9)

This guide details a verified method for integrating Model Context Protocol (MCP) servers with the OpenAI Agents SDK (specifically tested with `openai-agents==0.0.9` and `mcp==1.6.0`), addressing common pitfalls encountered during integration.

## Core Working Pattern: Native SDK + Explicit Server Activation

The most reliable method identified involves using the **base `agents` package components** (`Agent`, `Runner`) and explicitly managing the lifecycle of MCP server objects using the classes provided by the `mcp` package (or potentially `agents.mcp` if verified) within an `async` context.

**Key Principles:**

1.  **Use Base `agents` Components:** Rely on `agents.Agent` and `agents.Runner`. The `agents_mcp` extension package can lead to compatibility issues with tool discovery in the base runner.
2.  **Identify Correct MCP Server Class:** Locate the specific class for your server type (e.g., `MCPServerStdio`). **Crucially, verify the correct import path**. Despite some documentation examples, `MCPServerStdio` was found in `agents.mcp` during this successful integration (verify this first in new projects).
3.  **Explicit Server Initialization:** Instantiate the server class (e.g., `MCPServerStdio`) passing necessary configuration (like `name` and `params` containing `command`, `args`, `env`) as required by its `__init__` method. **Do not rely on implicit loading via server names.**
4.  **Asynchronous Activation:** Use `async with YourMCPServerClass(...) as active_server:` to start the server process and get an *active* server object. The server process runs only *within* this block.
5.  **Pass Active Server Object(s) to Agent:** Initialize `agents.Agent` *inside* the `async with` block(s), passing the *list* containing the active server object(s) (e.g., `[active_slack_server, active_firecrawl_server]`) to the `mcp_servers` parameter.
6.  **Use Static `Runner.run`:** Execute the agent using the static method `await Runner.run(starting_agent=your_agent, input=your_input)`. Do *not* instantiate `Runner` with the agent.
7.  **Bridge Async/Sync:** If using in a synchronous framework (like Streamlit), wrap the entire process (server activation, agent definition, runner execution) in an `async def` function and call it using `asyncio.run()`.

## Step-by-Step Implementation Guide

### 1. Installation

Ensure you have the necessary packages. Note that `npx` is also required if using stdio servers based on Node.js.

```bash
# In your requirements.txt
streamlit # Or your main framework
openai
openai-agents
mcp # Core MCP library (often a dependency of openai-agents)
PyYAML # For parsing config file
python-dotenv # For .env file handling

# --------
# Activate virtual environment
# python -m venv .venv
# source .venv/bin/activate # or .\.venv\Scripts\activate (Windows)
pip install -r requirements.txt

# Ensure npx is available if needed (install Node.js/npm)
# npm install -g npx 
```

### 2. Configuration Files

#### a) `.env`

Store sensitive keys here. Load using `dotenv`.

```dotenv
OPENAI_API_KEY="sk-..."
SLACK_BOT_TOKEN="xoxb-..."
SLACK_TEAM_ID="T..."
FIRECRAWL_API_KEY="fc-..."
# Add other keys as needed
```
**Note:** Ensure no trailing commas or parsing issues in this file.

#### b) `mcp_agent.config.yaml` (Optional but Recommended)

Define server configurations for clarity and reusability.

```yaml
mcp:
  servers:
    # Example: Slack Server (Stdio)
    slack:
      command: npx
      args:
        - "-y"
        - "@modelcontextprotocol/server-slack"
      # Env vars here are primarily for reference or defaults;
      # We will explicitly pass loaded keys from .env during initialization.
      env: 
        SLACK_BOT_TOKEN: "${SLACK_BOT_TOKEN}" 
        SLACK_TEAM_ID: "${SLACK_TEAM_ID}"

    # Example: Firecrawl Server (Stdio using 'env' command)
    firecrawl-mcp: 
      command: env # Use 'env' to prepend environment variables
      args:
        # The actual key value will be substituted here from .env in the Python code
        - "FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY}" 
        - npx
        - "-y"
        - firecrawl-mcp
      env: {} # Can be empty if using 'env' command trick

    # Example: Filesystem Server (Stdio)
    filesystem:
      command: npx
      args: 
        - "-y" 
        - "@modelcontextprotocol/server-filesystem"
        - "./relative/path/to/serve" # Argument for the server
      env: {}
      
    # Example: Remote Server (SSE) - Hypothetical
    # remote-service:
    #   url: "https://your-mcp-service.com/sse"
    #   # May require headers for auth, passed during MCPServerSse init
```

### 3. Core Application Logic (Example `app.py` Structure)

```python
import streamlit as st
import os
import asyncio
import yaml 
from dotenv import load_dotenv
from pathlib import Path
import traceback 

# --- VERIFY IMPORTS CAREFULLY ---
# Use BASE Agent/Runner
from agents import Agent, Runner, function_tool 
# MCP Server class - VERIFY this path based on installed package structure
# Example path found to work with agents==0.0.9:
from agents.mcp import MCPServerStdio 
# If using remote servers: from agents.mcp import MCPServerSse 
# If the above fails, explore 'mcp.server', 'mcp.client' or package contents.

# --- Your Custom Tools (Example) ---
# from tools.your_tool import your_tool_function
@function_tool
def dummy_tool(query: str) -> str:
    """A placeholder tool."""
    return f"Dummy tool processed: {query}"

# --- Constants ---
MODEL_NAME = "gpt-4o" # Or your preferred model

# --- Load Config and Env Vars ---
st.set_page_config(page_title="Agent + MCP", layout="wide") # First Streamlit command

load_dotenv(override=True) # Load .env, override existing env vars

# Load API keys needed for Agent and MCP servers
openai_api_key = os.getenv("OPENAI_API_KEY")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
slack_team_id = os.getenv("SLACK_TEAM_ID")
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY") 
# Add checks here for essential keys

# Load MCP Server Definitions from YAML
mcp_config = None
mcp_config_path = Path("mcp_agent.config.yaml")
if mcp_config_path.exists():
    try:
        mcp_config = yaml.safe_load(mcp_config_path.read_text())
        print("DEBUG: Loaded MCP config.")
    except Exception as e:
        print(f"ERROR loading MCP config: {e}")
else:
    print(f"WARNING: MCP config file not found: {mcp_config_path}")

# --- Async Logic Wrapper ---

async def run_agent_with_servers(agent_input: str):
    """Manages MCP server lifecycles and runs the agent."""
    
    active_mcp_servers = [] # List to hold successfully activated server objects
    result = None
    # trace = Trace() # Optional: Requires correct import and usage with Runner.run

    # Get server configs safely
    servers_config = mcp_config.get('mcp', {}).get('servers', {}) if mcp_config else {}
    slack_config = servers_config.get('slack')
    firecrawl_config = servers_config.get('firecrawl-mcp')

    # --- Prepare Server Parameters ---
    # Prepare Slack params (if config and keys exist)
    slack_params = None
    if slack_config and slack_bot_token and slack_team_id:
        env = slack_config.get('env', {}).copy()
        env["SLACK_BOT_TOKEN"] = slack_bot_token
        env["SLACK_TEAM_ID"] = slack_team_id
        slack_params = {
            "command": slack_config.get('command'),
            "args": slack_config.get('args'),
            "env": {k: v for k, v in env.items() if v is not None}
        }
        print("DEBUG: Prepared Slack server params.")

    # Prepare Firecrawl params (if config and key exist)
    firecrawl_params = None
    if firecrawl_config and firecrawl_api_key:
        env = firecrawl_config.get('env', {}).copy()
        # Handle 'env' command substitution
        args = firecrawl_config.get('args', []).copy()
        if args and args[0].startswith("FIRECRAWL_API_KEY="):
             args[0] = f"FIRECRAWL_API_KEY={firecrawl_api_key}"
        firecrawl_params = {
            "command": firecrawl_config.get('command'),
            "args": args,
            "env": {k: v for k, v in env.items() if v is not None}
        }
        print("DEBUG: Prepared Firecrawl server params.")

    # --- Activate Servers and Run Agent ---
    # Use nested async with or asyncio.gather with context managers
    try:
        # Example with nesting (simpler for few servers)
        if slack_params:
            async with MCPServerStdio(name="slack", params=slack_params) as active_slack:
                print("DEBUG: Slack server active.")
                active_mcp_servers.append(active_slack)
                
                if firecrawl_params:
                     async with MCPServerStdio(name="firecrawl-mcp", params=firecrawl_params) as active_fc:
                        print("DEBUG: Firecrawl server active (nested).")
                        active_mcp_servers.append(active_fc)
                        # Agent defined and run with BOTH servers
                        agent = Agent(name="Tutor", model=MODEL_NAME, instructions="Use Slack and Firecrawl tools.", tools=[dummy_tool], mcp_servers=active_mcp_servers)
                        print(f"DEBUG: Agent created with servers: {active_mcp_servers}")
                        result = await Runner.run(starting_agent=agent, input=agent_input) 
                else:
                    # Agent defined and run with ONLY Slack
                    agent = Agent(name="Tutor", model=MODEL_NAME, instructions="Use Slack tools.", tools=[dummy_tool], mcp_servers=active_mcp_servers)
                    print(f"DEBUG: Agent created with servers: {active_mcp_servers}")
                    result = await Runner.run(starting_agent=agent, input=agent_input)
        elif firecrawl_params: # If only Firecrawl is configured
             async with MCPServerStdio(name="firecrawl-mcp", params=firecrawl_params) as active_fc:
                print("DEBUG: Firecrawl server active (standalone).")
                active_mcp_servers.append(active_fc)
                # Agent defined and run with ONLY Firecrawl
                agent = Agent(name="Tutor", model=MODEL_NAME, instructions="Use Firecrawl tools.", tools=[dummy_tool], mcp_servers=active_mcp_servers)
                print(f"DEBUG: Agent created with servers: {active_mcp_servers}")
                result = await Runner.run(starting_agent=agent, input=agent_input)
        else:
            # Agent defined and run with NO MCP servers
            print("DEBUG: No MCP servers configured or activated.")
            agent = Agent(name="Tutor", model=MODEL_NAME, instructions="MCP tools unavailable.", tools=[dummy_tool], mcp_servers=[])
            print(f"DEBUG: Agent created with servers: []")
            result = await Runner.run(starting_agent=agent, input=agent_input)

        print("DEBUG: Agent run finished.")
        # return result, trace # If using trace
        return result, None 
        
    except Exception as e:
        print(f"ERROR during async agent logic: {e}")
        traceback.print_exc() 
        # return None, trace # If using trace
        return None, None

# --- Streamlit UI and Execution Flow ---

st.title("Agent + MCP Integration")
st.caption(f"Powered by {MODEL_NAME} and Agents SDK.")

# Display warnings based on actual loaded keys/config
# ... (UI warnings as implemented previously) ...

# Initialize session state 
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []
# No runner/agent needed in session state

# Display chat history
# ...

# Get user input
if prompt := st.chat_input("Ask the agent..."):
    # ... (Display user message) ...

    agent_input = f"User query: {prompt}"
    try:
        with st.spinner("Agent is thinking..."):
            # Execute the async logic
            result, trace = asyncio.run(run_agent_with_servers(agent_input))

        # Process and display result
        if result:
            final_text = result.final_output or "Agent finished without text output."
        else:
            final_text = "Agent execution failed. Check logs."
        
        st.session_state.display_messages.append({"role": "assistant", "content": final_text})
        with st.chat_message("assistant"):
            st.markdown(final_text)
            # Display trace if implemented and returned
            # if trace and hasattr(trace, 'steps'):
            #     st.expander("Trace").json(trace.steps)

    except Exception as e:
        st.error(f"Error running agent: {e}")
        print(f"ERROR in Streamlit main loop: {e}")
        traceback.print_exc()

```

### 4. Key Debugging Points & Pitfalls Addressed

*   **Import Paths:** `MCPServerStdio`/`MCPServerSse` are likely in `agents.mcp`. Verify this path first when starting a new project. `Agent` and `Runner` should typically come from the base `agents` package.
*   **Server Initialization:** Use the `params={...}` dictionary structure when initializing `MCPServerStdio`. Ensure the `env` dictionary within `params` contains the *actual loaded secret values* from `.env`, not just placeholders. Handle specific command styles like `env VAR=... command ...` by substituting keys into the `args` list.
*   **Server Activation:** `MCPServerStdio` (and likely `MCPServerSse`) *must* be activated using `async with`. The agent needs the *active* server object passed to its `mcp_servers` list. Define the agent *inside* the `async with` block.
*   **Runner Execution:** Use the *static* `Runner.run` method: `await Runner.run(starting_agent=your_agent, input=your_input)`. Do not instantiate the `Runner` with the agent.
*   **Async in Sync:** Use `asyncio.run()` to call your main async logic function from the synchronous Streamlit script flow.
*   **.env Parsing:** Ensure no syntax errors (like trailing commas) in your `.env` file. Use `load_dotenv(override=True)` and debug prints `os.getenv("YOUR_KEY")` to verify loading.
*   **Tracing:** While temporarily removed during debugging, re-enabling `Trace` (importing `Trace`, creating `trace = Trace()`, passing `trace=trace` to `Runner.run`, and displaying `trace.steps` via `st.json`) is valuable.

This updated documentation and structure provide a clear, working pattern for integrating MCP servers using the native Agents SDK components, addressing the specific errors and confusion encountered previously.

## Understanding Model Context Protocol (MCP)

Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to large language models (LLMs). Think of MCP like a USB-C port for AI applications - it acts as a universal connector that enables AI models to interface seamlessly with different data sources and tools[^8].

MCP serves three primary functions:

- **Tools**: Allows models to execute actions like querying databases or sending emails
- **Resources**: Provides structured data such as documents and API responses
- **Prompts**: Offers predefined templates that guide interactions[^7]

Without this standardized approach, each LLM application would require custom integration methods, leading to unnecessary complexity and redundant development. MCP addresses this by providing a common protocol for connecting agents to external resources.

## MCP Server Types and Transport Protocols

The MCP specification defines two primary server types based on their transport mechanisms:

### Local Servers (stdio)

- Run as subprocesses of your application
- Communicate using standard input/output
- Ideal for local tool access
- Use the `MCPServerStdio` class to connect[^8]


### Remote Servers (SSE)

- Run on remote endpoints
- Connect via HTTP over Server-Sent Events (SSE)
- Access cloud-based tools and services
- Use the `MCPServerSse` class to connect[^8][^4]

Each server type employs specific transport protocols:

- **stdio**: Used for communication with local servers
- **SSE**: Used for communication with remote servers[^4]


## Setting Up Your Development Environment

Before integrating MCP with the OpenAI Agents SDK, ensure you have the proper environment set up:

### Basic Installation

```python
# Install the core OpenAI Agents SDK
pip install openai-agents

# For MCP extension
pip install openai-agents-mcp
# or
uv add openai-agents-mcp

# For Node.js based MCP servers
npm install -g npx
```


### Configuration File Setup

Create an `mcp_agent.config.yaml` file to define your MCP server configurations:

```yaml
mcp:
  servers:
    fetch:
      command: npx
      args: ["-y", "@modelcontextprotocol/server-fetch"]
    filesystem:
      command: npx
      args: ["-y", "@modelcontextprotocol/server-filesystem", "."]
```


## Connecting OpenAI Agents to MCP Servers

### Basic Connection Pattern

There are two main approaches to connecting agents with MCP servers:

#### 1. Using Native OpenAI Agents SDK

```python
from agents import Agent
import asyncio
from openai.mcp import MCPServerStdio

# Initialize MCP server
async with MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "./samples_dir"],
    }
) as server:
    # Create agent with MCP server
    agent = Agent(
        name="File Explorer",
        instructions="Help users explore and understand files",
        mcp_servers=[server]
    )
    
    # Run the agent
    await agent.run("List all text files in the directory")
```


#### 2. Using the MCP Extension Package

```python
from agents_mcp import Agent

# Create an agent with specific MCP servers
agent = Agent(
    name="MCP Agent",
    instructions="You are a helpful assistant with access to both local/OpenAI tools and tools from MCP servers.",
    tools=[get_current_weather],  # Local/OpenAI tools
    mcp_servers=["fetch", "filesystem"],  # MCP servers defined in config
)
```


## Using Multiple MCP Servers Simultaneously

You can connect an agent to multiple MCP servers to combine their capabilities:

```python
from agents import Agent, Runner
from openai.mcp import MCPServerStdio

async def main():
    # Initialize filesystem MCP server
    async with MCPServerStdio(
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "./docs"],
        }
    ) as fs_server:
        # Initialize Slack MCP server
        async with MCPServerStdio(
            params={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-slack"],
                "env": {
                    "SLACK_BOT_TOKEN": os.environ["SLACK_BOT_TOKEN"],
                    "SLACK_TEAM_ID": os.environ["SLACK_TEAM_ID"],
                }
            }
        ) as slack_server:
            # Create agent with both servers
            agent = Agent(
                name="Multi-Tool Assistant",
                instructions="You can access files and send Slack messages",
                mcp_servers=[fs_server, slack_server]
            )
            
            # Run the agent
            runner = Runner(agent=agent)
            await runner.run("Find the monthly report and send a summary to the #reports channel")
```


## Building Custom MCP Servers

You can create your own MCP servers to expose custom tools:

```python
# Example of building a custom weather MCP server
# This would typically be a separate Node.js or Python application

# 1. Define your tool schema and functionality
# 2. Create server endpoints that follow MCP specifications
# 3. Expose the tools via stdio or SSE transport
```

For a custom server, you'll need to:

1. Define the tools you want to expose
2. Implement the MCP server interface
3. Set up proper request/response handling
4. Package it for reuse across projects[^4]

## Performance Optimization

### Caching Tool Lists

Every time an Agent runs, it calls `list_tools()` on the MCP server, which can introduce latency, especially for remote servers. To improve performance:

```python
# Enable caching of tool lists
mcp_server = MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "./"],
    },
    cache_tools_list=True  # Enable caching
)
```

Only use caching when you're certain the tool list won't change during execution.

## Debugging and Tracing

The OpenAI Agents SDK provides built-in tracing capabilities that work well with MCP:

```python
from agents import Agent, Trace

# Create agent with tracing
agent = Agent(
    name="Traceable Agent",
    instructions="Use MCP tools to complete tasks",
    mcp_servers=[mcp_server]
)

# Execute with tracing
trace = Trace()
result = await agent.run("Analyze the data in sales.csv", trace=trace)

# Inspect the trace
print(trace.steps)
```

This enables you to visualize and debug your agent's interactions with MCP servers and tools.

## Practical Use Cases

### 1. File System Navigation and Analysis

```python
# Create a file explorer agent
async with MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "./project"],
    }
) as fs_server:
    agent = Agent(
        name="Code Explorer",
        instructions="Help analyze code repositories and generate reports",
        mcp_servers=[fs_server]
    )
    
    await agent.run("Find all Python files over 1000 lines and summarize their main classes")
```


### 2. Web Search and Data Retrieval

```python
# Create an agent that can search the web
async with MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-fetch"],
    }
) as fetch_server:
    agent = Agent(
        name="Research Assistant",
        instructions="Research topics and synthesize information from websites",
        mcp_servers=[fetch_server]
    )
    
    await agent.run("Research recent developments in quantum computing and provide a summary")
```


## Conclusion

Integrating MCP with the OpenAI Agents SDK provides a powerful, standardized way to connect AI agents to external tools and data sources. By following the patterns outlined in this guide, you can create agents that seamlessly interact with file systems, APIs, and custom tools through a unified protocol.

The combination of OpenAI's agent capabilities with MCP's standardized approach to tool integration creates a flexible foundation for building sophisticated AI applications. Whether you're developing simple assistants or complex multi-agent systems, MCP provides the connectivity layer that makes external interactions possible and consistent.

As the ecosystem of MCP servers continues to grow, your agents will gain access to an increasingly diverse set of capabilities without requiring custom integrations for each new tool or service.

<div>⁂</div>

[^1]: https://github.com/lastmile-ai/openai-agents-mcp

[^2]: https://apidog.com/blog/mcp-servers-openai-agents/

[^3]: https://www.prompthub.us/blog/openais-agents-sdk-and-anthropics-model-context-protocol-mcp

[^4]: https://www.youtube.com/watch?v=kQPvwSV0YzI

[^5]: https://openai.github.io/openai-agents-python/

[^6]: https://dev.to/seratch/openai-agents-sdk-multiple-mcp-servers-8d2

[^7]: https://wandb.ai/byyoung3/Generative-AI/reports/Getting-Started-with-MCP-using-OpenAI-Agents---VmlldzoxMjAwNzU5NA

[^8]: https://openai.github.io/openai-agents-python/mcp/

[^9]: https://www.youtube.com/watch?v=e7qvd2bOITc

[^10]: https://news.ycombinator.com/item?id=43485566

[^11]: https://openai.com/index/new-tools-for-building-agents/

[^12]: https://www.youtube.com/watch?v=35nxORG1mtg

[^13]: https://www.youtube.com/watch?v=e7qvd2bOITc

[^14]: https://blog.venturemagazine.net/building-a-multi-agent-homework-system-with-openais-agents-sdk-d6bac962026a

