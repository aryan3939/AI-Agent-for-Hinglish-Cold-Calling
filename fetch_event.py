import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Load credentials
service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
credentials = service_account.Credentials.from_service_account_file(service_account_path, scopes=["https://www.googleapis.com/auth/calendar"])

# Build Calendar API service
service = build("calendar", "v3", credentials=credentials)

# Fetch upcoming 5 events
events_result = service.events().list(calendarId="primary", maxResults=5, orderBy="startTime", singleEvents=True).execute()
events = events_result.get("items", [])

calendar_list = service.calendarList().list().execute()
for calendar in calendar_list['items']:
    print(f"Calendar ID: {calendar['id']} - {calendar['summary']}")

    
if not events:
    print(" No events found. The event might not be created.")
else:
    print(" Upcoming Events in Calendar:")
    for event in events:
        print(f"- {event['summary']} at {event['start'].get('dateTime', event['start'].get('date'))}")
        print(f"  Event ID: {event['id']}")