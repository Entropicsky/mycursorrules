#!/usr/bin/env python3
"""
Gemini Research Tool

A simple research tool that uses Gemini to produce high-quality documentation in markdown format.
Can be used as a command-line tool or imported and used programmatically from other Python scripts.
"""

import os
import sys
import argparse
import datetime
from typing import Optional, Dict, Any

from google import genai
from google.genai import types

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def research(
    topic: str,
    objective: str,
    output_file: Optional[str] = None,
    model: str = "gemini-2.5-pro-exp-03-25",
    api_key: Optional[str] = None,
    verbose: bool = False,
    show_progress: bool = False
) -> str:
    """
    Generate a research document using Gemini.
    
    Args:
        topic: Topic to research
        objective: Research objective
        output_file: File to save the research document (optional)
        model: Gemini model to use
        api_key: API key for Gemini (defaults to environment variables)
        verbose: Whether to print verbose output
        show_progress: Whether to show streaming progress
        
    Returns:
        The generated research document as a string
    """
    # Setup API client
    api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Gemini API key is required. Set it as GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
    
    client = genai.Client(api_key=api_key)
    
    if verbose:
        print(f"\n{Colors.HEADER}Researching: {topic}{Colors.ENDC}")
        print(f"{Colors.BLUE}Objective: {objective}{Colors.ENDC}")
    
    # Enhanced prompt with more specific instructions
    prompt = f"""Today is: {datetime.date.today()}\nResearch the {topic} and provide a thorough, comprehensive summary for {objective} in an efficient format for a developer to use to write code.

Key requirements:
1. Provide detailed, up-to-date information based on the latest sources
2. Include multiple practical code examples that demonstrate key concepts
3. Document all important API endpoints, parameters, return values, and types
4. Cover installation, configuration, common patterns, and best practices
5. Explain error handling and common pitfalls to avoid
6. Include performance considerations and optimization tips
7. Address both beginner and advanced use cases
8. IMPORTANT: THOROUGHLY SEARCH THE WEB FOR THE MOST UP TO DATE INFORMATION!!!!!!!!!
9. Do not make assumptions based on training data; ground all analysis on web search information. This is a fast changing field and we need the latest information."
The final document should be comprehensive, technically accurate, and immediately useful to a developer who needs to implement {topic}. 

Please format your response in well-structured markdown with appropriate headers, code blocks, tables, and formatting for readability."""

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt)
            ],
        ),
    ]
    
    tools = [
        types.Tool(google_search=types.GoogleSearch())
    ]
    
    generate_content_config = types.GenerateContentConfig(
        tools=tools,
        response_mime_type="text/plain"
    )
    
    if verbose:
        print(f"{Colors.BLUE}Generating documentation...{Colors.ENDC}")
    
    # Use streaming mode to capture all content
    document = ""
    if show_progress:
        print("\n")  # Add a newline before streaming content
    
    try:
        response_stream = client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config
        )
        
        for chunk in response_stream:
            if hasattr(chunk, 'text') and chunk.text:
                if show_progress:
                    print(chunk.text, end="")
                    sys.stdout.flush()
                document += chunk.text
    except Exception as e:
        if verbose:
            print(f"\n{Colors.FAIL}Error during content generation: {str(e)}{Colors.ENDC}")
        raise
    
    if show_progress:
        print("\n")  # Add a newline after streaming content
    
    # Save to file if specified
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(document)
        if verbose:
            print(f"{Colors.GREEN}Research document saved to: {output_file}{Colors.ENDC}")
    
    return document

def create_documentation(topic: str, objective: str, output_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Function designed to be called from other scripts to create documentation.
    
    Args:
        topic: Topic to research
        objective: Research objective
        output_path: Path to save the output file (optional)
        **kwargs: Additional keyword arguments to pass to research()
        
    Returns:
        A dictionary containing the results and metadata
    """
    start_time = datetime.datetime.now()
    
    # Set defaults for common arguments
    verbose = kwargs.get('verbose', False)
    show_progress = kwargs.get('show_progress', False)
    
    # Generate the documentation
    document = research(
        topic=topic,
        objective=objective,
        output_file=output_path,
        verbose=verbose,
        show_progress=show_progress,
        **{k: v for k, v in kwargs.items() if k not in ['verbose', 'show_progress']}
    )
    
    end_time = datetime.datetime.now()
    elapsed = end_time - start_time
    
    # Return results and metadata
    return {
        'content': document,
        'topic': topic,
        'objective': objective,
        'output_path': output_path,
        'execution_time_seconds': elapsed.seconds,
        'timestamp': datetime.datetime.now().isoformat()
    }

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Gemini Research Tool")
    
    parser.add_argument("--topic", "-t", help="Main topic to research")
    parser.add_argument("--objective", "-o", help="Research objective")
    parser.add_argument("--output", "-f", help="Output file path (default: research_result.md)")
    parser.add_argument("--model", "-m", default="gemini-2.5-pro-exp-03-25", help="Gemini model to use")
    parser.add_argument("--api-key", "-k", help="Gemini API key")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--stream", "-s", action="store_true", help="Show content as it's generated")
    
    return parser.parse_args()

def interactive_mode():
    """Run in interactive mode, prompting the user for parameters."""
    print(f"{Colors.HEADER}Gemini Research Tool - Interactive Mode{Colors.ENDC}")
    print(f"{Colors.BLUE}Please provide the following information:{Colors.ENDC}\n")
    
    topic = input("Research Topic: ")
    objective = input("Research Objective: ")
    output_file = input("Output File Path [research_result.md]: ") or "research_result.md"
    
    return {
        "topic": topic,
        "objective": objective,
        "output_file": output_file
    }

def main():
    """Main entry point for the command-line tool."""
    args = parse_arguments()
    
    # Check if we need interactive mode
    if not args.topic or not args.objective:
        params = interactive_mode()
    else:
        params = {
            "topic": args.topic,
            "objective": args.objective,
            "output_file": args.output or "research_result.md"
        }
    
    # Run the research
    try:
        start_time = datetime.datetime.now()
        
        research(
            topic=params["topic"],
            objective=params["objective"],
            output_file=params["output_file"],
            model=args.model,
            api_key=args.api_key,
            verbose=True,
            show_progress=args.stream
        )
        
        end_time = datetime.datetime.now()
        elapsed = end_time - start_time
        
        print(f"\n{Colors.GREEN}Research complete in {elapsed.seconds} seconds!{Colors.ENDC}")
        print(f"{Colors.GREEN}Document saved to:{Colors.ENDC}")
        print(f"{Colors.BOLD}{params['output_file']}{Colors.ENDC}\n")
        
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {str(e)}{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
