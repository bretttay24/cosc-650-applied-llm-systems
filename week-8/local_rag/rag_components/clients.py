"""Shared external service clients for the local RAG application."""

import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import AzureOpenAI


load_dotenv()

RESOURCE_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"].split("/api/projects")[0]

azure_openai_client = AzureOpenAI(
    azure_endpoint=RESOURCE_ENDPOINT,
    azure_ad_token_provider=get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    ),
    api_version="2024-10-21",
)
