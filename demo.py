"""
Demo script to populate the database with sample forecasts for dashboard demonstration.

This script generates several forecast runs with varying parameters to showcase
the Streamlit dashboard's analytical capabilities.
"""

import sys
from pathlib import Path
import time
import random
import os

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.pipeline import ForecastPipeline
from src.config import load_settings

def run_demo_forecasts(num_runs: int = 5):
    """Generate multiple forecast runs for dashboard demonstration."""
    print(f"🚀 Running {num_runs} demo forecasts...")
    
    settings = load_settings()
    
    # Create a notifier (will use console since we're removing tokens)
    from src.automation.notifications import SlackNotifier
    
    # Temporarily disable API keys to use synthetic data
    original_keys = {}
    api_keys = ["OPENWEATHER_API_KEY", "NORDPOOL_API_KEY", "SLACK_TOKEN", "NOTION_TOKEN", "GITHUB_TOKEN"]
    
    for key in api_keys:
        if key in os.environ:
            original_keys[key] = os.environ[key]
            del os.environ[key]
    
    # Create console notifier for demo
    class ConsoleNotifier:
        def post_message(self, channel: str, text: str) -> dict:
            print(f"[{channel}] {text}")
            return {"channel": channel, "text": text}
    
    notifier = ConsoleNotifier()
    pipeline = ForecastPipeline(slack_notifier=notifier)
    
    # Temporarily disable API keys to use synthetic data
    original_keys = {}
    api_keys = ["OPENWEATHER_API_KEY", "NORDPOOL_API_KEY", "SLACK_TOKEN", "NOTION_TOKEN", "GITHUB_TOKEN"]
    
    for key in api_keys:
        if key in os.environ:
            original_keys[key] = os.environ[key]
            del os.environ[key]
    
    try:
        for i in range(num_runs):
            print(f"📊 Running forecast {i+1}/{num_runs}...")
            
            # Add some randomness to make demo data more interesting
            # Temporarily modify environment to simulate different scenarios
            if i % 2 == 0:
                os.environ["DEMO_VARIATION"] = "high_variance"
            else:
                os.environ["DEMO_VARIATION"] = "low_variance"
            
            result = pipeline.run()
            
            print(f"   ✅ Forecast: {result.metrics['latest']:.2f} €/MWh")
            print(f"   📈 RMSE: {result.metrics['rmse']:.2f}, MAE: {result.metrics['mae']:.2f}, MAPE: {result.metrics['mape']:.2f}%")
            
            # Small delay to create time separation
            if i < num_runs - 1:
                time.sleep(2)
        
        print(f"\n🎉 Demo complete! Generated {num_runs} forecast runs.")
        print("🌐 Launch the Streamlit dashboard to explore the data:")
        print("   streamlit run streamlit_app.py")
        
    finally:
        # Restore original API keys
        for key, value in original_keys.items():
            os.environ[key] = value
        
        # Clean up demo environment variables
        if "DEMO_VARIATION" in os.environ:
            del os.environ["DEMO_VARIATION"]

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate demo forecasts for dashboard")
    parser.add_argument("--runs", type=int, default=5, help="Number of forecast runs to generate")
    
    args = parser.parse_args()
    run_demo_forecasts(args.runs)