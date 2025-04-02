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