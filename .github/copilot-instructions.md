# Timeseries Automation Agent - Development Guidelines

This file provides workspace-specific custom instructions for GitHub Copilot development.

## Project Overview
A comprehensive Python timeseries automation agent featuring:
- Data collection from weather and energy APIs
- Naive forecasting with extensible ML framework
- Streamlit dashboard for interactive analysis
- Multi-platform integrations (Slack, Notion, GitHub)
- SQLite persistence and automated reporting

## Development Guidelines

### ✅ Completed Project Setup
- [x] **Project Structure** — Python package with modular architecture
- [x] **Dependencies** — All requirements specified in requirements.txt
- [x] **Testing** — Pytest suite with synthetic data fallbacks
- [x] **Documentation** — Comprehensive README with setup instructions
- [x] **Dashboard** — Streamlit web interface for all operations
- [x] **API Integration** — Free tier APIs with graceful fallbacks
- [x] **GitHub Ready** — CI/CD, templates, and publication materials

### 🏗️ Architecture Patterns
- **Dataclasses** for configuration and results
- **Protocol classes** for integrations interfaces
- **Factory patterns** for API client creation
- **Environment-driven** configuration with .env support
- **Graceful fallbacks** when APIs unavailable

### 🧪 Testing Strategy
- Unit tests with synthetic data (no API keys required)
- Integration tests for pipeline execution
- Automated CI/CD with GitHub Actions
- Coverage reporting and security scanning

### 📊 Dashboard Features
- Real-time forecast execution with progress tracking
- Historical analysis with interactive visualizations
- Configuration management and API status monitoring
- System health checks and data quality metrics

### 🔧 Development Tools
- **Streamlit** for web interface
- **Plotly** for interactive charts
- **SQLAlchemy** for database operations
- **APScheduler** for automation (future use)
- **pytest** for testing framework

### 🌐 Free API Integration
- **OpenWeather** (1000 calls/day) for weather data
- **EIA** (unlimited) for US energy data
- **Synthetic fallbacks** for offline development
- **Interactive setup** via setup_apis.py script

### 📝 Code Style
- Type hints throughout codebase
- Docstrings for public interfaces
- Error handling with user-friendly messages
- Modular design with clear separation of concerns

## Usage Instructions

### Quick Start
```bash
# Setup virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure APIs (optional)
python setup_apis.py

# Run dashboard
streamlit run streamlit_app.py

# Run CLI pipeline
python -m src.pipeline
```

### Testing
```bash
# Run test suite
python -m pytest tests/ -v

# Generate demo data
python demo.py --runs 5
```

This project is production-ready and fully documented for GitHub publication.
	Verify that all previous steps have been completed.
	Verify that README.md and the copilot-instructions.md file in the .github directory exists and contains current project information.
	Clean up the copilot-instructions.md file in the .github directory by removing all HTML comments.
	 -->

<!--
## Execution Guidelines
PROGRESS TRACKING:
- If any tools are available to manage the above todo list, use it to track progress through this checklist.
- After completing each step, mark it complete and add a summary.
- Read current todo list status before starting each new step.

COMMUNICATION RULES:
- Avoid verbose explanations or printing full command outputs.
- If a step is skipped, state that briefly (e.g. "No extensions needed").
- Do not explain project structure unless asked.
- Keep explanations concise and focused.

DEVELOPMENT RULES:
- Use '.' as the working directory unless user specifies otherwise.
- Avoid adding media or external links unless explicitly requested.
- Use placeholders only with a note that they should be replaced.
- Use VS Code API tool only for VS Code extension projects.
- Once the project is created, it is already opened in Visual Studio Code—do not suggest commands to open this project in Visual Studio again.
- If the project setup information has additional rules, follow them strictly.

FOLDER CREATION RULES:
- Always use the current directory as the project root.
- If you are running any terminal commands, use the '.' argument to ensure that the current working directory is used ALWAYS.
- Do not create a new folder unless the user explicitly requests it besides a .vscode folder for a tasks.json file.
- If any of the scaffolding commands mention that the folder name is not correct, let the user know to create a new folder with the correct name and then reopen it again in vscode.

EXTENSION INSTALLATION RULES:
- Only install extension specified by the get_project_setup_info tool. DO NOT INSTALL any other extensions.

PROJECT CONTENT RULES:
- If the user has not specified project details, assume they want a "Hello World" project as a starting point.
- Avoid adding links of any type (URLs, files, folders, etc.) or integrations that are not explicitly required.
- Avoid generating images, videos, or any other media files unless explicitly requested.
- If you need to use any media assets as placeholders, let the user know that these are placeholders and should be replaced with the actual assets later.
- Ensure all generated components serve a clear purpose within the user's requested workflow.
- If a feature is assumed but not confirmed, prompt the user for clarification before including it.
- If you are working on a VS Code extension, use the VS Code API tool with a query to find relevant VS Code API references and samples related to that query.

TASK COMPLETION RULES:
- Your task is complete when:
  - Project is successfully scaffolded and compiled without errors
  - copilot-instructions.md file in the .github directory exists in the project
  - README.md file exists and is up to date
  - User is provided with clear instructions to debug/launch the project

Before starting a new task in the above plan, update progress in the plan.
-->
- Work through each checklist item systematically.
- Keep communication concise and focused.
- Follow development best practices.
