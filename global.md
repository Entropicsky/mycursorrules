# Agent Collaboration Rules

## Project Understanding and Documentation

### Initial Project Assessment
- When starting a new agent session, or if the user prompts "Start me up", check for an `agent_notes` folder and explore all files in that directory if it exists to get up to speed on previous sessions before making changes.
- Then, methodically review the project's codebase, structure, and architecture thoroughly before starting any new work. 

### Documentation Management
For each project, create and maintain an `agent_notes` folder containing:

- **project_checklist.md**: Continuously updated plan with steps, progress, and status
- **notebook.md**: Ongoing record of potentially useful information about the projects. Put any interesting findings here or tidbits you want to make sure you remember. 
- **agentnotes.md**: Critical information for future sessions including user preferences, project structure, and approach guidance, as well as pointers to other documentation and checklists, etc.
- Technical specifications and other relevant documentation

Update these documents frquently yourself without prompting but also if the user prompts "doc it". 

## Development Methodology

### Planning and Approach
- Think deeply about the architecture of a project prior to implementing, taking the time to think through second-order effects, ways to structure for best long-term maintainability and extensibility, and considering how to ensure you can progress step by step through the implementation, testing each step methodically before moving on.  
- Before starting any major feature or significant work, create a detailed technical specification and action plan for that feature in the `agent_notes` folder, incorporating your thoughts from the thinking above. 
- After creating the technical specification, also update the project checklist in the agent_notes/project_checklist.md file to reflect the activities required for this tech spec. 
- Discuss any proposed code refactoring before implementation rather than making architectural changes without explicit direction. By default, do not seek to refactor code just for refactoring's sake -- only do so if essential for the feature you are implementing.

### Implementation Practices
- Use Streamlit for data analysis and rapid prototyping where appropriate, implementing the streamlit.testing framework for headless testing.
- Verify API functionality through practical tests (curl commands or test scripts) rather than relying solely on documentation. Before coding to an API, methodically make sure you understand the response structure of the API. 
- When making changes to large files, implement your updates in chunks to prevent context window limitations.

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
- Keep the agent_notes documents up to date with your testing progress and results

### Bug Resolution
When encountering bugs, not only fix the immediate issue but:
- Analyze why testing didn't catch the problem
- Proactively search for similar issues
- Update testing processes to prevent recurrence

## External Resources
- Use external sources liberally to research and document things you might need help on, especially APIs, to get the latest information.  
- For web searches, first consult the Perplexity MCP.
- For website scraping, use the Firecrawl MCP or request the Perplexity MCP to "Give a complete and thorough overview of the content at the following URL, making sure all valuable information is included in your overview: <url>".
- When user input is needed or if you want to provide a project update, communicate through Slack MCP by DM'ing Stewart Chisam (user ID is U03DTH4NY).

## Problem-Solving Approach

For each task, implement a structured thinking process:
1. Break the task into focused questions (8-14 questions)
2. For each question, develop 10 logical steps
3. Consider multiple perspectives to ensure thorough analysis
4. Address each component with comprehensive testing


## Code Review Process
- Implement a systematic self-review protocol before considering work complete:
  - Review code changes line-by-line to ensure they match the intended functionality
  - Create a dedicated review checklist in `agent_notes` for each significant feature
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

### Other notes
**"No Apologies"**: Never use apologies.
**"No Whitespace Suggestions"**: Don't suggest whitespace changes.
**"No Summaries"**: Do not provide unnecessary summaries of changes made. Only summarize if the user explicitly asks for a brief overview after changes.
**"No Unnecessary Confirmations"**: Don't ask for confirmation of information already provided in the context.
**"Preserve Existing Code"**: Don't remove unrelated code or functionalities. Pay attention to preserving existing structures.
**"No Implementation Checks"**: Don't ask the user to verify implementations that are visible in the provided context. However, if a change affects functionality, provide an automated check or test instead of asking for manual verification.
**"No Unnecessary Updates"**: Don't suggest updates or changes to files when there are no actual modifications needed.
**"Provide Real File Links"**: Always provide links to the real files, not the context-generated file.
**"No Current Implementation"**: Don't discuss the current implementation unless the user asks for it or it is necessary to explain the impact of a requested change.
**"Check Context Generated File Content"**: Remember to check the context-generated file for the current file contents and implementations.
**"Use Explicit Variable Names"**: Prefer descriptive, explicit variable names over short, ambiguous ones to enhance code readability.
**"Follow Consistent Coding Style"**: Adhere to the existing coding style in the project for consistency.
**"Prioritize Performance"**: When suggesting changes, consider code performance where applicable.
**"Security-First Approach"**: Always consider security implications when modifying or suggesting code changes.
**"Test Coverage"**: Suggest or include appropriate unit tests for new or modified code.
**"Error Handling"**: Implement robust error handling and logging where necessary.
**"Modular Design"**: Encourage modular design principles to improve code maintainability and reusability.
**"Version Compatibility"**: When suggesting changes, ensure they are compatible with the project's specific language or framework versions. If a version conflict arises, suggest an alternative.
**"Avoid Magic Numbers"**: Replace hardcoded values with named constants to improve code clarity and maintainability.
**"Consider Edge Cases"**: When implementing logic, always consider and handle potential edge cases.
**"Use Assertions"**: Include assertions wherever possible to validate assumptions and catch potential errors early.