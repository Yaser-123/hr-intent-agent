# Multi-Intent Identification App

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![UiPath](https://img.shields.io/badge/UiPath-Cloud-orange.svg)](https://cloud.uipath.com/)

HR Intent Identification Agent with Human-in-the-Loop via UiPath Action Center

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Author](#author)

## Overview

This LangGraph agent automatically identifies HR-related intents from user messages. When the AI cannot confidently identify intents, it escalates to UiPath Action Center for human validation, ensuring accurate processing of HR requests.

## Features

- **AI-Powered Intent Detection**: Leverages advanced LLMs (Azure OpenAI GPT-4o, Anthropic Claude, or OpenAI) to analyze HR requests
- **Human-in-the-Loop**: Seamlessly escalates uncertain cases to UiPath Action Center for human validation
- **Multi-Intent Support**: Handles multiple HR intents in a single message
- **Supported Intents**:
  - `LeaveRequest` - Vacation, PTO, time off requests
  - `AssetRequest` - Equipment, laptop, phone requests
  - `AddressUpdate` - Relocation, address changes
  - `ExpenseReimbursement` - Receipt submissions, expense claims

## Architecture

The agent follows a streamlined workflow:

1. **Extract Intents**: LLM analyzes user prompt to identify HR intents
2. **Validate with Human**: If no intents found, create Action Center task for human validation
3. **Route Intents**: Process identified intents

See `agent.mermaid` for visual representation.

## Prerequisites

- Python 3.10 or higher
- UiPath Cloud account with Action Center access
- API access to Azure OpenAI, Anthropic Claude, or OpenAI (optional for mock mode)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/multi-intent-identification-app.git
   cd multi-intent-identification-app
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**:
   ```bash
   # Windows
   .\.venv\Scripts\Activate.ps1
   # Linux/Mac
   source .venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -e .
   ```

## Configuration

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Configure API keys** in `.env`:
   - Add your `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` (optional for mock mode)
   - UiPath credentials are pre-configured for cloud deployment

## Usage

### Local Testing

1. **Run the agent locally**:
   ```bash
   uipath run agent --file input.json
   ```

2. **View results in web dashboard**:
   ```bash
   python web_viewer.py
   ```

### Sample Input

Create `input.json`:
```json
{
  "user_prompt": "I need to request time off for vacation and also update my address"
}
```

Expected output identifies `LeaveRequest` and `AddressUpdate` intents.

## Deployment

1. **Package the project**:
   ```bash
   uipath pack
   ```

2. **Publish to UiPath Cloud**:
   ```bash
   uipath publish --my-workspace
   ```

3. **Invoke on cloud**:
   ```bash
   uipath invoke agent --file input.json
   ```

## Project Structure

```
.
├── main.py              # LangGraph agent implementation
├── langgraph.json       # LangGraph configuration
├── pyproject.toml       # Project metadata and dependencies
├── uipath.json          # UiPath-specific configuration
├── agent.mermaid        # Visual workflow diagram
├── web_viewer.py        # Local web dashboard for results
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
├── input.json           # Sample input file
├── input2.json          # Additional test input
└── README.md            # This documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Author

**T MOHAMED AMMAR**
- Email: 1ammar.yaser@gmail.com
