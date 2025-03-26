from flask import Flask, request, jsonify
import threading
from services.slack_service import fetch_slack_messages, send_slack_message
from services.openai_service import generate_ai_analysis
from services.google_service import fetch_google_sheets_data, fetch_google_doc_data
from services.tableau_service import fetch_tableau_auth_token
from datetime import datetime, timedelta
from services.jira_service import jira,handle_epic_history
import logging
import requests
import re

app = Flask(__name__)


@app.route("/insights", methods=["POST"])
def handle_insights_request():
    """API to handle insights request from various sources."""
    logging.info("Received insights request")

    # Check if request is JSON or Slack form-encoded
    if request.content_type == "application/json":
        data = request.get_json()
    else:
        data = request.form  # Handle Slack's `application/x-www-form-urlencoded`

    logging.debug(f"Request Data: {data}")

    if "text" in data:
        source, source_details, prompt = parse_command_text(data["text"])
        if not source or not source_details:
            return jsonify({"error": "Invalid command format. Expected: /insights <source> <source_details> <extra_details>"}), 400
    else:
        source = data.get("source", "")
        source_details = data.get("source_details", "")

    # Validate required parameters
    if not source or not source_details:
        logging.error("Missing required parameters: source, source_details")
        return jsonify({"error": "Missing required parameters: source, source_details"}), 400

    threading.Thread(target=generate_insights, args=(prompt,source,source_details,data.get("response_url"))).start()
    response = {"text": "Processing... I'll update you soon!"}
    return jsonify(response)



@app.route("/slack/command", methods=["POST"])
def handle_slack_command():
    """Handle the /apollo Slack command."""
    print("coming into slack-command")
    data = request.form
    command_text = data.get("text", "").split()
    if len(command_text) < 2:
        return jsonify({"text": "Usage: /apollo <team_name> <month>"})
    team_name, days = command_text[0], command_text[1]
    # insights = generate_summary(f"Generate insights for team {team_name} for the month {month}.")
    threading.Thread(target=handle_epic_history, args=(days,data.get("response_url"),'''
        project = EHGI AND
        ("#Key Project Status" = "Yes-POD" OR
        "#Key Project Status" = "Yes-Group" OR
        "#Key Project Status" = "Yes-Sub-Group") AND
        "#Quarter(New)" = "FY25-Q4"
    ''')).start()
      # ✅ Respond immediately (Slack expects this within 3 sec)
    response = {"text": "Processing... :hourglass_flowing_sand: I'll update you soon"}
    return jsonify(response)

def parse_command_text(command_text):
    """Parse Slack command text with square brackets format."""
    try:
        # Regular expression to match text within square brackets
        pattern = r'\[(.*?)\]'
        matches = re.findall(pattern, command_text)

        if len(matches) < 3:
            raise ValueError("Invalid command format. Expected: /insights [source] [source_details] [prompt]")

        source = matches[0].strip()
        source_details = matches[1].strip()
        prompt = matches[2].strip()

        return source, source_details, prompt
    except ValueError as e:
        logging.error(f"Command parsing error: {e}")
        return None, None, None

def process_request(source, source_details, response_url):
    """Process the insights request based on the source."""
    if source == "slack":
        data = fetch_slack_messages(source_details[0])
        store_messages_in_vector_db(data)
        insights = generate_summary(f"Analyze and summarize Slack messages: {data}")
    elif source == "google_sheets":
        data = fetch_google_sheets_data(source_details[0], source_details[1], "A1:Z100")
        insights = generate_summary(f"Summarize Google Sheets data: {data}")
    else:
        insights = "Invalid source."

    send_slack_message(response_url, insights)

def generate_insights(prompt, source, source_details, response_url):
    """Generate insights based on the prompt and source data."""
    source_data = ""
    logging.info(f"Source Details: {source_details}")
    if source == "slack":
        source_data = fetch_slack_messages(source_details)
    elif source == "jira":
        source_data = handle_epic_history(30,"",source_details,True)
    elif source == "google_doc":
        source_data = fetch_google_doc_data(source_details)
    elif source == "google_sheets":
        source_data = fetch_all_sheets_data(source_details)
    elif source == "tableau":
        auth_token, site_id = fetch_tableau_auth_token()
        source_data = fetch_tableau_view_data(auth_token, site_id, "ba5ba5d7-b22b-414b-8700-a63657cb17cb")


    integrated_prompt = f"""
    {prompt}
    Data Source ({source}): {source_data}
    """
    insights = generate_ai_analysis(integrated_prompt)  # Fetch insights from Bedrock
    #report_filename = generate_doc_report(insights)
    #send_doc_to_slack(response_url, report_filename)
    #print(insights)
    requests.post(response_url, json={"text": insights})




if __name__ == "__main__":
   app.run(port=3000, debug=True)
