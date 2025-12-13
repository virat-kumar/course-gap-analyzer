"""Application configuration settings."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str
    azure_openai_api_key: str
    api_version: str = "2024-12-01-preview"
    azure_openai_model: str = "gpt-4o"
    markdown_fixer_agent_max_iterations: int = 4
    
    # Tavily API Configuration
    tavily_api_key: Optional[str] = None
    
    # Database Configuration
    database_url: str = "sqlite:///./syllabus_gap_analyzer.db"
    
    # Retry Configuration
    max_retries: int = 3
    retry_backoff_base: float = 2.0  # Exponential backoff base
    
    # Top Companies Allowlist (configurable)
    top_companies_allowlist: List[str] = [
        # FAANG
        "Google", "Alphabet", "Microsoft", "Amazon", "Apple", "Meta", "Facebook",
        "Netflix",
        # Fortune 500 Tech Companies
        "IBM", "Oracle", "Cisco", "Intel", "Salesforce", "Adobe", "Nvidia",
        "Dell", "HP", "Qualcomm", "Broadcom", "VMware", "Palantir",
        "Snowflake", "Databricks", "Datadog", "MongoDB", "Elastic",
        "Splunk", "ServiceNow", "Workday", "Atlassian", "Zscaler",
        # Major Tech Employers
        "Tesla", "SpaceX", "Uber", "Lyft", "Airbnb", "Stripe", "Square",
        "PayPal", "Visa", "Mastercard", "Goldman Sachs", "JPMorgan",
        "Morgan Stanley", "Bank of America", "Wells Fargo",
        # Cloud Providers
        "AWS", "Amazon Web Services", "Azure", "Microsoft Azure",
        "GCP", "Google Cloud Platform",
    ]
    
    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


