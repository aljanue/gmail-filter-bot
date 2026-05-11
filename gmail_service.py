import os
from typing import List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from logger import get_logger

logger = get_logger(__name__)

class GmailService:
    def __init__(self, credentials_file: str, token_file: str, scopes: List[str]):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.service = None

    def authenticate(self):
        creds = None
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            except Exception as e:
                logger.warning(f"Could not read local {self.token_file}: {e}")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired Google token...")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Failed to refresh token: {e}. Manual re-authentication required.")
                    if os.path.exists(self.token_file):
                        os.remove(self.token_file)
                    raise
            else:
                logger.info("Starting manual authorization flow (Handshake)...")
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scopes)
                creds = flow.run_local_server(port=0)
                
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
                
        self.service = build('gmail', 'v1', credentials=creds, cache_discovery=False)

    def fetch_unread_messages(self, emails: List[str]) -> List[Dict[str, Any]]:
        if not emails or not self.service:
            return []

        query_parts = [f"from:{email}" for email in emails]
        query = f"is:unread ({' OR '.join(query_parts)})"
        
        try:
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            parsed_messages = []
            for msg in messages:
                m = self.service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
                headers = m['payload']['headers']
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No subject")
                sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
                snippet = m.get('snippet', '')
                
                parsed_messages.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'snippet': snippet
                })
            return parsed_messages
        except Exception as e:
            logger.error(f"Error fetching messages: {e}", exc_info=True)
            return []