# Tools Documentation

## createdocumentation.py

A powerful documentation generation tool that leverages Google's Gemini 2.5 Pro model to create comprehensive research on any topic. This tool is designed to be used both from the command line and programmatically from other Python scripts.

### Using as an Imported Tool

You can import the tool in your Python scripts to generate documentation programmatically:

```python
import sys
import os
from pathlib import Path

# Add .cursor/tools to the Python path if needed
tools_path = Path(__file__).parent.parent / ".cursor" / "tools"
sys.path.append(str(tools_path))

# Import the tool
from createdocumentation import create_documentation

# Use the tool
result = create_documentation(
    topic="FastAPI",
    objective="create a REST API tutorial",
    output_path="fastapi_docs.md",  # Optional
    show_progress=True,             # Optional
    verbose=True                    # Optional
)

# The result is a dictionary containing:
# - 'content': The generated documentation text
# - 'topic': The researched topic
# - 'objective': The research objective
# - 'output_path': The file path where the content was saved (if provided)
# - 'execution_time_seconds': How long the generation took
# - 'timestamp': When the documentation was generated

# You can use the content directly:
documentation_text = result['content']
print(f"Generated {len(documentation_text)} characters of documentation")
```

### Command Line Usage

The tool can also be used directly from the command line:

```bash
python .cursor/tools/createdocumentation.py --topic "Python asyncio" --objective "create a practical guide" --output "asyncio_guide.md" --stream
```

#### Command Line Options

- `--topic`, `-t`: Main topic to research
- `--objective`, `-o`: Research objective
- `--output`, `-f`: Output file path (default: research_result.md)
- `--model`, `-m`: Gemini model to use (default: gemini-2.5-pro-exp-03-25)
- `--api-key`, `-k`: Gemini API key (if not set in environment)
- `--verbose`, `-v`: Enable verbose output
- `--stream`, `-s`: Show content as it's generated in real-time

#### Interactive Mode

Run without topic and objective to use interactive mode:

```bash
python .cursor/tools/createdocumentation.py
```

### Requirements

The tool requires:
- Google Generative AI Python SDK (`google-generativeai`)
- A valid Gemini API key set as `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable

### API Keys

Ensure the Gemini API key is available in the environment. You can set it:
- In a `.env` file at the project root
- As an environment variable: `export GEMINI_API_KEY=your_key_here`
- Pass it directly via the `api_key` parameter when using programmatically

### Example Use Cases

- Generate technical documentation for APIs or libraries
- Create tutorials and guides for programming concepts
- Research and document best practices for development workflows
- Generate summaries of technical papers or documentation

## chat_summary_tool.py

A single, self-contained tool for summarizing SpecStory chat history using Google's Gemini models. This tool generates concise summaries of recent chat sessions to help AI agents maintain context across sessions, improving continuity and knowledge retention.

### Features

- Summarizes the latest chat history or multiple recent chats
- Saves summaries to `.cursor/chat_summary/` directory with timestamps
- Retrieves existing summaries
- Provides a startup mode that automatically retrieves the latest summary or generates one
- Handles large chat histories by truncating content when necessary
- Includes detailed error handling and debug logging

### Command Line Usage

The tool can be used directly from the command line:

```bash
# Generate summary for the latest chat
python tools/chat_summary_tool.py --latest

# Generate summary for the 3 most recent chats
python tools/chat_summary_tool.py --recent 3

# Get the most recent summary
python tools/chat_summary_tool.py --get

# Show debug information
python tools/chat_summary_tool.py --latest --debug

# Save summary to a specific file
python tools/chat_summary_tool.py --latest --output my_summary.md

# Run startup summary (default behavior)
python tools/chat_summary_tool.py
```

#### Command Line Options

- `--latest`, `-l`: Summarize the latest chat
- `--recent N`, `-r N`: Summarize N recent chats (default: 3)
- `--get`, `-g`: Get the latest existing summary
- `--startup`, `-s`: Run startup sequence for new agent sessions
- `--output PATH`, `-o PATH`: Output file path for the summary
- `--debug`, `-d`: Enable debug messages

### Requirements

The tool requires:
- Google Generative AI Python SDK (`google-generativeai`)
- Python-dotenv (optional, for loading environment variables from `.env`)
- A valid Gemini API key set as `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable

### Integration with Agent Workflows

This tool is particularly useful for:

1. **Agent Session Startup**: Run at the beginning of a new agent session to get context from previous sessions
2. **Context Management**: Maintain a history of conversation summaries for long-running projects
3. **Knowledge Handover**: Generate summaries when switching between different AI agents or human collaborators

### Example Programmatic Usage

You can also import and use the tool programmatically:

```python
import sys
from pathlib import Path

# Add tools directory to path if needed
tools_path = Path("/path/to/tools")
sys.path.append(str(tools_path))

from chat_summary_tool import summarize_latest_chat, summarize_recent_chats, get_latest_summary

# Get a summary of the latest chat
summary = summarize_latest_chat(debug=True)

# Or summarize the 3 most recent chats
multi_summary = summarize_recent_chats(count=3)

# Or get the latest existing summary
latest = get_latest_summary()
``` 