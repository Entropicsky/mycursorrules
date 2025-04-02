# Research Tool for Agent Use

This document describes how to use the Gemini research tool that's available in the `.cursor/tools` directory. This tool allows you to quickly research any topic or question using Google's Gemini 2.5 Pro model.

## When to Use the Research Tool

Use this tool when you need to:
- Research a technology, library, or framework you're unfamiliar with
- Get up-to-date information about a rapidly changing topic
- Generate comprehensive documentation about an API or tool
- Answer technical questions that require current information
- Create guides or tutorials on specific topics

## How to Use the Research Tool from Python

### Quick Agent Research

The simplest way to use the tool as an agent is with the `agent_research` function:

```python
# Import the tool
from .cursor.tools.research_helper import agent_research

# Research a topic or answer a question
result = agent_research("How does async/await work in JavaScript?")

# The result will include both the content and save location
print(result)  # Will print where it saved the file and the content
```

This automatically:
- Saves the output to `.cursor/docs` with a timestamped filename
- Creates the `.cursor/docs` directory if it doesn't exist
- Returns both the content and the save location

### Custom Research Options

For more control, use the `quick_research` function:

```python
from .cursor.tools.research_helper import quick_research

# Return the content without saving
content = quick_research(
    "React hooks best practices", 
    save_to_file=False,
    agent_mode=True  # Still defaults to agent mode
)

# Save to a specific location
result = quick_research(
    "GraphQL vs REST API", 
    output_path=".cursor/docs/api_comparison.md"
)
```

### Advanced Documentation Generation

For the most control, use the original documentation generator:

```python
from .cursor.tools.createdocumentation import create_documentation

result = create_documentation(
    topic="MongoDB aggregation pipeline",
    objective="create a comprehensive reference guide with examples",
    output_path=".cursor/docs/mongodb_aggregation.md",
    verbose=True,
    show_progress=True  # Shows content as it's generated
)
```

## Command Line Usage

You can also run the tools directly from the command line:

```bash
# Quick research
python .cursor/tools/research_helper.py "What is the OpenAI Assistants API?" .cursor/docs/openai_assistants.md

# Full documentation generator
python .cursor/tools/createdocumentation.py --topic "Docker" --objective "create a beginner's guide" --output ".cursor/docs/docker_guide.md" --stream
```

## Important Tips

1. **API Key**: The tool requires a Gemini API key set as `GEMINI_API_KEY` or `GOOGLE_API_KEY` in the environment.

2. **Project Integration**: When generating documentation for the current project, consider saving to a project-specific docs location (like `docs/` or `.cursor/docs/`) and referencing it in your README.

3. **Importing**: The tools have path-handling logic, but you may need to adjust imports based on your current working directory.

4. **Large Documentation**: For very comprehensive documentation, consider setting specific objectives rather than general topics to focus the research.

5. **Response Time**: Generating detailed documentation can take 30-120 seconds or more depending on the topic complexity.

## Examples of Good Queries

- "How do I implement server-sent events in FastAPI?"
- "What are the best practices for React state management in 2025?"
- "Explain the OAuth 2.0 authorization flow with diagrams"
- "TypeScript advanced type system features tutorial"
- "Generate a quickstart guide for the AWS Lambda SDK" 