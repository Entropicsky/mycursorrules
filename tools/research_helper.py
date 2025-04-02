#!/usr/bin/env python3
"""
Research Helper

A simple helper script that makes it easy for an agent to quickly get information on any topic.
This is a wrapper around createdocumentation.py for even easier use.
"""

import sys
import os
from pathlib import Path
import tempfile
import datetime
import re

# Ensure the current directory is in the path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Import the documentation tool
from createdocumentation import create_documentation

def quick_research(query: str, save_to_file: bool = True, output_path: str = None, agent_mode: bool = True) -> str:
    """
    Quickly research a topic and return the results as a string.
    
    Args:
        query: The topic or question to research
        save_to_file: Whether to save the results to a file
        output_path: Optional path to save the research. If None but save_to_file is True,
                     creates a file in the appropriate location.
        agent_mode: If True, automatically saves to .cursor/docs when no output_path is specified
                     
    Returns:
        The research content as a string
    """
    # Determine if this is a question or just a topic
    if "?" in query:
        # It's a question - use it as the objective
        parts = query.split("?", 1)
        topic = parts[0].strip()
        objective = f"answer the question: '{query}'"
    else:
        # It's a topic - create an objective
        topic = query
        objective = f"provide comprehensive information about {topic}"
    
    # Generate a readable filename from the topic/question
    safe_topic = re.sub(r'[^\w\s-]', '', query.lower())
    safe_topic = re.sub(r'[\s-]+', '_', safe_topic)
    safe_topic = safe_topic[:50]  # Limit length
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_topic}_{timestamp}.md"
    
    # Determine where to save the file
    final_output_path = None
    if save_to_file:
        if output_path:
            final_output_path = output_path
        elif agent_mode:
            # When in agent mode, save to .cursor/docs by default
            # First, find the project root (where .cursor exists or could be created)
            project_root = find_project_root()
            docs_dir = project_root / ".cursor" / "docs"
            
            # Ensure the docs directory exists
            docs_dir.mkdir(parents=True, exist_ok=True)
            
            final_output_path = str(docs_dir / filename)
        else:
            # Create a temporary file with a meaningful name
            temp_file = tempfile.NamedTemporaryFile(
                prefix=f"research_{safe_topic[:20]}_",
                suffix=".md",
                delete=False
            )
            final_output_path = temp_file.name
            temp_file.close()
    
    # Run the research
    result = create_documentation(
        topic=topic,
        objective=objective,
        output_path=final_output_path,
        verbose=False,  # Keep it quiet
        show_progress=False  # Don't show streaming output
    )
    
    # Return the content and optionally the file path
    if save_to_file:
        return f"Research saved to: {final_output_path}\n\n{result['content']}"
    else:
        return result['content']

def find_project_root() -> Path:
    """
    Find the project root directory (where .cursor is or should be).
    Starts from the current directory and moves up until it finds .cursor
    or returns the home directory as a fallback.
    """
    # Start with the current working directory
    current_dir = Path.cwd()
    
    # Check if we're already in the .cursor/tools directory
    if current_dir.name == "tools" and current_dir.parent.name == ".cursor":
        return current_dir.parent.parent
    
    # Look for .cursor directory by walking up
    for path in [current_dir] + list(current_dir.parents):
        if (path / ".cursor").exists():
            return path
    
    # Fallback: Use home directory
    return Path.home()

def agent_research(query: str) -> str:
    """
    Special function specifically for agent use.
    Always saves the result to .cursor/docs and returns the content plus the save location.
    
    Args:
        query: The topic or question to research
        
    Returns:
        The research content and save location
    """
    return quick_research(query, save_to_file=True, output_path=None, agent_mode=True)

if __name__ == "__main__":
    # Simple command line interface
    if len(sys.argv) < 2:
        print("Usage: python research_helper.py \"your question or topic here\" [output_file]")
        sys.exit(1)
    
    query = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = quick_research(query, save_to_file=bool(output_file), output_path=output_file, agent_mode=False)
    print(result) 