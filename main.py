# main.py

import os
import json
from datetime import datetime, timedelta
import google.auth
from googleapiclient.discovery import build
from google.generativeai import GenerativeModel, configure

# --- Configuration ---
# Your Gemini API key
configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Google Calendar API Scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Service Account file name
SERVICE_ACCOUNT_FILE = 'credentials.json'

def get_calendar_service():
    """
    Authenticates with Google Calendar using the service account file.
    """
    creds, _ = google.auth.load_credentials_from_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=creds)

def process_schedule_request(request):
    """
    Main function for the Cloud Function.
    Handles a POST request from the web interface.
    """
    try:
        request_json = request.get_json(silent=True)
        user_input = request_json.get('text', '')

        if not user_input:
            return {'status': 'error', 'message': 'No input text provided.'}, 400

        # Use Gemini to parse the request
        model = GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"""
        You are a highly intelligent and helpful scheduling assistant. Your task is to extract event details from user commands.
        If the user wants to add an event, extract the event name, date, and time.
        Format your response as a JSON object with the following keys:
        - "action": "add"
        - "event_name": "[Event Name]"
        - "date": "[YYYY-MM-DD]"
        - "start_time": "[HH:MM:SS]"
        - "end_time": "[HH:MM:SS]"

        If you cannot extract the required information, respond with:
        {{
            "action": "error",
            "message": "I could not understand your request. Please specify the event, date, and time."
        }}

        Current date and time: {datetime.now().isoformat()}

        User command: "{user_input}"
        """

        response = model.generate_content(prompt)
        ai_response_text = response.text.replace('```json', '').replace('```', '').strip()
        parsed_data = json.loads(ai_response_text)

        if parsed_data.get('action') == 'add':
            event_name = parsed_data.get('event_name')
            date_str = parsed_data.get('date')
            start_time_str = parsed_data.get('start_time')
            end_time_str = parsed_data.get('end_time')

            # Let's assume the user's primary calendar ID is 'primary'
            calendar_id = 'primary'
            
            # Create a Google Calendar event
            service = get_calendar_service()
            event_body = {
                'summary': event_name,
                'start': {
                    'dateTime': f'{date_str}T{start_time_str}',
                    'timeZone': 'UTC',  # Adjust to your timezone later
                },
                'end': {
                    'dateTime': f'{date_str}T{end_time_str}',
                    'timeZone': 'UTC',
                }
            }
            event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
            
            return {
                'status': 'success',
                'message': f'Event "{event_name}" has been added to your calendar!'
            }, 200

        else:
            return parsed_data, 200

    except Exception as e:
        return {'status': 'error', 'message': f'An error occurred: {str(e)}'}, 500
