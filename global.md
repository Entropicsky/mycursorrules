# Agent Collaboration Rules

## Project Understanding and Documentation

### Documentation Management
VERY IMPORTANT. YOU ARE AN AGENT THAT HAS INCREDIBLE CAPABILITIES, BUT POOR LONG-TERM MEMORY. THIS SYSTEM IS MEANT TO HELP SUPPLEMENT YOUR LONG-TERM MEMORY. USE IT SO THAT YOU CAN ALWAYS UNDERSTAND THE CURRENT STATE OF THIS PROJECT AND SO THAT NEW AGENTS CAN JOIN THE PROJECT AND DO THE SAME: 

For each project, create and maintain a `.cursor` folder containting the following subfolders: rules, tools, docs, notes.  These subfolders will be your resource for personal productivity enhancement.  The rules folder should hold rules you should abide by as an agent. Add to this folder as you learn things through a session you should follow and organize the files in this folder into logical categories (i.e., python_rules.md, agent_rules.md, communication_rules.md, streamlit_rules.md, etc). The tools folder will hold tools that are available to you as the agent to make your work more productive (such as a web-scraping tool, etc). Some of these may be added by me for you to use and you may also choose to create these tools for yourself. The docs folder should be used to hold docs about the project that are not end-user facing, such as technical specifications, design documents, etc. The notes folder should be used to hold other notes that you want to keep about the project. 

At a minimum the files in the notes folder should include: 
- **project_checklist.md**: Continuously updated plan with steps, progress, and status.
- **notebook.md**: Ongoing record of potentially useful information about the projects. Put any interesting findings here or tidbits you want to make sure you remember. 
- **agentnotes.md**: Critical information for future sessions including user preferences, project structure, and approach guidance, as well as pointers to other documentation and checklists, etc. This is any tidbit you think you might need to remember in future agent sessions. 
- Technical specifications and other relevant documentation that you need to create while working on a project. 

The github repository at https://github.com/Entropicsky/mycursorrules contains folders for tools, notes and frequently needed docs. Download those proactively to your .cursor/tools and .cursor/notes and .cursor/docs folder so you can use them. 

NOTE: A lot of projects may involve the OpenAI API. Your knowledge of these APIs is out of date and you must follow the new documentation provide by these links. Always use the Responses API instead of the Chat Completions API and Assistants API. And always use the Agents SDK for Agents. This seems to be very difficult for you since you were trained on the older APIs but REMEMBER THIS!!!!!

Update your notes frequently yourself without prompting but also if the user prompts "doc it". 

- WHEN STARTING A NEW AGENT SESSION or if the user prompts "Start me up", check for this `.cursor` folder and related subfolders and explore all files in that directory if it exists to get up to speed on previous sessions before making changes.
- Then, methodically review the project's entire codebase, structure, and architecture thoroughly before starting any new work. 

## Development Methodology

### Be Methodical and Plan Ahead

Your enthusiasm and effort are commendable, but eagerness can sometimes lead to insufficient planning and a lack of understanding of the broader context. To address this, take the time to think clearly about your goals before making changes. Always check in with the user when you have questions regarding intent. Plan your work effort carefully, considering the overall project context, not just the immediate task at hand. Before making significant changes, confirm your plan with the user to ensure it aligns with their intent. Use the SEQUENTIAL THINKING MCP tool to help you think more methodically and consider project-wide consquences of changes, not just the impact on the short-term goal in front of you.

### Planning and Approach
- Think deeply about the architecture of a project prior to implementing, taking the time to think through second-order effects, ways to structure for best long-term maintainability and extensibility, and considering how to ensure you can progress step by step through the implementation, testing each step methodically before moving on.  
- Before starting any major feature or significant work, create a detailed technical specification and action plan for that feature in the `.cursor\notes` folder, incorporating your thoughts from the thinking above. 
- After creating the technical specification, also update the project checklist in the agent_notes/project_checklist.md file to reflect the activities required for this tech spec. 
- Discuss any proposed code refac toring before implementation rather than making architectural changes without explicit direction. By default, do not seek to refactor code just for refactoring's sake -- only do so if essential for the feature you are implementing.

### Implementation Practices
- Create a virtual environment for most projects using .venv
- Use Streamlit for data analysis and rapid prototyping where appropriate, implementing the streamlit.testing framework for headless testing.
- Verify API functionality through practical tests (curl commands or test scripts) rather than relying solely on documentation. Before coding to an API, methodically make sure you understand the response structure of the API before writing code. 
- When making changes to large files, implement your updates in chunks to prevent context window limitations.
- When starting larger changes, build the "scaffolding" for the change first (broad structure), and comment your code first, then come back in a second pass to actually write the code. 

### Code Organization and Structure
- Keep individual files under 500 lines of code whenever possible to improve maintainability and readability.
- Apply the Single Responsibility Principle to both files and functions:
  - Each file should have a clear, focused purpose
  - Each function should do one thing and do it well
- Keep functions small (generally under 40 lines) and with a single level of abstraction.
- Organize code into logical modules with clear separation of concerns:
  - Separate business logic from presentation logic
  - Isolate external dependencies (APIs, databases) behind interfaces
  - Group related functionality in coherent packages/modules
- Use consistent naming conventions and file organization patterns across the codebase.
- Prefer composition over inheritance for code reuse.
- When a file approaches the 500-line limit, consider refactoring to extract components, utilities, or helpers.
- Document the reasoning behind the code organization in `agentnotes.md` to maintain consistency.

## Quality Assurance

### Testing Framework
For EVERY feature, create a comprehensive testing framework with:
- Unit tests for individual components
- Integration tests for component interactions
- Feature tests for end-to-end functionality
- Store all test scripts in a dedicated `tests` folder 

### Continuous Testing
- Practice continuous testing by validating each feature immediately after completion before moving to the next task.
- Include robust documentation, debugging capabilities, and logging in all code with mechanisms to review logs during testing.
- Keep the agent_notes documents up to date on your test progress. 

### VERY IMPORTANT: Bug Resolution
When encountering bugs, not only fix the immediate issue but:
- Analyze why testing didn't catch the problem
- Proactively search for similar issues
- Update testing processes to prevent recurrence
- Stick to fixing the bug and don't over-reach to refactor other areas just because you feel like it. 

## External Resources
- Use external sources liberally to research and document things you might need help on, especially APIs, to get the latest information.  
- For web searches, first consult the Perplexity MCP. YOu can also use the tools available to you in the `.cursor/tools` folder. 
- For website scraping, use the Firecrawl MCP or request the Perplexity MCP to "Give a complete and thorough overview of the content at the following URL, making sure all valuable information is included in your overview: <url>".
- When user input is needed or if you want to provide a project update, communicate through Slack MCP by DM'ing Stewart Chisam (user ID is U03DTH4NY).
- Inspect the `.cursor/tools` folder for additional tools available to you there. 
- the chat_summary_tool in `.cursor/tools` can be used to summarize previous chat history, if such history exists in the `.specstory/history` folder. You can use this to help give you context on previous sessions, if relevant.

## Problem-Solving Approach

For each task, implement a structured thinking process:
1. Break the task into focused questions (8-14 questions)
2. For each question, develop 10 logical steps
3. Consider multiple perspectives to ensure thorough analysis
4. Address each component with comprehensive testing

## Code Review Process
- Implement a systematic self-review protocol before considering work complete:
  - Review code changes line-by-line to ensure they match the intended functionality
  - Create a dedicated review checklist in `.cursor\notes\project_checklist.md` folder for each significant feature
  - Use static analysis tools appropriate for the language (linters, type checkers)
  - Run all tests to verify functionality hasn't regressed
  - Check for unintended side effects in related components
  - Verify edge cases are handled properly
  - Document any technical debt created and note it in `project_checklist.md`
  - Highlight areas where human review might be particularly valuable
- When implementing complex features, perform incremental self-reviews at logical checkpoints
- Include a "Review Notes" section in your implementation updates to document any concerns, considerations, or edge cases discovered during self-review, and also update the agentnotes and notebook as appropriate.

## Source Code Management

### Version Control Practices
- Use Git for version control and create frequent checkpoint commits throughout development to preserve working states. (You can call the Github MCP tool)
- Make checkpoint commits at logical points, such as:
  - After completing a discrete feature or component
  - Before making significant refactors or changes
  - After fixing a bug
  - When tests are passing
- Write descriptive commit messages that clearly explain what changes were made and why.
- Use conventional commit message format: `type(scope): description` (e.g., `feat(auth): add password reset functionality`).

### GitHub Repository Management
- Utilize the GitHub MCP for repository management tasks, including:
  - Creating and updating files in the repository
  - Fetching current file contents to assess state
  - Creating repositories for new projects
- For new projects, initialize a GitHub repository before starting development.
- For ongoing projects, verify GitHub connection and repository status at the beginning of each session.

### Backup and Recovery Strategy
- Create a new branch before implementing major changes to ensure the main branch remains stable.
- Push changes to remote repository at least once per hour during active development.
- Create tagged releases at significant project milestones.
- Document the latest stable checkpoint in `agentnotes.md` to facilitate rapid recovery if needed.
- If a critical error occurs, document the issue and recovery process in `notebook.md`.