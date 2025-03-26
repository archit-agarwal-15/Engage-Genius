import logging
import requests
import xml.etree.ElementTree as ET
import os
from config import TABLEAU_SERVER, TABLEAU_TOKEN_NAME,TABLEAU_TOKEN_SECRET

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load Tableau credentials from environment variables
TABLEAU_API_VERSION = "3.10"

def fetch_tableau_views(auth_token, site_id):
    """
    Fetch all available views in Tableau.
    :param auth_token: Authentication token for Tableau
    :param site_id: ID of the Tableau site
    :return: List of views
    """
    url = f"{TABLEAU_SERVER}/api/{TABLEAU_API_VERSION}/sites/{site_id}/views"
    headers = {
        "X-Tableau-Auth": auth_token,
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to fetch Tableau views: {response.text}")
        return []

    return response.json()

def fetch_tableau_view_data(auth_token, site_id, view_id):
    """
    Fetch data from a specific Tableau view.
    :param auth_token: Authentication token for Tableau
    :param site_id: Tableau site ID
    :param view_id: Tableau view ID
    :return: View data in JSON
    """
    url = f"{TABLEAU_SERVER}/api/{TABLEAU_API_VERSION}/sites/{site_id}/views/{view_id}/data"
    headers = {
        "X-Tableau-Auth": auth_token,
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f"Failed to fetch view data: {response.text}")
        return None

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        logging.error(f"Response is not in JSON format: {response.text}")
        return response.text  # Return raw text if JSON decoding fails

def fetch_tableau_auth_token():
    """Fetch the Tableau authentication token and site ID."""
    url = "https://tableau.razorpay.in/api/3.10/auth/signin"
    headers = {"Content-Type": "application/json"}
    payload = {
        "credentials": {
            "personalAccessTokenName": TABLEAU_TOKEN_NAME,
            "personalAccessTokenSecret": TABLEAU_TOKEN_SECRET,
            "site": {"contentUrl": ""}
        }
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        logging.error(f"Failed to authenticate with Tableau: {response.text}")
        return None, None

    try:
        # Parse XML with namespace handling
        root = ET.fromstring(response.text)
        ns = {"ts": "http://tableau.com/api"}  # Namespace from response

        credentials = root.find("ts:credentials", ns)
        site = credentials.find("ts:site", ns) if credentials is not None else None

        if credentials is None or site is None:
            logging.error(f"Unexpected XML structure: {response.text}")
            return None, None

        auth_token = credentials.attrib.get("token", "")
        site_id = site.attrib.get("id", "")

        logging.info(f"Successfully retrieved auth token and site ID: {site_id}")
        return auth_token, site_id

    except ET.ParseError as e:
        logging.error(f"Error parsing Tableau XML response: {e}")
        return None, None