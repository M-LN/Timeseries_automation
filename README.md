# ⚡ Timeseries Automation Agent

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](#testing)

An end-to-end automation agent for collecting energy and weather data, preparing features, training forecasting models, and distributing insights through collaboration tools with a modern Streamlit dashboard interface.

## Roadmap

1. **Data Collection**
   - Collect hourly weather features from OpenWeather (temperature, humidity, wind).
   - Collect electricity spot prices from Nord Pool APIs.
   - Persist raw snapshots for reproducibility (local SQLite by default).

2. **Data Preparation**
   - Clean and impute gaps.
   - Engineer lagged, calendar, and weather-derived features.

3. **Forecasting**
   - Start with naïve and statistical baselines.
   - Extend to machine learning (Random Forest, Gradient Boosting).
   - Explore deep learning (LSTM/GRU) for longer horizons.
   - Track accuracy with RMSE, MAE, and MAPE.

4. **Visualisation & Reporting**
   - Plot actual vs. forecasted values.
   - Produce shareable reports (Jupyter, nbconvert, or Streamlit).

5. **Automation & Agents**
   - Orchestrate daily pipelines with APScheduler.
   - Send Slack summaries and sync results to Notion.
   - Commit artefacts (data, model runs) to GitHub automatically.

6. **Portfolio Value**
   - Provide a clear README detailing problem, solution, and results.
   - Showcase a demo (Streamlit dashboard or screenshots).

## Features

### 🔮 Automated Forecasting
- Naive baseline models with real-time execution
- Synthetic data fallback when API keys unavailable
- Configurable forecast horizons (1-168 hours)
- Comprehensive error metrics (RMSE, MAE, MAPE)

### 📊 Interactive Dashboard
- **Streamlit Web Interface**: Modern, responsive UI for all operations
- **Real-time Monitoring**: Live performance metrics and system health
- **Historical Analysis**: Trend visualization and performance tracking
- **Configuration Management**: API status and environment validation

### 🔗 Multi-Platform Integration
- **Slack Notifications**: Automated forecast summaries
- **Notion Database**: Structured logging and metrics storage
- **GitHub Automation**: Automatic artifact commits and versioning
- **SQLite Persistence**: Local database for forecast history

### 🌐 Data Sources
- **OpenWeather API**: Real-time weather data collection
- **Nord Pool API**: European electricity spot prices
- **Synthetic Fallback**: Generated data when APIs unavailable

## Project Layout

```
data/
  raw/              # incoming snapshots
  processed/        # cleaned and feature-rich datasets
models/             # serialized model artefacts
notebooks/          # exploratory analysis and reports
reports/            # generated reporting assets
src/
  automation/       # schedulers and notification clients
  data_collection/  # API integrations
  data_preparation/ # cleaning and feature engineering
  forecasting/      # modelling utilities
  config.py         # configuration dataclasses
  pipeline.py       # orchestration entry points
```

## Getting Started

### 1. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure secrets

Create a `.env` file with the necessary tokens:

```
OPENWEATHER_API_KEY=your-key
NORDPOOL_API_KEY=your-key
SLACK_TOKEN=your-token
NOTION_TOKEN=your-token
NOTION_DATABASE_ID=your-database
DATABASE_URL=sqlite:///data/timeseries.db
GITHUB_TOKEN=ghp_yourtoken
GITHUB_REPO=owner/repo
GITHUB_BRANCH=main
GITHUB_COMMITTER_NAME=Automation Agent
GITHUB_COMMITTER_EMAIL=automation@example.com
```

### 4. Run the pipeline

**Option A: Command Line Interface**
```powershell
python -m src.pipeline
```

**Option B: Interactive Web Dashboard**
```powershell
streamlit run streamlit_app.py
```

The Streamlit dashboard provides a comprehensive web interface with:

- **🏠 Overview**: Key metrics, performance trends, and quick actions
- **🔮 Run Forecast**: Interactive forecast execution with real-time progress
- **📊 Historical Analysis**: Performance analytics and data visualization
- **⚙️ Configuration**: API status, environment setup, and validation
- **📈 Data Monitoring**: System health checks and data quality metrics

The pipeline module currently exposes helper functions and will be expanded with a CLI entry point as features mature. Executing it now will create a plot in `reports/plots/` summarising the latest forecast. If a `SLACK_TOKEN` environment variable is available, the run will also notify the configured Slack workspace; otherwise it logs to the console.

Each execution appends a row to the `forecast_runs` table and the corresponding horizon values to `forecast_values` inside the configured database (SQLite by default). When `NOTION_TOKEN` and `NOTION_DATABASE_ID` are provided, the same metrics are pushed to your Notion database. Update property names (`Horizon`, `RMSE`, `MAE`, `MAPE`, `Data Source`, `Report`) to match your Notion schema. With GitHub credentials set (`GITHUB_TOKEN`, `GITHUB_REPO`, etc.), the agent commits the rendered plot to `reports/plots/` and a JSON snapshot with metrics and values to `reports/history/` in the repository.

### 5. Demo Data (Optional)

Generate sample forecasts for dashboard demonstration:

```powershell
python demo.py --runs 5
```

This creates multiple forecast runs with varying parameters to showcase the analytics capabilities.

## Contributing

1. Format code with `ruff` or `black` (tooling to be added).
2. Run tests (to be added) before submitting changes.
3. Update documentation when behaviour changes.

## License

MIT License (add `LICENSE` file if desired).
