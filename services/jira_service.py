import logging
from jira import JIRA
import os
from services.apollo_service import generate_final_insights
from datetime import datetime, timedelta
from config import JIRA_API_TOKEN,JIRA_EMAIL, JIRA_SERVER

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
summarize_prompt = """
Prompt: Generate Uber Insights from Project Plan & JIRA
*"You are an AI-powered project analyst. Your task is to analyze and combine data from two sources: the Project Plan (Google Sheets/Docs) and JIRA (Issues, Epics, Status, Changelog, and Assignees) to generate Uber Insights at the project level.

📌 Inputs:
Project Plan: Contains key milestones, dependencies, owners, and deadlines.
JIRA Data: Includes Epics, Stories, Issues, Status, Assignees, and historical changes.
🔍 Expected Insights:
Delivery Health: Compare planned vs actual progress on key milestones.
Risk Detection: Identify blockers, delays, or high-risk items.
Ownership & Accountability: Track workload distribution and ownership gaps.
Velocity & Progress Trends: Analyze weekly completion rates and sprint performance.
Dependency Management: Highlight cross-team dependencies and risks.
Escalation Needs: Flag issues that require leadership attention.
📊 Output Format:
Summary Report: High-level project status (On Track, At Risk, Blocked).
Risk & Delay Analysis: Highlight tasks/issues slipping behind schedule.
Top Contributors & Bottlenecks: Identify high performers and stuck items.
Suggested Actions: Actionable recommendations to improve project health.
"""

# Load JIRA credentials from environment variables

JIRA_OPTIONS = {
    "server": "https://razorpay.atlassian.net",
    "verify": False  # Disable SSL verification (use with caution)
}
#jobj = JIRA(options=JIRA_OPTIONS, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))
# Initialize JIRA client
try:
    jira = JIRA(options=JIRA_OPTIONS, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))
    logging.info("✅ JIRA connection established successfully.")
except Exception as e:
    logging.error(f"❌ Failed to connect to JIRA: {e}")
    jira = None  # Set to None if connection fails


def fetch_jira_issues(jql_query, max_results=50):
    """
    Fetch JIRA issues based on the given JQL query.

    :param jql_query: JIRA Query Language (JQL) string
    :param max_results: Maximum number of issues to fetch
    :return: List of issues with key details
    """
    if not jira:
        logging.error("JIRA client is not initialized.")
        return []

    try:
        issues = jira.search_issues(jql_query, maxResults=max_results, fields="summary,assignee,status,created,updated")
        issue_list = []

        for issue in issues:
            issue_data = {
                "key": issue.key,
                "summary": issue.fields.summary,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                "status": issue.fields.status.name,
                "created": issue.fields.created,
                "updated": issue.fields.updated
            }
            issue_list.append(issue_data)

        return issue_list
    except Exception as e:
        logging.error(f"❌ Error fetching JIRA issues: {e}")
        return []

def fetch_jira_changelog(issue_key):
    """
    Fetch the changelog for a specific JIRA issue.

    :param issue_key: JIRA issue key (e.g., ENG-123)
    :return: List of changes with timestamps
    """
    if not jira:
        logging.error("JIRA client is not initialized.")
        return []

    try:
        issue = jira.issue(issue_key, expand="changelog")
        changelog = issue.changelog.histories
        changes = []

        for history in changelog:
            change_details = {
                "updated_by": history.author.displayName,
                "timestamp": history.created,
                "changes": []
            }

            for item in history.items:
                change_details["changes"].append({
                    "field": item.field,
                    "from": item.fromString if item.fromString else "None",
                    "to": item.toString if item.toString else "None"
                })

            changes.append(change_details)

        return changes
    except Exception as e:
        logging.error(f"❌ Error fetching JIRA changelog: {e}")
        return []
def handle_epic_history(days, response_url, jql_query, fetchOnly=False):

    days_ago = datetime.now() - timedelta(days=int(days))

    # Initialize a list to store all collected information
    epic_data = []

    # Step 1: Get all Epics based on your JQL filter
    # jql_query = '''
    #     project = EHGI AND
    #     ("#Key Project Status" = "Yes-POD" OR
    #     "#Key Project Status" = "Yes-Group" OR
    #     "#Key Project Status" = "Yes-Sub-Group") AND
    #     "#Quarter(New)" = "FY25-Q4"
    # '''
    epics = jira.search_issues(jql_query, maxResults=50, fields="summary")

    # Step 2: Iterate through each Epic and find linked issues
    for epic in epics:
        epic_info = {
            "epic_key": epic.key,
            "epic_summary": epic.fields.summary,
            "issues": []
        }

        jql_issues = f'"Epic Link" = {epic.key}'
        issues = jira.search_issues(jql_issues, maxResults=100, fields="summary,status,assignee")

        if not issues:
            continue

        # Step 3: Fetch changelog for each issue
        for issue in issues:
            issue_info = {
                "issue_key": issue.key,
                "issue_summary": issue.fields.summary,
                "updates": []
            }

            # Get issue changelog
            changelog = jira.issue(issue.key, expand="changelog").changelog.histories

            # Step 4: Filter updates from the last 'days' days
            for history in changelog:
                update_time = datetime.strptime(history.created[:19], "%Y-%m-%dT%H:%M:%S")
                if update_time >= days_ago:
                    update_info = {
                        "updated_by": history.author.displayName,
                        "update_time": update_time.strftime('%Y-%m-%d %H:%M:%S'),
                        "changes": []
                    }

                    for item in history.items:
                        change = {
                            "field": item.field,
                            "from_value": item.fromString if item.fromString else "None",
                            "to_value": item.toString if item.toString else "None"
                        }
                        update_info["changes"].append(change)

                    issue_info["updates"].append(update_info)

            epic_info["issues"].append(issue_info)

        epic_data.append(epic_info)




    if fetchOnly:
        return epic_data

     # if analysis also, fetech project plan and prompt
    projectPlan = fetch_google_sheets_data('1aPnyN7rkIjhpT3MzOFpl9eKpMITppoM4nzTAgNWRl0w', 'Project Plan', 'A1:Z1000')





    print("\n✅ Done!")


    integrated_prompt = f"""
    {summarize_prompt}
        Additional Inputs:
        - JIRA Data: {epic_data}
        - Project Plan: {projectPlan}
    """


    summary = generate_ai_analysis(integrated_prompt)
    print("*******************summary********************************")

    totalSummary = generate_final_insights(summary)
    print("*******************total-summary********************************")

    #report_filename = generate_report(totalSummary)
    #upload_report_to_slack("C08HCMTDU75", report_filename)
    requests.post(response_url, json={"text": totalSummary})