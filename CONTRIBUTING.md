# Contributing to Timeseries Automation Agent

Welcome! We're excited that you're interested in contributing to the Timeseries Automation Agent project.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**: `git clone https://github.com/your-username/timeseries-automation.git`
3. **Create virtual environment**: `python -m venv .venv`
4. **Activate environment**: `.\.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (Unix)
5. **Install dependencies**: `pip install -r requirements.txt`
6. **Run tests**: `python -m pytest tests/ -v`

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+ (3.13 recommended)
- Git
- Virtual environment tool

### Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-username/timeseries-automation.git
cd timeseries-automation

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Unix
# or
.\.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Set up pre-commit hooks (optional but recommended)
pre-commit install
```

### API Keys (Optional)
```bash
# Copy environment template
cp .env.template .env

# Add your API keys (or use synthetic data)
# Edit .env with your preferred editor
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_naive_forecast.py -v

# Run pipeline integration test
python -m src.pipeline
```

### Test Structure
- `tests/` - Unit and integration tests
- `tests/test_*.py` - Test files following pytest conventions
- Use synthetic data for testing (no API keys required)

## 📝 Code Style

We use several tools to maintain code quality:

### Formatting
```bash
# Auto-format code
black src/ tests/
isort src/ tests/

# Check formatting
black --check src/ tests/
isort --check-only src/ tests/
```

### Linting
```bash
# Run linter
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

### Type Checking
```bash
# Run type checker
mypy src/
```

## 🏗️ Project Structure

```
src/
├── automation/          # Scheduling and notifications
├── data_collection/     # API integrations
├── data_preparation/    # Data cleaning and features
├── forecasting/         # Models and algorithms
├── reporting/           # Visualization and logging
├── config.py           # Configuration management
└── pipeline.py         # Main orchestration

tests/                   # Test suite
docs/                   # Documentation
.github/                # GitHub workflows and templates
```

## 🔄 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Write code following existing patterns
- Add tests for new functionality
- Update documentation if needed
- Ensure all tests pass

### 3. Commit Changes
```bash
git add .
git commit -m "feat: add your feature description"
```

### 4. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] All tests pass locally
- [ ] Code is properly formatted (black, isort)
- [ ] No linting errors (ruff)
- [ ] Documentation updated if needed
- [ ] Changes are backwards compatible

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Reproduction Steps**: Minimal steps to reproduce
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Python version, dependency versions
6. **Logs**: Relevant error messages or logs

## 💡 Feature Requests

For new features:

1. **Use Case**: Describe the problem or need
2. **Proposed Solution**: Your suggested approach
3. **Alternatives**: Other solutions considered
4. **Impact**: Who would benefit from this feature

## 🏷️ Commit Convention

We follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or modifying tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add OpenWeather API integration
fix: handle missing API keys gracefully
docs: update README with setup instructions
test: add unit tests for forecast models
```

## 🤝 Code Review Process

1. **Automated Checks**: CI pipeline runs tests and linting
2. **Peer Review**: At least one maintainer reviews the code
3. **Discussion**: Address feedback and questions
4. **Approval**: Maintainer approves the changes
5. **Merge**: Changes are merged to main branch

## 📚 Resources

- [Project Documentation](README.md)
- [API Reference](docs/api.md)
- [Streamlit Dashboard Guide](docs/dashboard.md)
- [Deployment Guide](docs/deployment.md)

## ❓ Questions?

- Open an issue for bug reports or feature requests
- Start a discussion for general questions
- Check existing issues before creating new ones

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

*Happy coding!* 🚀