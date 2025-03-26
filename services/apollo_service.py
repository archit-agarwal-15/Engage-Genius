import logging
from services.google_service import fetch_google_sheets_data, fetch_google_doc_data
from services.slack_service import fetch_slack_messages
from services.openai_service import generate_ai_analysis

def generate_final_insights(jira_summary):
    # slack_summary = generate_ai_analysis(f"Summarize the following Slack messages: {fetch_slack_messages(CHANNEL_ID)}")




    slack_summary_2 = generate_ai_analysis(f"""Tell me about updates from slack message added below. Concentrate only on "GC Issuing"
        {fetch_slack_messages(CHANNEL_ID_2)}""")



    print("slack_summary_2")


    sheets_summary = generate_ai_analysis(f"""
    Analyze the Google Sheet data, specifically filtering for metrics under the 'GC Issuance' category (L0 and associated L1s). Exclude any unrelated sections.
    For the filtered data:

    Compare the 'Target' and 'Actual' values — highlight significant gaps or overachievements.
    Identify metrics that are closest to their targets and those that are farthest.
    Analyze patterns or trends among the L1 metrics related to 'GC Issuance.'
    Suggest potential areas for improvement based on discrepancies between targets and actuals.
    Provide data-driven insights or recommendations to optimize performance in areas with notable gaps.

    Ensure the analysis remains focused only on 'GC Issuance' and avoids unrelated data." {fetch_google_sheets_data('13R3WgzPsrXc1TvK6Q-CoIOre0M8NFINR4SLbpjhnX_4', 'Staff Review', 'A1:V7')}""")
    final_summary_doc = fetch_google_doc_data('11J0QhFRX2bK-I5SYw5_-U00xY38YckpwP6Knx6PnGUE')

    summary_parts = [
        "📌 Executive Summary\nIn [Quarter], our primary focus is to:",
        "🎯 OKR Table\n| OKR | [Month] | [Previous Month] |",
        "🏆 Highlights\n1. **[Key achievement 1]** - [Brief explanation of impact].",
        "⚠️ Lowlights\n1. **[Challenge/blocker 1]** - [Brief explanation of impact].",
        "📌 Key Projects\n| Related OKR | Project | RAG Status | Status | Goal |",
        "🌍 GTM Updates\n### **[Initiative 1] Updates**",
        "🚧 Challenges\n### **[Issue Category 1]**\n- **Description:** [Brief description of the challenge]",
        "✅ Path to Green\n[OKR/Initiative 1]\n- Current status: [Current status of the OKR/initiative]"
    ]

    insights = []
    for part in summary_parts:
        result = generate_ai_analysis(f"""
            Using this section template: {part}
            Consolidate the following summaries into a well-formatted Slack message. Mark sure to put only relevant messages as per the section heading
            Format the message with:
            - Proper Slack markdown (bold, italics, bullet points)
            - Clear section headers with emojis
            - Concise, scannable content
            - A consistent and professional tone

            Source summaries to consolidate:
            - Slack: {slack_summary_2}
            - Google Sheets: {sheets_summary}
            - JIRA: {jira_summary}""")
        insights.append(result)

    final_insight = "\n".join(insights)
    return final_insight
