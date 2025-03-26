import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
GOOGLE_CREDENTIALS = "credentials.json"
JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
TABLEAU_SERVER = os.getenv("TABLEAU_SERVER")
TABLEAU_TOKEN_NAME = os.getenv("TABLEAU_TOKEN_NAME")
TABLEAU_TOKEN_SECRET = os.getenv("TABLEAU_TOKEN_SECRET")