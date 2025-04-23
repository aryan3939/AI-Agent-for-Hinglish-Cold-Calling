import os
from googleapiclient.discovery import build
from google.oauth2 import service_account


# Load credentials
service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
credentials = service_account.Credentials.from_service_account_file(
    service_account_path, scopes=["https://www.googleapis.com/auth/calendar"]
)

# Build Calendar API service
service = build("calendar", "v3", credentials=credentials)


def delete_event(event_id):
    try:
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        print(f" Event with ID {event_id} deleted successfully.")
    except Exception as e:
        print(f" Error deleting event: {e}")

# Example Usage
event = str(input("Enter Event ID Here: "))
delete_event(str(event))  # Replace with actual event ID