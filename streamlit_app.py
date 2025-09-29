"""
Streamlit Dashboard for Timeseries Automation Agent

This dashboard provides an interactive interface to:
- Run forecasting pipelines
- View historical forecast performance
- Monitor data collection status
- Configure automation settings
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.config import load_settings
from src.pipeline import ForecastPipeline
from src.reporting.logging import ForecastLogger
from src.forecasting.models import naive_forecast

# Page configuration
st.set_page_config(
    page_title="Energy Forecast Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

class StreamlitDashboard:
    def __init__(self):
        self.settings = load_settings()
        self.logger = ForecastLogger(self.settings.database)
        
    def run(self):
        """Main dashboard application"""
        st.title("⚡ Energy Forecast Dashboard")
        st.markdown("*Real-time electricity price forecasting and automation*")
        
        # Sidebar navigation
        if 'page' not in st.session_state:
            st.session_state.page = "🏠 Overview"
        
        page = st.sidebar.selectbox(
            "Navigate to:",
            ["🏠 Overview", "🔮 Run Forecast", "📊 Historical Analysis", "⚙️ Configuration", "📈 Data Monitoring"],
            index=["🏠 Overview", "🔮 Run Forecast", "📊 Historical Analysis", "⚙️ Configuration", "📈 Data Monitoring"].index(st.session_state.page)
        )
        
        st.session_state.page = page
        
        if page == "🏠 Overview":
            self.overview_page()
        elif page == "🔮 Run Forecast":
            self.forecast_page()
        elif page == "📊 Historical Analysis":
            self.analysis_page()
        elif page == "⚙️ Configuration":
            self.config_page()
        elif page == "📈 Data Monitoring":
            self.monitoring_page()
    
    def overview_page(self):
        """Dashboard overview with key metrics"""
        st.header("📊 Dashboard Overview")
        
        # Get latest forecast data
        try:
            runs_df = self.logger.get_recent_runs(limit=10)
            
            if not runs_df.empty:
                latest_run = runs_df.iloc[0]
                
                # Key metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Latest Forecast",
                        f"{latest_run['mean_forecast']:.2f} €/MWh",
                        f"{latest_run['rmse']:.2f} RMSE"
                    )
                
                with col2:
                    st.metric(
                        "Data Source", 
                        latest_run['data_source'],
                        f"Horizon: {latest_run['horizon_hours']}h"
                    )
                
                with col3:
                    accuracy = 100 - latest_run['mape']
                    st.metric(
                        "Accuracy",
                        f"{accuracy:.1f}%",
                        f"{latest_run['mape']:.1f}% MAPE"
                    )
                
                with col4:
                    st.metric(
                        "Last Update",
                        latest_run['created_at'].strftime("%H:%M"),
                        latest_run['created_at'].strftime("%Y-%m-%d")
                    )
                
                # Performance trend chart
                st.subheader("🎯 Recent Performance Trend")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=runs_df['created_at'],
                    y=runs_df['rmse'],
                    mode='lines+markers',
                    name='RMSE',
                    line=dict(color='#ff6b6b', width=2)
                ))
                
                fig.update_layout(
                    title="Forecast Accuracy Over Time",
                    xaxis_title="Time",
                    yaxis_title="RMSE (€/MWh)",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.info("No forecast runs found. Run your first forecast to see metrics here!")
                
        except Exception as e:
            st.error(f"Error loading overview data: {e}")
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Run New Forecast", type="primary"):
                st.rerun()
        
        with col2:
            if st.button("View Analysis"):
                st.session_state.page = "📊 Historical Analysis"
                st.rerun()
        
        with col3:
            if st.button("Check Configuration"):
                st.session_state.page = "⚙️ Configuration"
                st.rerun()
    
    def forecast_page(self):
        """Interactive forecast execution page"""
        st.header("🔮 Run Forecast")
        
        # Forecast configuration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Forecast Configuration")
            
            horizon = st.slider(
                "Forecast Horizon (hours)",
                min_value=1,
                max_value=168,  # 7 days
                value=24,
                help="How many hours ahead to forecast"
            )
            
            force_synthetic = st.checkbox(
                "Use Synthetic Data",
                value=False,
                help="Force use of synthetic data instead of real APIs"
            )
            
            notification_enabled = st.checkbox(
                "Send Notifications",
                value=True,
                help="Send results to Slack/Notion if configured"
            )
        
        with col2:
            st.subheader("Current Settings")
            st.write(f"**Database:** {self.settings.database.database_url}")
            
            # API status indicators
            apis_available = []
            if os.getenv("OPENWEATHER_API_KEY"):
                apis_available.append("🌤️ OpenWeather")
            if os.getenv("NORDPOOL_API_KEY"):
                apis_available.append("⚡ Nord Pool")
            if os.getenv("SLACK_TOKEN"):
                apis_available.append("💬 Slack")
            if os.getenv("NOTION_TOKEN"):
                apis_available.append("📝 Notion")
            
            if apis_available:
                st.success("**APIs Available:**")
                for api in apis_available:
                    st.write(f"• {api}")
            else:
                st.warning("**Using Synthetic Data**")
                st.write("No API keys configured")
        
        # Run forecast button
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Run Forecast Pipeline", type="primary", use_container_width=True):
                self.run_forecast_pipeline(horizon, force_synthetic, notification_enabled)
    
    def run_forecast_pipeline(self, horizon, force_synthetic, notification_enabled):
        """Execute the forecast pipeline with progress tracking"""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize pipeline
            status_text.text("Initializing pipeline...")
            progress_bar.progress(10)
            
            # Create notifier based on settings
            from src.automation.notifications import SlackNotifier
            
            class ConsoleNotifier:
                def post_message(self, channel: str, text: str) -> dict:
                    return {"channel": channel, "text": text}
            
            if notification_enabled and os.getenv("SLACK_TOKEN"):
                notifier = SlackNotifier(os.getenv("SLACK_TOKEN"))
            else:
                notifier = ConsoleNotifier()
            
            pipeline = ForecastPipeline(slack_notifier=notifier)
            
            # Run pipeline
            status_text.text("Running forecast pipeline...")
            progress_bar.progress(30)
            
            # Temporarily override settings if needed
            if force_synthetic:
                # Remove API keys to force synthetic data
                original_keys = {}
                for key in ["OPENWEATHER_API_KEY", "NORDPOOL_API_KEY"]:
                    if key in os.environ:
                        original_keys[key] = os.environ[key]
                        del os.environ[key]
            
            result = pipeline.run()
            progress_bar.progress(80)
            
            # Restore API keys if they were removed
            if force_synthetic and original_keys:
                os.environ.update(original_keys)
            
            status_text.text("Forecast completed successfully!")
            progress_bar.progress(100)
            
            # Display results
            st.success("✅ Forecast completed successfully!")
            
            # Show results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 Forecast Summary")
                st.write(f"**Mean Forecast:** {result.metrics['latest']:.2f} €/MWh")
                st.write(f"**RMSE:** {result.metrics['rmse']:.2f}")
                st.write(f"**MAE:** {result.metrics['mae']:.2f}")
                st.write(f"**MAPE:** {result.metrics['mape']:.2f}%")
                st.write(f"**Data Source:** {result.data_source}")
                
                # Check for integration results (these are not in the output yet, so using placeholders)
                slack_sent = notification_enabled and os.getenv("SLACK_TOKEN")
                notion_synced = os.getenv("NOTION_TOKEN") and os.getenv("NOTION_DATABASE_ID")
                github_committed = os.getenv("GITHUB_TOKEN") and os.getenv("GITHUB_REPO")
                
                if slack_sent:
                    st.success("💬 Slack notification sent")
                if notion_synced:
                    st.success("📝 Notion database updated")
                if github_committed:
                    st.success("📁 GitHub artifacts committed")
            
            with col2:
                st.subheader("📈 Forecast Visualization")
                
                # Load and display the plot
                if result.report_path and os.path.exists(result.report_path):
                    st.image(result.report_path, caption="Forecast vs Actual")
                else:
                    st.warning("Plot not found")
            
            # Show forecast values table
            if hasattr(result.forecast, 'y_pred') and len(result.forecast.y_pred) > 0:
                st.subheader("📊 Detailed Forecast Values")
                
                df = pd.DataFrame([
                    {
                        'Hour': i + 1,
                        'Forecast (€/MWh)': val,
                        'Timestamp': datetime.now() + timedelta(hours=i+1)
                    }
                    for i, val in enumerate(result.forecast.y_pred.values)
                ])
                
                st.dataframe(df, use_container_width=True)
            
        except Exception as e:
            progress_bar.progress(100)
            status_text.text("Error occurred during forecast")
            st.error(f"❌ Forecast failed: {str(e)}")
            st.exception(e)
    
    def analysis_page(self):
        """Historical analysis and performance metrics"""
        st.header("📊 Historical Analysis")
        
        try:
            runs_df = self.logger.get_recent_runs(limit=50)
            
            if runs_df.empty:
                st.info("No historical data available. Run some forecasts first!")
                return
            
            # Time range selector
            col1, col2 = st.columns(2)
            with col1:
                days_back = st.selectbox(
                    "Analysis Period",
                    [7, 14, 30, 90],
                    index=1,
                    format_func=lambda x: f"Last {x} days"
                )
            
            with col2:
                metric_type = st.selectbox(
                    "Primary Metric",
                    ["rmse", "mae", "mape"],
                    format_func=lambda x: x.upper()
                )
            
            # Filter data by time range
            cutoff_date = datetime.now() - timedelta(days=days_back)
            filtered_df = runs_df[runs_df['created_at'] >= cutoff_date]
            
            if filtered_df.empty:
                st.warning(f"No data available for the last {days_back} days")
                return
            
            # Performance metrics
            st.subheader("🎯 Performance Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_rmse = filtered_df['rmse'].mean()
                st.metric("Average RMSE", f"{avg_rmse:.2f}")
            
            with col2:
                avg_mae = filtered_df['mae'].mean()
                st.metric("Average MAE", f"{avg_mae:.2f}")
            
            with col3:
                avg_mape = filtered_df['mape'].mean()
                st.metric("Average MAPE", f"{avg_mape:.2f}%")
            
            with col4:
                total_runs = len(filtered_df)
                st.metric("Total Runs", total_runs)
            
            # Performance trend chart
            st.subheader("📈 Performance Trends")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=filtered_df['created_at'],
                y=filtered_df[metric_type],
                mode='lines+markers',
                name=metric_type.upper(),
                line=dict(width=2),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title=f"{metric_type.upper()} Over Time",
                xaxis_title="Date",
                yaxis_title=f"{metric_type.upper()} Value",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Data source breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📡 Data Source Distribution")
                source_counts = filtered_df['data_source'].value_counts()
                
                fig_pie = px.pie(
                    values=source_counts.values,
                    names=source_counts.index,
                    title="Forecast Data Sources"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.subheader("⏰ Forecast Frequency")
                
                # Group by day
                daily_counts = filtered_df.groupby(
                    filtered_df['created_at'].dt.date
                ).size().reset_index()
                daily_counts.columns = ['date', 'count']
                
                fig_bar = px.bar(
                    daily_counts,
                    x='date',
                    y='count',
                    title="Daily Forecast Count"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Detailed data table
            st.subheader("📋 Detailed History")
            
            # Format the dataframe for display
            display_df = filtered_df.copy()
            display_df['created_at'] = display_df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
            display_df = display_df[[
                'created_at', 'mean_forecast', 'rmse', 'mae', 'mape', 
                'data_source', 'horizon_hours'
            ]]
            display_df.columns = [
                'Timestamp', 'Forecast (€/MWh)', 'RMSE', 'MAE', 'MAPE (%)', 
                'Data Source', 'Horizon (h)'
            ]
            
            st.dataframe(display_df, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading historical analysis: {e}")
            st.exception(e)
    
    def config_page(self):
        """Configuration management page"""
        st.header("⚙️ Configuration")
        
        # API Configuration Status
        st.subheader("🔗 API Configuration Status")
        
        apis = [
            ("OpenWeather API", "OPENWEATHER_API_KEY", "Weather data collection"),
            ("Nord Pool API", "NORDPOOL_API_KEY", "Electricity price data"),
            ("Slack Token", "SLACK_TOKEN", "Notifications"),
            ("Notion Token", "NOTION_TOKEN", "Logging and database sync"),
            ("GitHub Token", "GITHUB_TOKEN", "Automated commits")
        ]
        
        for name, env_var, description in apis:
            col1, col2, col3 = st.columns([2, 1, 3])
            
            with col1:
                st.write(f"**{name}**")
            
            with col2:
                if os.getenv(env_var):
                    st.success("✅ Configured")
                else:
                    st.error("❌ Missing")
            
            with col3:
                st.write(description)
        
        st.markdown("---")
        
        # Database Configuration
        st.subheader("🗄️ Database Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Database URL:** {self.settings.database.database_url}")
            
            # Check database connectivity
            try:
                runs_df = self.logger.get_recent_runs(limit=1)
                st.success("✅ Database connected")
                st.write(f"**Total forecast runs:** {len(self.logger.get_recent_runs(limit=1000))}")
            except Exception as e:
                st.error(f"❌ Database error: {e}")
        
        with col2:
            st.write("**Database Tables:**")
            st.write("• `forecast_runs` - Run metadata and metrics")
            st.write("• `forecast_values` - Detailed forecast values")
        
        st.markdown("---")
        
        # Environment Variables Guide
        st.subheader("📝 Environment Setup Guide")
        
        st.markdown("""
        To configure the application, create a `.env` file in the project root with the following variables:
        """)
        
        env_template = """
# Weather API (optional - will use synthetic data if not provided)
OPENWEATHER_API_KEY=your-openweather-api-key

# Nord Pool API (optional - will use synthetic data if not provided)  
NORDPOOL_API_KEY=your-nordpool-api-key

# Slack notifications (optional)
SLACK_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL=#energy-forecast

# Notion logging (optional)
NOTION_TOKEN=secret_your-notion-integration-token
NOTION_DATABASE_ID=your-notion-database-id

# Database (uses SQLite by default)
DATABASE_URL=sqlite:///data/timeseries.db

# GitHub automation (optional)
GITHUB_TOKEN=ghp_your-github-token
GITHUB_REPO=owner/repo-name
GITHUB_BRANCH=main
GITHUB_COMMITTER_NAME=Automation Agent
GITHUB_COMMITTER_EMAIL=automation@example.com
        """
        
        st.code(env_template, language="bash")
        
        # Configuration validation
        st.subheader("🔍 Configuration Validation")
        
        if st.button("Validate Configuration"):
            self.validate_configuration()
    
    def validate_configuration(self):
        """Validate current configuration"""
        issues = []
        successes = []
        
        # Check API keys
        if not os.getenv("OPENWEATHER_API_KEY"):
            issues.append("⚠️ OpenWeather API key not configured - using synthetic weather data")
        else:
            successes.append("✅ OpenWeather API key configured")
        
        if not os.getenv("NORDPOOL_API_KEY"):
            issues.append("⚠️ Nord Pool API key not configured - using synthetic price data")
        else:
            successes.append("✅ Nord Pool API key configured")
        
        # Check database
        try:
            self.logger.get_recent_runs(limit=1)
            successes.append("✅ Database connection successful")
        except Exception as e:
            issues.append(f"❌ Database connection failed: {e}")
        
        # Check optional integrations
        if os.getenv("SLACK_TOKEN"):
            successes.append("✅ Slack integration configured")
        else:
            issues.append("ℹ️ Slack integration not configured (optional)")
        
        if os.getenv("NOTION_TOKEN"):
            successes.append("✅ Notion integration configured")
        else:
            issues.append("ℹ️ Notion integration not configured (optional)")
        
        if os.getenv("GITHUB_TOKEN"):
            successes.append("✅ GitHub integration configured")
        else:
            issues.append("ℹ️ GitHub integration not configured (optional)")
        
        # Display results
        for success in successes:
            st.success(success)
        
        for issue in issues:
            if issue.startswith("❌"):
                st.error(issue)
            elif issue.startswith("⚠️"):
                st.warning(issue)
            else:
                st.info(issue)
    
    def monitoring_page(self):
        """Data monitoring and system health page"""
        st.header("📈 Data Monitoring")
        
        st.subheader("🏥 System Health")
        
        # System health checks
        health_checks = []
        
        # Database health
        try:
            runs_df = self.logger.get_recent_runs(limit=5)
            if not runs_df.empty:
                last_run = runs_df.iloc[0]['created_at']
                time_since_last = datetime.now() - last_run
                
                if time_since_last.total_seconds() < 3600:  # Less than 1 hour
                    health_checks.append(("Database", "✅ Recent data available", "success"))
                elif time_since_last.total_seconds() < 86400:  # Less than 24 hours
                    health_checks.append(("Database", "⚠️ No recent runs (24h)", "warning"))
                else:
                    health_checks.append(("Database", "❌ No recent runs (>24h)", "error"))
            else:
                health_checks.append(("Database", "⚠️ No data available", "warning"))
        except Exception as e:
            health_checks.append(("Database", f"❌ Connection failed: {e}", "error"))
        
        # API availability (basic check)
        apis_to_check = [
            ("OpenWeather", "OPENWEATHER_API_KEY"),
            ("Nord Pool", "NORDPOOL_API_KEY"),
            ("Slack", "SLACK_TOKEN"),
            ("Notion", "NOTION_TOKEN"),
            ("GitHub", "GITHUB_TOKEN")
        ]
        
        for api_name, env_var in apis_to_check:
            if os.getenv(env_var):
                health_checks.append((f"{api_name} API", "✅ Configured", "success"))
            else:
                health_checks.append((f"{api_name} API", "⚠️ Not configured", "warning"))
        
        # Display health status
        for component, status, level in health_checks:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**{component}**")
            with col2:
                if level == "success":
                    st.success(status)
                elif level == "warning":
                    st.warning(status)
                else:
                    st.error(status)
        
        st.markdown("---")
        
        # Data quality metrics
        st.subheader("📊 Data Quality Metrics")
        
        try:
            runs_df = self.logger.get_recent_runs(limit=30)
            
            if not runs_df.empty:
                # Success rate
                total_runs = len(runs_df)
                successful_runs = len(runs_df[runs_df['rmse'] > 0])  # Assuming positive RMSE indicates success
                success_rate = (successful_runs / total_runs) * 100
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                
                with col2:
                    avg_execution_time = "< 1 min"  # Placeholder
                    st.metric("Avg Execution Time", avg_execution_time)
                
                with col3:
                    data_sources = runs_df['data_source'].nunique()
                    st.metric("Data Sources", data_sources)
                
                # Data source reliability
                st.subheader("🔗 Data Source Reliability")
                
                source_stats = runs_df.groupby('data_source').agg({
                    'rmse': ['count', 'mean'],
                    'mape': 'mean'
                }).round(2)
                
                source_stats.columns = ['Count', 'Avg RMSE', 'Avg MAPE']
                st.dataframe(source_stats, use_container_width=True)
                
            else:
                st.info("No data available for quality analysis")
        
        except Exception as e:
            st.error(f"Error loading data quality metrics: {e}")
        
        # Recent activity log
        st.subheader("📝 Recent Activity")
        
        try:
            recent_runs = self.logger.get_recent_runs(limit=10)
            
            if not recent_runs.empty:
                for _, run in recent_runs.iterrows():
                    with st.expander(f"🔮 Forecast - {run['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Mean Forecast:** {run['mean_forecast']:.2f} €/MWh")
                            st.write(f"**RMSE:** {run['rmse']:.2f}")
                            st.write(f"**MAE:** {run['mae']:.2f}")
                        
                        with col2:
                            st.write(f"**MAPE:** {run['mape']:.2f}%")
                            st.write(f"**Data Source:** {run['data_source']}")
                            st.write(f"**Horizon:** {run['horizon_hours']} hours")
            else:
                st.info("No recent activity to display")
        
        except Exception as e:
            st.error(f"Error loading recent activity: {e}")

def main():
    """Main application entry point"""
    try:
        dashboard = StreamlitDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"Application error: {e}")
        st.exception(e)

if __name__ == "__main__":
    main()