import os
import base64
import gspread
from google.oauth2 import service_account
from dotenv import load_dotenv
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def initialize_google_sheets_client(credentials_base64=None):
    """
    Initialize and return a Google Sheets client.
    
    Args:
        credentials_base64 (str): Base64-encoded service account credentials.
        
    Returns:
        gspread.Client: Authenticated Google Sheets client.
        
    Raises:
        EnvironmentError: If credentials are not provided.
        ValueError: If credentials are invalid.
    """
    if credentials_base64 is None:
        credentials_base64 = os.getenv("GOOGLE_SHEETS_CREDS")
    
    if not credentials_base64:
        logger.error("GOOGLE_SHEETS_CREDS environment variable is not set.")
        raise EnvironmentError("GOOGLE_SHEETS_CREDS environment variable is not set.")

    try:
        credentials_json = base64.b64decode(credentials_base64)
    except base64.binascii.Error as e:
        logger.error("Failed to decode GOOGLE_SHEETS_CREDS: Invalid base64 encoding.")
        raise ValueError("Failed to decode GOOGLE_SHEETS_CREDS: Invalid base64 encoding.") from e

    try:
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(credentials_json),
            scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"],
        )
    except json.JSONDecodeError as e:
        logger.error("Failed to parse GOOGLE_SHEETS_CREDS: Invalid JSON.")
        raise ValueError("Failed to parse GOOGLE_SHEETS_CREDS: Invalid JSON.") from e

    logger.info("Google Sheets client initialized successfully.")
    return gspread.authorize(credentials)

# Initialize the client once
google_sheets_client = initialize_google_sheets_client()

def save(name, feedback, rating, sheet_name="ai-medicine-analyzer-feedback"):
    """
    Save feedback to a Google Sheets document.
    
    Args:
        name (str): Name of the person providing feedback.
        feedback (str): Feedback text.
        rating (int): Rating value.
        sheet_name (str): Name of the Google Sheets document.
        
    Raises:
        RuntimeError: If saving feedback to Google Sheets fails.
    """
    try:
        spreadsheet = google_sheets_client.open(sheet_name).sheet1
        spreadsheet.append_row([name, feedback, rating])
        logger.info("Feedback saved successfully.")
    except gspread.exceptions.APIError as e:
        logger.error(f"Failed to save feedback to Google Sheets: {str(e)}")
        raise RuntimeError(f"Failed to save feedback to Google Sheets: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")