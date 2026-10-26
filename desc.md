# Project: Auto Installer — AI-Powered Software Installation and Configuration

Act as a senior Python developer. Build a complete, working MVP of a Windows application called **Auto Installer** in the current VS Code workspace.

Do not just provide example code or explain how to build it. Create the actual project files, implement the functionality, run available tests, fix errors, and provide clear instructions for running the application.

## 1. Project Objective

Auto Installer is a prompt-driven application that automatically installs and configures software using an AI/LLM API.

The user's only task-specific input should be a natural-language prompt describing the application and desired configuration.

Example:

"Install Git, Visual Studio Code, and Python. Configure Git with my username Matrix and prepare the environment for Python development."

The application should interpret this request and carry out the installation and configuration workflow automatically.

## 2. Required Workflow

Implement this exact workflow:

1. **User Prompt:** Accept a natural-language description of the software to install and configure.
2. **AI Processing:** Send the prompt to an online AI/LLM API.
3. **Batch Generation:** Have the LLM generate a Windows Batch (`.bat`) installation script containing the necessary installation commands.
4. **Plan Generation:** Have the LLM return a structured JSON manifest containing the requested applications, exact package IDs, configuration instructions, and verification checks.
5. **Validation:** Validate the generated script and manifest before executing anything. Reject unknown or unsafe commands.
6. **Script Creation:** Save the validated batch script as `install.bat`.
7. **Installation:** Execute the batch script using Python's subprocess functionality and stream its output to the application's activity log.
8. **Configuration:** After successful installation, execute the validated configuration actions defined in the manifest.
9. **Verification:** Check whether each application was installed and whether its supported configuration was applied successfully.
10. **Result:** Display a completion report listing successful installations, completed configurations, failed operations, and any required manual steps.

The intended workflow is:

`Prompt → LLM API → Generate .bat + JSON Manifest → Validate → Execute → Configure → Verify → Ready-to-Use Application`

## 3. Technology Stack

Use the following technologies:

- Python 3.11 or later.
- Tkinter for the graphical user interface.
- An online LLM API using the official OpenAI Python SDK initially.
- A configurable LLM model name.
- Python `subprocess`, `pathlib`, `logging`, `json`, and other standard libraries where appropriate.
- Windows Package Manager (`winget`) as the initial package installation backend.
- Windows Batch scripts (`.bat`) for installation.
- `python-dotenv` for loading environment variables.
- `unittest` or `pytest` for automated tests.

Keep the LLM integration behind a separate provider module so another API provider can be supported later.

## 4. AI/LLM API Integration

Create an LLM client module that:

- Sends the user's prompt to the configured API.
- Uses a carefully designed system prompt to request a valid batch script and structured JSON manifest.
- Requests structured output where supported.
- Handles malformed JSON, incomplete responses, API errors, rate limits, and timeouts.
- Never assumes the model's generated output is trustworthy.
- Does not hardcode API keys or other secrets.

Use environment variables:

`OPENAI_API_KEY`
`OPENAI_MODEL`
`OPENAI_BASE_URL` (optional)

Include a `.env.example` file showing the required configuration. Add `.env` to `.gitignore`.

If the API configuration is missing, display a useful setup message instead of crashing. Do not print API keys in logs.

## 5. Batch File Generation

The LLM must generate the actual `.bat` file content rather than merely suggesting installation commands.

For the initial implementation, support Windows software installed through Winget.

Generated installation commands should use exact package IDs and appropriate non-interactive flags, for example:

`winget install --id 7zip.7zip --exact --silent --accept-package-agreements --accept-source-agreements`

The generated batch script should:

- Disable command echoing.
- Display useful progress messages.
- Install the requested packages in a predictable order.
- Detect installation failures and return a nonzero exit code.
- Avoid unnecessary installation of already-installed software where practical.
- Use appropriate error handling.
- Exit with a meaningful status code.

Do not fabricate Winget package IDs. Use Winget's search functionality when necessary to validate package availability.

Save generated artifacts in a dedicated run directory, for example:

`output/runs/<run_id>/install.bat`

Also save the corresponding JSON manifest and execution log in that directory.

## 6. Configuration Engine

Installation and configuration must be separate stages.

After the batch script succeeds, read the validated JSON manifest and perform the requested configuration operations.

Implement a modular configuration engine supporting, where applicable:

- Git user name and email configuration when supplied in the prompt.
- Creation of configuration files with validated contents and paths.
- Creation of directories.
- Supported application-specific configuration handlers.
- Environment-variable configuration where safely implemented.
- Application-specific post-install commands through explicitly registered, validated handlers.

Do not pretend that every Windows application can be configured through a universal mechanism.

If the requested configuration is not supported, report that limitation clearly rather than silently claiming success.

Only perform configuration actions that are explicitly described in the validated manifest and supported by the application.

## 7. Security and Validation

**Security is a core requirement. Never blindly execute arbitrary AI-generated commands.**

Implement a validation layer between LLM generation and execution.

The initial MVP should:

- Allow only the supported installation command patterns and explicitly approved configuration actions.
- Validate package IDs, manifest fields, executable paths, and file destinations.
- Reject PowerShell execution, encoded commands, arbitrary downloaded scripts, command obfuscation, destructive filesystem commands, unauthorized registry modifications, credential theft, and unrelated system changes.
- Reject command chaining, pipelines, redirection, or other shell features when they are not required and explicitly supported.
- Refuse to execute the generated script if its commands cannot be validated confidently.
- Never bypass Windows User Account Control or silently grant administrator privileges.
- Prevent configuration actions from writing to arbitrary protected paths.
- Avoid logging secrets or sensitive configuration values.
- Record validation failures and explain why execution was blocked.

The application should not require repeated confirmation dialogs during a normal, validated installation workflow. However, it must respect operating-system permission requirements and block operations that fall outside its supported safety policy.

Do not claim that simple pattern matching can guarantee that arbitrary batch files are safe. Limit the accepted script language to a small, explicitly defined subset.

## 8. Graphical User Interface

Create a simple, modern-looking Tkinter interface suitable for a college mini-project demonstration.

Include:

- Application title: Auto Installer.
- A large text box for the user's natural-language prompt.
- A Run Auto Installer button.
- A status indicator showing the current stage.
- A progress indicator.
- A live activity log.
- An installation completion/failure summary.
- A button to open the generated output directory.
- A read-only view of the generated batch script for inspection.
- Clear error messages when installation or configuration fails.

The main interface must remain responsive while the API request, installation, and verification are running. Use background threads for long-running operations and communicate with Tkinter widgets safely through the main thread.

The user should not have to manually edit a batch file or enter installation commands.

## 9. Reliability and Error Handling

Implement:

- API request timeouts.
- JSON schema validation.
- Batch-script validation.
- Installation exit-code handling.
- Subprocess timeouts.
- Application installation verification.
- Configuration verification where practical.
- Logging for every run.
- Graceful handling of missing Winget, unsupported applications, unavailable packages, network failures, and API errors.
- A clear final report separating success, failure, and incomplete configuration.

Do not report success merely because the batch file executed. Verify the requested results.

If one installation fails, record the failure and do not incorrectly report that the entire workflow succeeded. Stop dependent configuration steps when their prerequisites fail.

## 10. Project Structure

Organize the project into maintainable modules. Use a structure similar to:

AutoInstaller/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── ui/
│   └── main_window.py
├── ai/
│   ├── llm_client.py
│   └── prompts.py
├── core/
│   ├── planner.py
│   ├── models.py
│   ├── validator.py
│   ├── executor.py
│   ├── configurator.py
│   ├── verifier.py
│   └── logger.py
├── package_managers/
│   └── winget.py
├── tests/
│   ├── test_validator.py
│   ├── test_models.py
│   └── test_planner.py
└── output/
    └── runs/

You may adjust the structure if necessary, but maintain clear separation between the user interface, AI integration, security validation, script execution, configuration, and verification.

## 11. Testing

Create automated tests that do not install real software.

Test at least:

- Valid and invalid LLM responses.
- Missing required manifest fields.
- Allowed and prohibited batch commands.
- Invalid or malformed package IDs.
- Safe handling of configuration paths.
- API error handling.
- Subprocess failure handling.
- Verification success and failure.

Mock the LLM API and installation subprocesses in unit tests. Never execute generated installation scripts during automated tests.

Manually verify that the application launches successfully and that its non-installation workflow works without requiring a real API request.

## 12. README and Setup Instructions

Write a README explaining:

- The project's purpose.
- System architecture and execution workflow.
- Prerequisites.
- Python environment setup.
- Dependency installation.
- LLM API key configuration.
- How to launch the GUI.
- How to test the application.
- Supported installation and configuration operations.
- Security limitations and known restrictions.

Provide Windows commands such as:

`python -m venv .venv`

`.venv\Scripts\activate`

`pip install -r requirements.txt`

`python main.py`

## 13. Implementation Instructions

Work directly in the current workspace.

Before making changes, inspect the existing files and preserve unrelated user work.

Implement the complete MVP rather than stopping after creating a project outline. Do not leave the core workflow as TODOs, placeholder methods, or pseudocode.

Prioritize a reliable Windows-only implementation over incomplete cross-platform support.

Do not add a database, cloud infrastructure, user accounts, or unnecessary frameworks unless they are genuinely required.

If a capability cannot be implemented reliably for every application, implement a working supported subset and document its limitations.

When finished:

1. List the files created or modified.
2. Explain how to install dependencies and run Auto Installer.
3. Explain how to configure the LLM API.
4. Identify what has been tested successfully.
5. State any remaining limitations honestly.

The final deliverable must be a runnable Python application that demonstrates the complete prompt-to-installation-to-configuration workflow for supported Windows applications.