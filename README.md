# Commit Summary Email Automation

## Overview

This mini project automates the process of collecting daily Git commits, transforming them into a structured summary using **Google Gemini AI**, and sending the result via email.

It is designed to help teams and managers quickly understand what was done during the day without needing to manually review commit histories.

---

## How It Works

1. **Collect commits**

   * Retrieves all commits made **today** from a local Git repository.

2. **Generate summary with AI**

   * Sends the commit messages to the **Gemini API**.
   * Uses a customizable prompt to format the output (e.g., executive summary, technical report, etc.).

3. **Send email**

   * Sends the generated summary to a configured email address using SMTP.

---

## Features

* Automatic daily commit extraction
* Customizable AI prompt
* AI-powered summaries (executive, technical, or custom)
* Email delivery via SMTP
* Environment-based configuration (`.env`)
* Lightweight and easy to integrate

---

## Project Structure

```
.
├── script.py      # Main script
├── .env           # Environment variables
├── README.md      # Project documentation
```

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo>
```

### 2. Install dependencies

```bash
pip install google-genai python-dotenv
```

---

## Configuration

Create a `.env` file in the root directory from the file `.env.example` and configure yours variables:

---

## Usage

Run the script:

```bash
python commit_summary_email.py
```

---

## Prompt Customization

You can fully control how the AI summarizes commits by editing:

```env
PROMPT_BASE=
```

### Example prompts:

**Executive summary**

```
Summarize these commits in a business-friendly way, focusing on impact and outcomes.
```

**Technical summary**

```
Group commits by feature and explain technical changes in detail.
```

**Changelog format**

```
Convert these commits into a structured changelog grouped by type (feat, fix, refactor).
```

---

## Email Output Example

```
Subject: Daily Commit Summary

- Added new API for command management
- Improved UI consistency in action buttons
- Fixed message loading issue in chat
- Optimized conversation ordering logic
```

---

## Notes

* Requires a valid **Gemini API key**
* If using Gmail, you must use an **App Password** (not your regular password)
* Only commits from the **current day** are included
* Repository must already be initialized with Git

---

## Possible Improvements

* Schedule execution (cron / task scheduler)
* Generate reports by week or sprint
* Attach raw commit logs to email
* Web dashboard for summaries
* Slack / Teams integration
* Multi-agent summarization (different perspectives)

---

## License

This project is open-source and free to use for personal or commercial purposes.

---

## Purpose

This tool was created to bridge the gap between **technical activity (commits)** and **business visibility**, making daily progress transparent and easy to understand.

---

**Built for productivity and clarity**
