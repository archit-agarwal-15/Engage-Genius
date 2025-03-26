from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from config import GOOGLE_CREDENTIALS
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def fetch_google_sheets_data(spreadsheet_id, sheet_name, range_value):
    """Fetch data from Google Sheets."""
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('sheets', 'v4', credentials=creds)
    range_query = f'{sheet_name}!{range_value}'
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_query).execute()
    return result.get('values', [])

def fetch_all_sheets_data(spreadsheet_id):
    """Fetch data from all sheets in a given Google Spreadsheet."""
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    try:
        service = build("sheets", "v4", credentials=creds)
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get("sheets", [])

        all_sheets_data = {}
        for sheet in sheets:
            sheet_name = sheet["properties"]["title"]
            range_query = f"'{sheet_name}'!A1:Z100"  # Adjust range as needed
            try:
                result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_query).execute()
            except Exception as e:
                logging.error(f"Error fetching Google Sheets data: {e}")
            all_sheets_data[sheet_name] = result.get("values", [])

        return all_sheets_data
    except Exception as e:
        logging.error(f"Error fetching Google Sheets data: {e}")
        return {}

def fetch_google_doc_data(document_id):
    """Fetch content from a Google Doc."""
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('docs', 'v1', credentials=creds)
    doc = service.documents().get(documentId=document_id).execute()
    content = []
    for element in doc.get('body', {}).get('content', []):
        if 'paragraph' in element:
            for text_run in element['paragraph'].get('elements', []):
                if 'textRun' in text_run:
                    content.append(text_run['textRun']['content'])
    return "".join(content)
