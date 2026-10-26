# Auto Installer

Auto Installer is a Windows-only Python desktop application that turns a natural-language prompt into a validated installation script, executes it using `winget`, applies supported configuration actions, and verifies the results.

## Features

- Prompt-driven install planning
- AI-powered or fallback manifest generation
- Batch script validation before execution
- Safe winget execution workflow
- GUI via Tkinter
- Verification and final status report
- Output saved in `output/runs/<run_id>/`

## Prerequisites

- Windows 10 or 11
- Python 3.11+
- `winget` available on PATH
- Gemini API key (optional for local demo behavior)

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## LLM configuration

Copy `.env.example` to `.env` and add your values:

```powershell
copy .env.example .env
```

Gemini is the default provider. Create a key in [Google AI Studio](https://aistudio.google.com/apikey), then set:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
```

The existing OpenAI-compatible provider is still available by setting `LLM_PROVIDER=openai` and configuring `OPENAI_API_KEY`, `OPENAI_MODEL`, and optionally `OPENAI_BASE_URL`.

When no key is set for the selected provider, the app falls back to a limited local planner. Provider/network/invalid-response errors are shown rather than silently switching to that fallback. Gemini requests retry transient provider errors; if Gemini remains unavailable (HTTP 503), wait briefly and try again.

## Run the app

```powershell
python main.py
```

## Build a Windows executable

Install the application dependencies and PyInstaller:

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

Then run `build_windows.bat` from the project folder. The standalone executable is created at `dist\AutoInstaller.exe`.

Copy your `.env` file beside `AutoInstaller.exe` (or create one there using `dist\.env.example`). The API key is loaded at runtime and is not bundled into the executable. Run the executable from a folder where you have write permission; run logs and generated installation files are placed under `output\runs` beside the executable.

## Test

```powershell
python -m unittest discover -s tests
```

## Security notes

- The app validates package IDs and script contents before execution.
- Only a restricted subset of batch commands is allowed.
- Unsupported or unsafe actions are rejected.
- The app does not bypass Windows security policies.
- Prompts are sent to the configured AI provider; do not include passwords, API keys, or other secrets.
- MySQL account/password configuration is not supported by this MVP.

## Supported subset

- `winget install --id <package_id> --exact --silent --accept-package-agreements --accept-source-agreements`
- `git config user.name <value>`
- `git config user.email <value>`
- creating directories and text files in explicit, safe locations

## Limitations

- Real AI-based generation requires a Gemini or OpenAI API key, network access, and available provider quota.
- Some software packages may not be available in `winget` at runtime.
- Advanced custom installer logic is intentionally restricted for safety.
