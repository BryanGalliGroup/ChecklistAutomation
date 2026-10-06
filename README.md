# Commit Summary Email Automation

## Overview

This project automates the process of collecting daily Git commits from one or more repositories, generating structured summaries using **Google Gemini AI**, allowing the user to review and edit the generated content, and sending the final result via email.

The automation supports multiple projects and consolidates their summaries into a single document and a single email.

The application provides both:

- **Graphical interface (GUI)** using Tkinter
- **Terminal/CLI mode** for command-line execution

Projects and application settings are managed through JSON configuration files, while sensitive credentials remain stored in the `.env` file.

The tool is designed to help teams and managers quickly understand what was done during the day without manually reviewing commit histories.

---

## How It Works

The automation follows these steps:

1. **Load configuration**

   The application loads:

   - Projects from `projects.json`
   - AI, email and editor settings from `settings.json`
   - Sensitive credentials from `.env`

2. **Select projects**

   The user selects which configured repositories should be processed.

   In GUI mode, projects can be selected through the graphical interface.

   In terminal mode, projects are selected through the command line.

3. **Collect commits**

   Retrieves commits made **today** from each selected Git repository.

   Each repository is processed independently.

4. **Generate summaries with AI**

   Sends the collected commits from each project to the **Gemini API**.

   Each project receives an independent AI-generated summary.

5. **Consolidate summaries**

   The generated summaries are combined into a single text document.

   Each project is clearly identified.

   Example:

   ```text
   CRM GALLI Group
   ─────────────────
   Summary generated from CRM commits...

   SGI Ambientalli
   ─────────────────
   Summary generated from SGI commits...
   ```

6. **Review and edit**

   The generated file is automatically opened in the configured text editor.

   The user can review, correct, or modify the generated content before sending.

7. **Confirm email sending**

   After the review, the application asks the user whether the final summary should be sent.

8. **Send email**

   If confirmed, the complete document is sent as **one email**.

   The email contains the final content reviewed and saved by the user.

---

## Application Modes

The application supports two execution modes.

### GUI Mode

The default mode opens the Tkinter graphical interface.

```bash
./script.sh
```

The GUI provides:

- Project management
- Project selection
- Settings management
- Execution controls
- Real-time logs
- Automation status
- Email confirmation
- Error messages
- Background execution without blocking the interface

### Terminal Mode

The terminal mode remains available for users who prefer command-line execution.

Using the project launcher:

```bash
./script.sh --cli
```

The CLI provides project selection and executes the same automation workflow used by the GUI.

---

## Supported Projects

Projects are no longer configured through `.env`.

They are stored in `projects.json`.

Example:

```json
{
  "projects": [
    {
      "key": "CRM",
      "name": "CRM GALLI Group",
      "path": "/home/ti/dev/CRM"
    },
    {
      "key": "SGI",
      "name": "SGI Ambientalli",
      "path": "/home/ti/dev/SGI-Ambientalli"
    }
  ]
}
```

Each project contains:

| Property | Description |
| --- | --- |
| `key` | Unique project identifier |
| `name` | Display name |
| `path` | Local Git repository path |

Projects can be added, edited or removed through the GUI without modifying the Python source code.

The configured repositories must already exist locally and be initialized as Git repositories.

---

## Project Management

The GUI provides complete project management.

### Add Project

A new project can be registered by providing:

- Project key
- Project name
- Repository path

The application validates:

- Required fields
- Project key format
- Duplicate project keys
- Directory existence
- Git repository initialization

### Edit Project

Existing projects can be modified through the GUI.

### Remove Project

One or more projects can be selected and removed.

The application requests confirmation before deletion.

---

## Application Settings

Application settings are stored in:

```text
settings.json
```

The settings are divided into three sections:

```json
{
  "ai": {
    "model": "gemini-2.5-flash",
    "prompt": "..."
  },
  "email": {
    "subject": "Checklist de Atividades | [DAY]",
    "from_name": "Automação de Desenvolvimento",
    "from_address": "seu-email@empresa.com",
    "to": [
      "destinatario@empresa.com"
    ],
    "signature": "Atenciosamente,\nAutomação de Desenvolvimento",
    "image_url": ""
  },
  "editor": {
    "command": "code"
  }
}
```

### AI Settings

The `ai` section controls:

- Gemini model
- AI prompt

Example:

```json
{
  "ai": {
    "model": "gemini-2.5-flash",
    "prompt": "Summarize these commits in a business-friendly way, focusing on impact and outcomes."
  }
}
```

### Email Settings

The `email` section controls:

- Subject
- Sender display name
- Sender address
- Recipients
- Signature
- Optional image URL

The SMTP server credentials are **not stored in `settings.json`**.

They remain in `.env`.

### Editor Settings

The `editor` section defines the preferred text editor.

Example:

```json
{
  "editor": {
    "command": "code"
  }
}
```

The editor command is optional.

---

## Environment Variables

The `.env` file is now reserved for **secrets and infrastructure configuration**.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_password
```

The following information should **not** be stored in `.env` anymore:

- Projects
- Project names
- Project paths
- AI prompt
- Gemini model
- Email subject
- Email recipients
- Email signature
- Email image URL
- Editor configuration

These values are managed through `projects.json` and `settings.json`.

---

## Configuration Files

The application uses three main configuration sources:

| File | Purpose |
| --- | --- |
| `.env` | Secrets and infrastructure |
| `projects.json` | Git projects |
| `settings.json` | AI, email and editor settings |

### `.env`

Contains sensitive information:

```env
GEMINI_API_KEY=...
SMTP_HOST=...
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
```

### `projects.json`

Contains the projects processed by the automation:

```json
{
  "projects": [
    {
      "key": "CRM",
      "name": "CRM GALLI Group",
      "path": "/home/ti/dev/CRM"
    }
  ]
}
```

### `settings.json`

Contains editable application settings:

```json
{
  "ai": {
    "model": "gemini-2.5-flash",
    "prompt": "..."
  },
  "email": {
    "subject": "Checklist de Atividades | [DAY]",
    "from_name": "Automação de Desenvolvimento",
    "from_address": "seu-email@empresa.com",
    "to": [
      "destinatario@empresa.com"
    ],
    "signature": "Atenciosamente,\nAutomação de Desenvolvimento",
    "image_url": ""
  },
  "editor": {
    "command": "code"
  }
}
```

---

## Features

- Automatic daily commit extraction
- Support for multiple Git repositories
- Dynamic project management
- Graphical project management
- Terminal/CLI mode
- Project selection before execution
- Add, edit and remove projects
- Git repository validation
- Independent AI summary generation per project
- Consolidated summary in a single document
- Manual review and editing before sending
- Email confirmation before sending
- Single email containing all selected project summaries
- Customizable AI model
- Customizable AI prompt
- Configurable email subject
- Configurable email recipients
- Configurable email signature
- Configurable text editor
- Email delivery via SMTP
- Environment-based secret management
- JSON-based application configuration
- Temporary file cleanup
- Background automation execution
- Real-time execution logs in the GUI
- Linux shell launcher
- Linux `.desktop` launcher
- Windows batch launcher
- Relative and absolute project path support
- No source code modification required when adding projects

---

## Project Structure

```text
.
├── main.py
├── cli.py
├── projects.json
├── settings.json
├── .env
├── .env.example
├── README.md
├── requirements.txt
├── script.sh
├── script.bat
│
├── src/
│   ├── config.py
│   ├── logger.py
│   ├── automation.py
│   ├── commit_collector.py
│   ├── ia_client.py
│   ├── email_sender.py
│   ├── build_html.py
│   └── build_plain.py
│
└── .venv/
```

A Linux external launcher can also be stored separately from the project.

Example:

```text
/home/ti/scripts/
├── run_ca.sh
├── AutomacaoChecklist.desktop
└── icon.png

/home/ti/dev/CA/
├── main.py
├── cli.py
├── projects.json
├── settings.json
├── .env
└── ...
```

This allows the launcher and application icon to be placed in a convenient location without moving the application itself.

---

## Main Components

### `main.py`

Responsible for the graphical interface and application orchestration.

Responsibilities include:

- Loading projects
- Displaying configured projects
- Project selection
- Project creation
- Project editing
- Project removal
- Project validation
- Loading application settings
- Starting automation
- Running automation in a background thread
- Displaying execution logs
- Displaying errors
- Confirming email sending
- Sending the final email
- Preventing conflicting actions while an automation is running

### `cli.py`

Provides the terminal version of the application.

Responsibilities include:

- Loading configuration
- Displaying available projects
- Project selection
- Running the automation
- Displaying execution logs
- Requesting email confirmation
- Sending the final email

### `src/config.py`

Responsible for configuration management.

Responsibilities include:

- Loading `.env`
- Loading `projects.json`
- Saving `projects.json`
- Loading `settings.json`
- Saving `settings.json`
- Providing access to required environment variables
- Providing SMTP configuration

### `src/logger.py`

Provides a centralized logging mechanism.

The logger can write messages to:

- The GUI
- The terminal
- Other callbacks

Messages include timestamps and execution status.

Example:

```text
[16:30:12] Projeto: CRM GALLI Group
[16:30:13] Coletando commits de CRM GALLI Group...
[16:30:14] Gerando resumo com IA...
[16:30:18] ✓ Resumo de CRM GALLI Group gerado.
```

### `src/automation.py`

Contains the main automation workflow.

Responsibilities include:

- Resolving project paths
- Collecting project commits
- Generating project summaries
- Consolidating summaries
- Creating temporary files
- Opening the configured editor
- Waiting for editing to finish
- Reading the edited summary
- Removing temporary files
- Sending the final email

### `src/commit_collector.py`

Responsible for interacting with Git and retrieving commits from selected repositories.

### `src/ia_client.py`

Responsible for communicating with the Gemini API and generating summaries.

The Gemini model and prompt are loaded from `settings.json`.

### `src/email_sender.py`

Responsible for creating and sending the final email through SMTP.

Email content is generated in both:

- Plain text
- HTML

### `src/build_html.py`

Responsible for generating the HTML version of the email.

### `src/build_plain.py`

Responsible for generating the plain-text version of the email.

---

## Installation

### 1. Clone the automation repository

```bash
git clone <your-repo-url>
cd <your-repo>
```

---

### 2. Create a Python virtual environment

Linux:

```bash
python3 -m venv .venv
```

Windows:

```bat
python -m venv .venv
```

---

### 3. Activate the virtual environment

Linux:

```bash
source .venv/bin/activate
```

Windows:

```bat
.venv\Scripts\activate
```

---

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

The project requires the Gemini client and environment configuration packages.

If dependencies need to be installed manually:

```bash
pip install google-genai python-dotenv
```

---

### 5. Linux Tkinter requirement

The GUI uses Tkinter.

On Ubuntu/Debian, install the Tkinter package if it is not already available:

```bash
sudo apt update
sudo apt install python3-tk
```

This is required for the graphical interface.

The terminal mode does not require Tkinter.

---

## Initial Configuration

Create `.env` from `.env.example`.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_password
```

Create or edit `projects.json`:

```json
{
  "projects": [
    {
      "key": "CRM",
      "name": "CRM GALLI Group",
      "path": "/home/ti/dev/CRM"
    },
    {
      "key": "SGI",
      "name": "SGI Ambientalli",
      "path": "/home/ti/dev/SGI-Ambientalli"
    }
  ]
}
```

Create or edit `settings.json`:

```json
{
  "ai": {
    "model": "gemini-2.5-flash",
    "prompt": "Summarize these commits in a business-friendly way, focusing on impact and outcomes."
  },
  "email": {
    "subject": "Checklist de Atividades | [DAY]",
    "from_name": "Automação de Desenvolvimento",
    "from_address": "your_email@example.com",
    "to": [
      "recipient@example.com"
    ],
    "signature": "Atenciosamente,\nAutomação de Desenvolvimento",
    "image_url": ""
  },
  "editor": {
    "command": "code"
  }
}
```

The GUI can subsequently be used to manage projects and settings.

---

## Usage

## Linux

### GUI

Make the launcher executable:

```bash
chmod +x script.sh
```

Run:

```bash
./script.sh
```

The graphical interface will open.

### Terminal

Run:

```bash
./script.sh --cli
```

---

## Linux External Launcher

The application can also be launched through a separate script located outside the project directory.

For example:

```text
/home/ti/scripts/run_ca.sh
```

The launcher can point to the actual application directory:

```text
/home/ti/dev/CA
```

This allows the launcher to remain in a convenient location while the application source stays organized separately.

Example:

```bash
/home/ti/scripts/run_ca.sh
```

Opens the GUI.

```bash
/home/ti/scripts/run_ca.sh --cli
```

Starts terminal mode.

The launcher should resolve the application directory independently from the current working directory.

This is important because applications started through a desktop launcher may have a different current working directory than applications started directly from a terminal.

---

## Linux Desktop Launcher

A `.desktop` file can be used to launch the GUI with a double click or from the application menu.

Example:

```ini
[Desktop Entry]
Version=1.0
Type=Application

Name=Automação de Checklist
Comment=Automação de resumo de commits

Exec=/bin/bash /home/ti/scripts/run_ca.sh
Path=/home/ti/scripts

Terminal=false
Icon=/home/ti/scripts/icon.png

Categories=Development;
StartupNotify=true
```

The launcher should be made executable:

```bash
chmod +x /home/ti/scripts/AutomacaoChecklist.desktop
```

It can also be registered in the user's application menu:

```bash
mkdir -p ~/.local/share/applications

cp /home/ti/scripts/AutomacaoChecklist.desktop \
   ~/.local/share/applications/automacao-checklist.desktop

chmod +x ~/.local/share/applications/automacao-checklist.desktop
```

The `Icon` property can point to a custom image:

```ini
Icon=/home/ti/scripts/icon.png
```

The `.desktop` launcher should contain only one `Icon` entry.

---

## Windows

The Windows launcher is:

```text
script.bat
```

Running it normally starts the GUI:

```bat
script.bat
```

The terminal mode can be started using:

```bat
script.bat terminal
```

The Windows launcher validates:

- `.env`
- Virtual environment
- Python executable
- Main Python file
- CLI file when terminal mode is selected

The `.bat` file can be executed by double-clicking it.

---

## Project Selection

### GUI

The GUI displays all projects configured in `projects.json`.

The user can select:

- One project
- Multiple projects
- All projects

The selected projects are processed independently.

### Terminal

The CLI displays the available projects and allows selection by number.

Example:

```text
Projetos disponíveis:

  1. CRM GALLI Group (CRM)
  2. SGI Ambientalli (SGI)

Digite os números dos projetos separados por vírgula.
Digite 'a' para selecionar todos.

Projetos: 1,2
```

---

## Daily Commit Collection

Only commits made on the **current day** are collected.

For example, if the automation runs on October 6th, only commits from October 6th are included.

If one selected project has no commits for the current day, that project is skipped.

If multiple projects are selected and only one contains commits, only that project's summary is generated and included in the email.

If none of the selected projects have commits, the automation finishes without generating or sending an email.

---

## AI Summary Generation

Each project is summarized independently.

Example:

```text
CRM GALLI Group
────────────────
- Implemented client management improvements
- Fixed authentication behavior
- Refactored service integration

SGI Ambientalli
────────────────
- Updated environmental compliance workflow
- Improved checklist validation
- Fixed report generation
```

This prevents commits from different projects from being mixed during the summarization process.

The AI model and prompt are configured in `settings.json`.

---

## Prompt Customization

The AI prompt can be changed through the GUI or directly in `settings.json`.

Example:

```json
{
  "ai": {
    "model": "gemini-2.5-flash",
    "prompt": "Summarize these commits in a business-friendly way, focusing on impact and outcomes."
  }
}
```

### Executive Summary

```text
Summarize these commits in a business-friendly way, focusing on impact and outcomes.
```

### Technical Summary

```text
Group commits by feature and explain the technical changes in detail.
```

### Changelog

```text
Convert these commits into a structured changelog grouped by type such as feat, fix, refactor, and chore.
```

---

## Review Before Sending

The automation does not immediately send the generated summary.

Instead, it creates a temporary file and opens it in the configured text editor.

The user can:

- Correct inaccurate summaries
- Remove unnecessary information
- Add additional context
- Change wording
- Reorganize the content
- Completely rewrite sections if necessary

After the editor is closed, the modified content is used for the email.

The temporary file is removed after processing.

---

## Editor Configuration

The preferred text editor is configured through `settings.json`.

Example:

```json
{
  "editor": {
    "command": "code"
  }
}
```

The editor configuration is optional.

Supported editors include:

- VS Code
- VS Code Insiders
- Codium
- Gedit
- Xed
- Kate
- Sublime Text
- Nano
- Vim
- Vi

For graphical editors that support a waiting/blocking argument, the automation automatically adds the appropriate option when supported.

If no editor is explicitly configured, the application attempts to detect an available editor on Linux.

On Windows, Notepad is used as the default editor.

---

## Email Output

When multiple projects are selected, only **one email** is sent.

Example:

```text
Subject: Checklist de Atividades | 06/10

CRM GALLI Group
────────────────
Implemented improvements to client management.
Fixed authentication and permission handling.
Refactored service integration.

SGI Ambientalli
────────────────
Updated compliance workflows.
Improved checklist validation.
Fixed report generation.
```

The email contains the final content exactly as reviewed and saved by the user.

The application supports both:

- Plain-text email
- HTML email

---

## Email Configuration

Editable email settings are stored in `settings.json`.

Example:

```json
{
  "email": {
    "subject": "Checklist de Atividades | [DAY]",
    "from_name": "Automação de Desenvolvimento",
    "from_address": "your_email@example.com",
    "to": [
      "recipient@example.com"
    ],
    "signature": "Atenciosamente,\nAutomação de Desenvolvimento",
    "image_url": ""
  }
}
```

The `[DAY]` placeholder is automatically replaced with the current day and month.

Example:

```text
Checklist de Atividades | 06/10
```

SMTP credentials remain in `.env`:

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_password
```

For Gmail, an **App Password** should be used instead of the regular account password when SMTP authentication requires it.

---

## Requirements

- Python 3.x
- Git
- Internet connection
- Valid Gemini API key
- SMTP account
- At least one configured Git repository
- Text editor for reviewing generated summaries
- Tkinter for GUI mode

Linux/Ubuntu:

```bash
sudo apt install python3-tk
```

Terminal mode does not require the Tkinter package.

---

## Security

Never store API keys, SMTP passwords, or other credentials directly in source code.

Use environment variables:

```env
GEMINI_API_KEY=...
SMTP_PASSWORD=...
```

The `.env` file should never be committed to Git.

Recommended `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

`projects.json` and `settings.json` do not contain SMTP passwords or Gemini API keys and can be versioned when appropriate.

If credentials are accidentally committed, they should be considered compromised and rotated immediately.

Project paths should also be treated as configuration data and validated before processing.

---

## Error Handling

The launcher validates:

- `.env` file
- Python virtual environment
- Python executable
- Main Python script
- CLI file when applicable

The Python application validates:

- Project configuration
- Project keys
- Project names
- Project paths
- Directory existence
- Git repository initialization
- AI configuration
- Email configuration

The application also handles:

- Empty commit collections
- Projects without commits
- Invalid project selection
- Duplicate project keys
- Invalid project paths
- Non-Git directories
- Empty edited summaries
- Editor execution errors
- Email cancellation
- Email configuration errors
- AI configuration errors
- Temporary file cleanup
- Automation errors in background execution

A project without commits does not interrupt the processing of other selected projects.

---

## Launcher Architecture

The application separates the launcher from the Python application.

### GUI

```text
.desktop / script.bat / script.sh
              │
              ▼
           main.py
              │
              ▼
        Tkinter GUI
              │
              ▼
       automation.py
```

### Terminal

```text
script.sh / script.bat
          │
          ▼
        cli.py
          │
          ▼
    automation.py
```

Both modes share the same automation layer.

This prevents the GUI and CLI from maintaining separate implementations of the core workflow.

---

## Configuration Architecture

The current configuration architecture separates application settings from secrets:

```text
.env
 │
 ├── GEMINI_API_KEY
 ├── SMTP_HOST
 ├── SMTP_PORT
 ├── SMTP_USER
 └── SMTP_PASSWORD

projects.json
 │
 └── Git repositories

settings.json
 │
 ├── AI configuration
 ├── Email configuration
 └── Editor configuration
```

This separation allows application settings to be edited without exposing infrastructure credentials.

---

## Future Improvements

Possible future improvements include:

- Automatic scheduled execution
- Weekly or monthly reports
- Sprint summaries
- Commit categorization
- Historical report storage
- Web dashboard
- Slack integration
- Microsoft Teams integration
- Automatic report archiving
- Multiple AI summary perspectives
- Project-specific prompts
- Additional email templates
- Attachments containing raw commit information
- Improved application logging
- Packaging as a standalone executable
- Automatic desktop shortcut creation
- Cross-platform installer

---

## License

This project is open-source and free to use for personal or commercial purposes.

---

## Purpose

This tool was created to bridge the gap between **technical activity** and **business visibility**.

Instead of requiring managers or stakeholders to manually review Git history, the automation transforms daily development activity into a concise, reviewable, and shareable summary.

The multi-project workflow allows different repositories to be configured independently and processed separately while maintaining a single consolidated communication channel.

The current architecture separates:

- User interface
- Terminal interface
- Automation logic
- Git collection
- AI integration
- Email delivery
- Configuration
- Logging

This makes the application easier to maintain and allows new projects and settings to be managed without modifying the application source code.

---

**Built for productivity and clarity.**