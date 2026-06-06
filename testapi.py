import os

from dotenv import load_dotenv
from openai import AzureOpenAI


# Load environment variables from the local .env file.
load_dotenv()


# Read Azure OpenAI settings from environment variables.
endpoint = os.getenv("AZURE_FOUNDRY_ENDPOINT")
model_name = os.getenv("AZURE_FOUNDRY_MODEL")
api_key = os.getenv("AZURE_FOUNDRY_API_KEY")


# Check that all required values exist before making the API call.
missing_keys = []
if not endpoint:
    missing_keys.append("AZURE_FOUNDRY_ENDPOINT")
if not model_name:
    missing_keys.append("AZURE_FOUNDRY_MODEL")
if not api_key:
    missing_keys.append("AZURE_FOUNDRY_API_KEY")

if missing_keys:
    print("Missing required environment variables:")
    for key in missing_keys:
        print(f"- {key}")
    raise SystemExit(1)


# Create the AzureOpenAI client using Azure Foundry endpoint.
# Strip the /api/projects/{project} path if it exists - only need the base URL
base_endpoint = endpoint
if "/api/projects/" in base_endpoint:
    base_endpoint = base_endpoint.split("/api/projects/")[0]

client = AzureOpenAI(
    api_key=api_key,
    api_version="2024-02-15-preview",
    azure_endpoint=base_endpoint,
)


# Ask a simple test question to verify the model call works.
response = client.chat.completions.create(
    model=model_name,
    messages=[
        {
            "role": "user",
            "content": "How many R's are there in the word raspberry?",
        }
    ],
)


# Print the model output so it is easy to confirm in terminal.
print("Model response:")
print(response.choices[0].message.content)
