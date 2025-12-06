import datetime
import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Als je scopes aanpast, verwijder dan token.json!
SCOPES = ['https://www.googleapis.com/auth/calendar']

class KikuCalendar:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Regelt de inlog bij Google."""
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # Als er geen (geldige) credentials zijn, laat de gebruiker inloggen.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Let op: Op een headless Pi moet je dit misschien eerst op Windows doen
                # en dan de token.json kopiëren!
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Sla de token op voor de volgende keer
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('calendar', 'v3', credentials=self.creds)
        print("[Calendar] ✅ Verbonden met Google Agenda.")

    def get_week_preview(self):
        """Haalt afspraken voor de komende 7 dagen op."""
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        next_week = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat() + 'Z'
        
        print("[Calendar] 🔄 Syncen met Google (Google is leidend)...")
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                              timeMax=next_week, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events

    def add_event(self, summary, start_time_str, duration_minutes=60):
        """
        Voegt een afspraak toe.
        Format start_time_str: '2025-12-06T15:00:00' (ISO)
        """
        try:
            start = datetime.datetime.fromisoformat(start_time_str)
            end = start + datetime.timedelta(minutes=duration_minutes)
            
            event = {
              'summary': summary,
              'start': {'dateTime': start.isoformat(), 'timeZone': 'Europe/Amsterdam'},
              'end': {'dateTime': end.isoformat(), 'timeZone': 'Europe/Amsterdam'},
            }

            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return f"Afspraak '{summary}' gemaakt voor {start.strftime('%d-%m om %H:%M')}."
        except Exception as e:
            return f"Fout bij maken afspraak: {e}"

    def check_upcoming_reminders(self):
        """Kijkt of er een afspraak start binnen nu en 15 minuten."""
        now = datetime.datetime.utcnow()
        soon = now + datetime.timedelta(minutes=15)
        
        events_result = self.service.events().list(calendarId='primary', 
                                              timeMin=now.isoformat() + 'Z',
                                              timeMax=soon.isoformat() + 'Z', 
                                              singleEvents=True).execute()
        events = events_result.get('items', [])
        
        reminders = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event['summary']
            # Simpele check om spam te voorkomen (zou in het echt slimmer moeten met een 'gezien' vlaggetje)
            reminders.append(f"Herinnering: '{summary}' begint bijna!")
            
        return reminders
