import logging
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import SLACK_BOT_TOKEN

slack_client = WebClient(token=SLACK_BOT_TOKEN)

def send_slack_message(channel, message):
    """Send a message to Slack."""
    try:
        slack_client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        logging.error(f"Slack message sending failed: {e}")

def fetch_slack_messages(channel_id, limit=50):
    """Fetches recent messages and their replies from Slack."""
    try:
        response = slack_client.conversations_history(channel=channel_id, limit=limit)
        messages = response.get("messages", [])
        formatted_messages = []

        thread_ts_list = [msg["thread_ts"] for msg in messages if "thread_ts" in msg]

        # Batch fetch thread messages
        thread_replies = fetch_threads_bulk(channel_id, thread_ts_list)

        for msg in messages:
            formatted_messages.append(msg["text"])
            if msg.get("thread_ts") in thread_replies:
                formatted_messages.extend(thread_replies[msg["thread_ts"]])

        return formatted_messages
    except SlackApiError as e:
        logging.error(f"Error fetching Slack messages: {e}")
        return []

def fetch_threads_bulk(channel_id, thread_ts_list):
    """Fetch multiple Slack threads in parallel."""
    thread_data = {}
    for ts in thread_ts_list:
        try:
            response = slack_client.conversations_replies(channel=channel_id, ts=ts)
            thread_data[ts] = [msg.get("text", "No text") for msg in response.get("messages", [])]
        except SlackApiError as e:
            logging.error(f"Error fetching Slack thread: {e}")
    return thread_data

