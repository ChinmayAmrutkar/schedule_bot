# main.py

import os
import json
from datetime import datetime
import google.auth
from googleapiclient.discovery import build
import google.generativeai as genai
from flask import jsonify

# --- Configuration ---
# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Google Calendar API Scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Service Account file name
SERVICE_ACCOUNT_FILE = 'credentials.json'

# --- Google Calendar Service ---
def get_calendar_service():
    """Authenticates with Google Calendar using the service account file."""
    creds, _ = google.auth.load_credentials_from_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=creds)

# --- Main Cloud Function ---
def process_schedule_request(request):
    """
    Main Cloud Function to handle POST requests from the web interface.
    Parses user input with Gemini and creates a Google Calendar event.
    """
    # Set CORS headers for preflight requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    try:
        request_json = request.get_json(silent=True)
        if not request_json or 'text' not in request_json:
            return (jsonify({'status': 'error', 'message': 'Invalid JSON or missing text field.'}), 400, headers)
        
        user_input = request_json['text']
        if not user_input:
            return (jsonify({'status': 'error', 'message': 'No input text provided.'}), 400, headers)

        # Use Gemini to parse the request
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        
        # Improved prompt for better parsing and default duration
        prompt = f"""
        You are a highly intelligent scheduling assistant. Your task is to extract event details from user commands.
        The user is in the 'America/Phoenix' timezone. All dates and times should be interpreted from this context.
        The current date and time is: {datetime.now().isoformat()}

        User command: "{user_input}"

        Your goal is to extract the event name, date, start time, and end time.
        - If the user does not specify an end time, assume a default event duration of 1 hour.
        - If you can extract all necessary information, respond with a JSON object.
        - If you cannot understand the request, respond with the 'error' action JSON.

        Example 1: "Add a meeting tomorrow at 3pm"
        Result: {{ "action": "add", "event_name": "meeting", "date": "YYYY-MM-DD", "start_time": "15:00:00", "end_time": "16:00:00" }}

        Example 2: "Schedule a dentist appointment on September 10th from 10 AM to 10:30 AM"
        Result: {{ "action": "add", "event_name": "dentist appointment", "date": "2025-09-10", "start_time": "10:00:00", "end_time": "10:30:00" }}

        Example 3: "i need to buy some milk"
        Result: {{ "action": "error", "message": "I couldn't understand the date and time for your event. Please be more specific." }}

        Provide ONLY the JSON object in your response.

        Your Response:
        """

        response = model.generate_content(prompt)
        ai_response_text = response.text.replace('```json', '').replace('```', '').strip()
        parsed_data = json.loads(ai_response_text)

        if parsed_data.get('action') == 'add':
            # --- Input Validation ---
            required_keys = ['event_name', 'date', 'start_time', 'end_time']
            if not all(key in parsed_data for key in required_keys):
                return (jsonify({
                    'status': 'error', 
                    'message': "I understood the event, but was missing some details. Please specify a full date and time."
                }), 200, headers)

            event_name = parsed_data['event_name']
            date_str = parsed_data['date']
            start_time_str = parsed_data['start_time']
            end_time_str = parsed_data['end_time']
            
            # --- IMPORTANT: Replace with your actual Calendar ID ---
            # This is typically your Google account email address.
            calendar_id = 'your.email@gmail.com' 
            
            service = get_calendar_service()
            event_body = {
                'summary': event_name,
                'start': {
                    'dateTime': f'{date_str}T{start_time_str}',
                    'timeZone': 'America/Phoenix', # Correct timezone
                },
                'end': {
                    'dateTime': f'{date_str}T{end_time_str}',
                    'timeZone': 'America/Phoenix', # Correct timezone
                }
            }
            service.events().insert(calendarId=calendar_id, body=event_body).execute()
            
            response_data = {
                'status': 'success',
                'message': f'✅ Success! I\'ve added "{event_name}" to your calendar.'
            }
            return (jsonify(response_data), 200, headers)
        else:
            # Handle error action from Gemini
            return (jsonify(parsed_data), 200, headers)

    except json.JSONDecodeError:
        return (jsonify({'status': 'error', 'message': 'Sorry, I had trouble understanding the format of the response.'}), 500, headers)
    except Exception as e:
        # Log the error for debugging if possible
        print(f"An error occurred: {e}")
        return (jsonify({'status': 'error', 'message': f'An unexpected error occurred. Please check the server logs.'}), 500, headers)
