#!/usr/bin/env python3
"""
Chat Summary Tool

A single, self-contained tool for summarizing SpecStory chat history using Gemini.
Use this to generate concise summaries of recent chat sessions to help agents
maintain context across sessions.

Examples:
    # Generate summary for the latest chat
    python chat_summary_tool.py --latest
    
    # Generate summary for the 3 most recent chats
    python chat_summary_tool.py --recent 3
    
    # Get the most recent summary
    python chat_summary_tool.py --get
    
    # Show debug information
    python chat_summary_tool.py --latest --debug
    
    # Save summary to a specific file
    python chat_summary_tool.py --latest --output my_summary.md
    
    # Run startup summary (default behavior)
    python chat_summary_tool.py
"""

import sys
import os
from pathlib import Path
import datetime
import argparse
from typing import Optional, Dict, Any, Union

print("Starting imports...")

# Import Google's generative AI library
genai = None
genai_client = None
types_module = None

try:
    import google.generativeai as genai
    print("Successfully imported google.generativeai")
except ImportError as e:
    print(f"Error importing google.generativeai: {e}")
    print("Google Generative AI package not found. Please install with:")
    print("pip install google-generativeai")
    sys.exit(1)

try:
    from google import genai as genai_client
    print("Successfully imported google.genai as genai_client")
except ImportError as e:
    print(f"Error importing google.genai: {e}")
    genai_client = None

try:
    from google.genai import types as types_module
    print("Successfully imported google.genai.types")
except ImportError as e:
    print(f"Error importing google.genai.types: {e}")
    types_module = None

# Try to import dotenv for loading environment variables from .env file
try:
    from dotenv import load_dotenv
    print("Successfully imported dotenv")
except ImportError:
    print("Warning: python-dotenv not found. Environment variables must be set manually.")
    # Define a simple placeholder if dotenv is not available
    def load_dotenv(path=None):
        print("Warning: python-dotenv not found. Environment variables must be set manually.")
        return False

#----------------------------------------
# Utility Functions
#----------------------------------------

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

def load_api_key() -> Optional[str]:
    """
    Load the Gemini API key from environment variables or .env file.
    
    Returns:
        The API key if found, None otherwise
    """
    # First check if the key is already in environment variables
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if api_key:
        return api_key
        
    # If not, try to load from .env file
    # Find the project root
    project_root = find_project_root()
    
    # Path to the .env file
    env_path = project_root / ".env"
    
    # Check if the .env file exists
    if env_path.exists():
        # Load the .env file
        load_dotenv(dotenv_path=env_path)
        
        # Get the API key
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    return api_key

def find_chat_history_files() -> list[Path]:
    """
    Find all chat history files in .specstory/history/
    
    Returns:
        List of paths to chat history files sorted by modification time (newest first)
    """
    # Find the project root
    project_root = find_project_root()
    history_dir = project_root / ".specstory" / "history"
    
    # Check if the history directory exists
    if not history_dir.exists():
        raise FileNotFoundError(f"SpecStory history directory not found: {history_dir}")
    
    # Find all markdown files in the history directory
    history_files = list(history_dir.glob("*.md"))
    
    # If no history files found, raise an error
    if not history_files:
        raise FileNotFoundError(f"No chat history files found in {history_dir}")
    
    # Sort by modification time, newest first
    return sorted(history_files, key=lambda p: p.stat().st_mtime, reverse=True)

def read_chat_history(file_path: Path) -> str:
    """
    Read the content of a chat history file
    
    Args:
        file_path: Path to the chat history file
        
    Returns:
        Content of the chat history file
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def ensure_summary_dir() -> Path:
    """
    Ensure the chat summary directory exists
    
    Returns:
        Path to the chat summary directory
    """
    project_root = find_project_root()
    summary_dir = project_root / ".cursor" / "chat_summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    return summary_dir

#----------------------------------------
# Gemini Integration
#----------------------------------------

def summarize_with_gemini(
    content: Union[str, Path],
    topic: str = "Chat History Summary",
    model: str = "gemini-2.5-pro-exp-03-25",
    debug: bool = False,
) -> str:
    """
    Generate a summary using Gemini.
    
    Args:
        content: Text content to summarize or Path to a file
        topic: Topic of the summary
        model: Gemini model to use
        debug: Whether to print debug messages
        
    Returns:
        The generated summary as a string
    """
    # Get API key (with debugging)
    api_key = load_api_key()
    if not api_key:
        # Provide debug info
        if debug:
            print("DEBUG: No API key found in environment or .env")
            print("  - Checked env vars: GEMINI_API_KEY, GOOGLE_API_KEY")
            print("  - Checked .env file at project root")
        
        # Use a fallback API key or provide instructions
        try:
            # Try to get it directly from .env file
            env_path = find_project_root() / ".env"
            if env_path.exists():
                with open(env_path, "r") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            api_key = line.strip().split("=", 1)[1].strip('"\'')
                            if debug:
                                print(f"DEBUG: Found key in .env directly")
                            break
        except Exception as e:
            if debug:
                print(f"DEBUG: Error reading .env directly: {e}")
                
        if not api_key:
            # Still no key found, provide clear error message
            raise ValueError("No Gemini API key found. Please set GEMINI_API_KEY in your environment or .env file.")
    
    # Initialize the Gemini client using the legacy API that's available
    if debug:
        print(f"DEBUG: Using Gemini API with model: {model}")
    
    genai.configure(api_key=api_key)
    
    # Determine if we're working with a file path or text content
    is_file = isinstance(content, Path)
    
    # If it's a file, read the content
    if is_file:
        if debug:
            print(f"DEBUG: Reading file content: {content}")
        with open(content, "r", encoding="utf-8") as f:
            file_content = f.read()
        content_preview = file_content[:10000]  # First 10000 chars
        if len(file_content) > 10000:
            content_preview += f"\n\n[...truncated - total length: {len(file_content)} characters]"
    else:
        # Create a condensed version of the content if it's too long
        content_preview = content[:10000]  # First 10000 chars
        if len(content) > 10000:
            content_preview += f"\n\n[...truncated - total length: {len(content)} characters]"
    
    # Build the prompt text
    prompt = f"""Today is: {datetime.date.today()}
    
Task: Analyze the provided Cursor AI chat history and create a comprehensive summary.

CONTENT TO SUMMARIZE:
```
{content_preview}
```

Your summary should be structured in markdown format and include:
1. Main topics and questions discussed
2. Key decisions made
3. Code changes implemented or solutions provided
4. Technical problems solved
5. Architecture and design choices
6. Any ongoing issues or next steps identified

Focus on technical details that would be most valuable for a new agent session.
Include relevant code snippets, file names, and technical concepts if mentioned.
Format the summary with clear sections and bullet points for readability.

Start with a brief overview paragraph followed by well-organized sections.
"""

    # Setup the model and generate with streaming
    model_obj = genai.GenerativeModel(model_name=model)
    if debug:
        print(f"DEBUG: Created model, generating content...")
    
    # Generate content with streaming to handle larger outputs
    all_text = ""
    
    try:
        # Stream the response
        response = model_obj.generate_content(prompt, stream=True)
        for chunk in response:
            if hasattr(chunk, 'text') and chunk.text:
                all_text += chunk.text
    except Exception as e:
        if debug:
            print(f"DEBUG: Error during content generation: {str(e)}")
            import traceback
            traceback.print_exc()
        return f"Error generating summary: {str(e)}"
    
    if not all_text and debug:
        print("DEBUG: No response text received from Gemini")
    
    return all_text

#----------------------------------------
# Core Functionality
#----------------------------------------

def summarize_latest_chat(output_path: Optional[str] = None, debug: bool = False) -> str:
    """
    Summarize the latest chat history and save to the specified location or default.
    
    Args:
        output_path: Optional specific path to save the summary
        debug: Whether to print debug messages
        
    Returns:
        The summary content and save location
    """
    try:
        # Find the latest chat history file
        latest_file = find_chat_history_files()[0]
        if debug:
            print(f"DEBUG: Found latest chat history file: {latest_file.name}")
        
        # Generate the summary using the file directly
        summary = summarize_with_gemini(latest_file, debug=debug)
        if debug:
            print(f"DEBUG: Generated summary, size: {len(summary)} chars")
        
        # Save to file if needed
        if output_path:
            summary_path = output_path
        else:
            # Generate a filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_summary_{timestamp}.md"
            summary_dir = ensure_summary_dir()
            summary_path = str(summary_dir / filename)
        
        # Write the summary to file
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
        if debug:
            print(f"DEBUG: Wrote summary to file: {summary_path}")
        
        return f"Chat history summary saved to: {summary_path}\n\n{summary}"
    except Exception as e:
        print(f"Error summarizing chat history: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()
        return f"Error summarizing chat history: {str(e)}"

def summarize_recent_chats(count: int = 3, output_path: Optional[str] = None, debug: bool = False) -> str:
    """
    Summarize the most recent chat histories and save to a single file.
    
    Args:
        count: Number of recent chat history files to summarize
        output_path: Optional specific path to save the summary
        debug: Whether to print debug messages
        
    Returns:
        The summary content and save location
    """
    try:
        # Find the recent chat history files
        recent_files = find_chat_history_files()[:count]
        if debug:
            print(f"DEBUG: Found {len(recent_files)} recent chat history files")
        
        # For multiple files, we need to combine them with text markers
        # as the file upload approach can only handle one file at a time
        if len(recent_files) > 1:
            # Create a temporary combined file
            temp_dir = Path(os.path.join(find_project_root(), ".cursor", "temp"))
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_file = temp_dir / f"combined_chats_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            # Combine all content with clear markers
            with open(temp_file, "w", encoding="utf-8") as f:
                for i, file_path in enumerate(recent_files):
                    content = read_chat_history(file_path)
                    if debug:
                        print(f"DEBUG: Read chat history {i+1}: {file_path.name} ({len(content)} chars)")
                    f.write(f"### Chat Session {i+1}: {file_path.name}\n\n{content}\n\n")
                    if i < len(recent_files) - 1:
                        f.write("\n\n---\n\n")
            
            if debug:
                print(f"DEBUG: Created temporary combined file: {temp_file}")
            
            # Use the combined file for summarization
            summary = summarize_with_gemini(temp_file, debug=debug)
            
            # Clean up the temporary file
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    if debug:
                        print(f"DEBUG: Removed temporary file: {temp_file}")
            except Exception as e:
                if debug:
                    print(f"DEBUG: Failed to remove temporary file: {e}")
        else:
            # For a single file, use it directly
            file_path = recent_files[0]
            if debug:
                print(f"DEBUG: Using single file: {file_path.name}")
            summary = summarize_with_gemini(file_path, debug=debug)
        
        if debug:
            print(f"DEBUG: Generated summary, size: {len(summary)} chars")
        
        # Save to file if needed
        if output_path:
            summary_path = output_path
        else:
            # Generate a filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"multi_chat_summary_{timestamp}.md"
            summary_dir = ensure_summary_dir()
            summary_path = str(summary_dir / filename)
        
        # Write the summary to file
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
        if debug:
            print(f"DEBUG: Wrote summary to file: {summary_path}")
        
        return f"Multi-chat summary saved to: {summary_path}\n\n{summary}"
    except Exception as e:
        print(f"Error summarizing recent chat histories: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()
        return f"Error summarizing recent chat histories: {str(e)}"

def get_latest_summary(debug: bool = False) -> str:
    """
    Get the most recent chat summary from .cursor/chat_summary/
    
    Args:
        debug: Whether to print debug messages
    
    Returns:
        Content of the most recent chat summary
    """
    try:
        # Ensure summary directory exists
        summary_dir = ensure_summary_dir()
        
        # Find all markdown files in the summary directory
        summary_files = list(summary_dir.glob("*.md"))
        
        # If no summary files found, generate one
        if not summary_files:
            if debug:
                print("DEBUG: No existing summaries found")
            print("No existing summaries found. Generating a new one...")
            return summarize_latest_chat(debug=debug)
        
        # Sort by modification time, newest first
        latest_file = max(summary_files, key=lambda p: p.stat().st_mtime)
        if debug:
            print(f"DEBUG: Found latest summary: {latest_file.name}")
        
        # Read the content
        with open(latest_file, "r", encoding="utf-8") as f:
            content = f.read()
        if debug:
            print(f"DEBUG: Read summary, size: {len(content)} chars")
        
        return f"Latest chat summary ({latest_file.name}):\n\n{content}"
    except Exception as e:
        print(f"Error retrieving latest summary: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()
        return f"Error retrieving latest summary: {str(e)}"

def startup_summary(debug: bool = False):
    """
    Function to run at agent startup - get or generate summary
    
    Args:
        debug: Whether to print debug messages
    """
    print("\n=== AGENT SESSION STARTUP ===\n")
    
    try:
        # Try to get existing summary or generate new one
        summary_dir = ensure_summary_dir()
        summary_files = list(summary_dir.glob("*.md"))
        
        if summary_files:
            # Get the latest summary
            if debug:
                print("DEBUG: Found existing summaries, getting latest")
            print(get_latest_summary(debug=debug))
        else:
            # Generate a new summary
            if debug:
                print("DEBUG: No existing summaries found")
            print("No existing summaries found. Generating a new one...")
            print(summarize_latest_chat(debug=debug))
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()
        
    print("\n=== END OF STARTUP SUMMARY ===\n")

#----------------------------------------
# Command Line Interface
#----------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SpecStory Chat History Summarizer")
    
    # Main action group
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("--latest", "-l", action="store_true", help="Summarize the latest chat")
    action_group.add_argument("--recent", "-r", type=int, nargs="?", const=3, help="Summarize N recent chats (default: 3)")
    action_group.add_argument("--get", "-g", action="store_true", help="Get the latest existing summary")
    action_group.add_argument("--startup", "-s", action="store_true", help="Run startup sequence for new agent sessions")
    
    # Additional options
    parser.add_argument("--output", "-o", help="Output file path for the summary")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug messages")
    
    args = parser.parse_args()
    
    try:
        # Handle actions based on arguments
        if args.latest:
            print(summarize_latest_chat(output_path=args.output, debug=args.debug))
        elif args.recent is not None:
            print(summarize_recent_chats(count=args.recent, output_path=args.output, debug=args.debug))
        elif args.get:
            print(get_latest_summary(debug=args.debug))
        elif args.startup:
            startup_summary(debug=args.debug)
        else:
            # Default to startup if no arguments provided
            startup_summary(debug=args.debug)
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc() 