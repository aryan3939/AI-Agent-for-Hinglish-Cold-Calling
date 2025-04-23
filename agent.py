import os
import pyttsx3
import re
from datetime import timedelta
import speech_recognition as sr
import pandas as pd
from gtts import gTTS
import tempfile
import pygame
import random
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from langchain.schema import AIMessage, HumanMessage
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain.llms.base import LLM
from typing import List, Optional
import google.generativeai as genai
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dateutil import parser
import pytz

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
credentials = service_account.Credentials.from_service_account_file(service_account_path, scopes=["https://www.googleapis.com/auth/calendar"])

genai.configure(api_key=API_KEY)
gemini_api = genai.GenerativeModel(model_name="gemini-2.0-flash")



# Initialize Pygame for audio playback
pygame.mixer.init()

# Hinglish Greetings
OPENING_GREETINGS = [
    "Namaste! Main iMax Global Ventures ki AI agent hoon. Main aapki madad ke liye yahan hoon. Kripya ek vikalp chuney:\n"
    "1. ERP system ka demo schedule karna hai.\n"
    "2. Kisi candidate ka interview lena hai.\n"
    "3. Payment/order ka status check karna hai ya sabhi pending payments ke liye reminder email bhejni hai.",
    
    
    "Namaskar! Main iMax Global Ventures ki AI agent hoon. Aapke call ka maksad kya hai? Kripya ek vikalp chuney:\n"
    "1. ERP demo schedule karna hai.\n"
    "2. Kisi candidate ka interview lena hai.\n"
    "3. Payment/order status check karna hai ya pending payments ke liye email bhejni hai.",

    "Hello, Main iMax Global Ventures ki AI agent hoon. Main aapki kis tarah se madad kar sakti hoon? Kripya ek vikalp chuney:\n"
    "1. ERP system ka demo schedule karna hai.\n"
    "2. Kisi candidate ka interview lena hai.\n"
    "3. Payment/order ka status dekhna hai ya sabhi pending payments ko email bhejna hai.",

    "Hii, Main iMax Global Ventures ki AI agent hoon. Aap kis madad ke liye yahan hain? Kripya ek vikalp chuney:\n"
    "1. ERP demo ke liye slot book karna hai.\n"
    "2. Kisi candidate ka interview lena hai.\n"
    "3. Payment/order status check karna hai ya sabhi pending payments ka reminder bhejna hai."
]

CLOSING_GREETINGS = [
    "Dhanyavaad! Phir milenge.",
    "Aapka samay dene ke liye shukriya! Aagey bhi humse sampark karein.",
    "Baat karke achha laga, milte hain dobara!"
]

chat_history = []

def add_to_chat_history(user_input, ai_response):
    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=ai_response))

def get_chat_history():
    return "\n".join([msg.content for msg in chat_history])

def speak(text):
    print(f"AI: {text}")
    tts = gTTS(text=text, lang='hi', slow=False)
    with tempfile.NamedTemporaryFile(delete=True) as temp_audio:
        temp_audio_path = temp_audio.name + ".mp3"
        tts.save(temp_audio_path)
        pygame.mixer.music.load(temp_audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue


# Recognize Speech
def recognize_speech():
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                text = recognizer.recognize_google(audio, language="hi-En")
                hinglish_text = GoogleTranslator(source='auto', target='en').translate(text)
                print(f"User: {hinglish_text}")
                return hinglish_text.lower()

            except sr.WaitTimeoutError:
                print("Timeout! No speech detected. Restarting listening...")
                speak("Mujhe aapki awaaz sunayi nahi di. Kripya dobara bolein.")  # Ask user to speak again

            except sr.UnknownValueError:
                print("Could not understand audio. Restarting listening...")
                speak("Maaf kijiye, main samajh nahi paayi. Kripya phir se kahe.")
            except sr.RequestError:
                print("Speech recognition request failed. Check internet connection.")
                speak("Speech recognition service unavailable. Kripya apne internet connection ka pata karein.")


# Custom LangChain LLM wrapper for Google Gemini
class GoogleGeminiLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "google_gemini"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        translated_prompt = GoogleTranslator(source='auto', target='en').translate(prompt)
        response = gemini_api.generate_content(translated_prompt)
        return response.text if response and hasattr(response, "text") else "Sorry, I couldn't process that request."

custom_llm = GoogleGeminiLLM()
agent = initialize_agent(tools=[], llm=custom_llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True)




def conduct_interview():
    speak("Candidate ka naam aur position bataye please.")
    user_input = recognize_speech()
    if user_input:
        print(f"User: {user_input}")

    # Ask whether to conduct now or schedule for later
    speak("Kya aap abhi interview lena chahenge ya kisi aur din schedule karna chahenge?")
    choice = recognize_speech().lower()

    if "schedule" in choice or "baad" in choice or "dusre" in choice:
        schedule_interview(user_input)
        return

    # Extract role from user input
    role = user_input.split()[-3:]  # Extract last three words as role
    role = " ".join(role)  # Convert list to string

    # Start AI-led interview
    speak(f"Main {role} ke liye interview shuru kar rahi hoon. Aap jab chahein 'exit' bolkar interview khatam kar sakte hain.")

    while True:
        # AI generates a domain-specific simple question
        response = agent.invoke({
            "input": f"Ask a short, one-line interview question for a {role} role.",
            "chat_history": get_chat_history()
        })

        ai_question = response if isinstance(response, str) else response.get("output", "No question generated.")
        print(f"AI: {ai_question}")
        speak(ai_question)

        # User responds
        user_answer = recognize_speech()
        if "exit" in user_answer.lower():
            speak("Interview samapt ho gaya hai. Dhanyavaad!")
            break

        print(f"User: {user_answer}")
        add_to_chat_history(ai_question, user_answer)



def extract_datetime(user_input):
    """Extracts and converts natural language date-time to ISO 8601 format."""
    try:
        # Convert text into a datetime object
        parsed_datetime = parser.parse(user_input, fuzzy=True)
        
        # Convert to ISO 8601 format with timezone
        ist = pytz.timezone("Asia/Kolkata")
        parsed_datetime = ist.localize(parsed_datetime)
        return parsed_datetime.isoformat()
    except Exception as e:
        print(f" Date parsing error: {e}")
        return None

def schedule_interview(candidate_name):
    speak("Kripya interview ka date aur time bataye.")
    user_input = recognize_speech()  

    event_datetime = extract_datetime(user_input)
    if not event_datetime:
        speak("Mujhe samajh nahi aaya. Kripya dobara date aur time bataye.")
        return

    credentials = service_account.Credentials.from_service_account_file(service_account_path, scopes=["https://www.googleapis.com/auth/calendar"])
    service = build("calendar", "v3", credentials=credentials)

    event = {
        "summary": f"Interview with {candidate_name}",
        "start": {"dateTime": event_datetime, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": event_datetime, "timeZone": "Asia/Kolkata"},
    }

    try:
        service.events().insert(calendarId="primary", body=event).execute()
        speak(f"Interview {candidate_name} ke saath {user_input} ke liye schedule ho gaya hai.")
    except Exception as e:
        speak("Interview schedule karne me samasya aayi hai.")
        print(f"Error: {e}")





def schedule_demo():
    speak("Kripya demo ka date aur time bataye.")
    user_input = recognize_speech()  

    event_datetime = extract_datetime(user_input)
    if not event_datetime:
        speak(" Mujhe samajh nahi aaya. Kripya dobara date aur time bataye.")
        return

    credentials = service_account.Credentials.from_service_account_file(
        os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"), 
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    service = build("calendar", "v3", credentials=credentials)

    event = {
        "summary": "ERP System Product Demo",
        "description": "Live demo of the ERP system features and capabilities.",
        "start": {"dateTime": event_datetime, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": (parser.parse(event_datetime) + timedelta(minutes=45)).isoformat(), "timeZone": "Asia/Kolkata"},
        "reminders": {"useDefault": False, "overrides": [{"method": "email", "minutes": 30}]}
    }

    try:
        service.events().insert(calendarId="primary", body=event).execute()
        speak(f" ERP System ka demo {user_input} ke liye schedule ho gaya hai.")
    except Exception as e:
        speak(" Demo schedule karne me samasya aayi hai.")
        print(f"Error: {e}")




def extract_order_id(text):
    """Extracts order ID using regex and removes spaces (e.g., 'ORD 0014' → 'ORD0014')."""
    match = re.search(r"\bORD\s*\d+\b", text, re.IGNORECASE)
    if match:
        return match.group(0).replace(" ", "")  # Remove spaces from order ID
    return None

def payment_status():
    """Asks user whether they want to check a specific order or send reminders to all pending customers."""
    speak("Kya aap sabhi pending payments ke liye payment reminder email bhejna chahenge, ya kisi ek order ka status dekhna chahenge?")
    speak("Kripya bataye: 'Sabhi Orders' ya 'Specific Order'")
    
    user_input = recognize_speech().lower()

    if "sabhi" in user_input or "all" in user_input:
        pending_payments()
    else:
        get_order_status()

def get_order_status():
    """Fetches order status and asks if user wants to send an email if payment is pending."""
    order_data = pd.read_csv("customer_orders.csv")
    speak("Apna order ID bataye please.")
    user_input = recognize_speech()
    
    if user_input:
        print(f"User: {user_input}")
    
    # Extract and clean order ID
    order_id = extract_order_id(user_input) if user_input else None

    if order_id:
        # Ensure case-insensitive and space-free matching
        order_data["Order ID"] = order_data["Order ID"].str.replace(" ", "").str.lower()
        order_id = order_id.lower()

        record = order_data[order_data["Order ID"] == order_id]
        
        if not record.empty:
            status = record.iloc[0]["Status"]
            amount_due = record.iloc[0]["Amount Due"]
            customer_email = record.iloc[0]["Email"]
            customer_name = record.iloc[0]["Customer Name"]

            if status.lower() == "paid":
                response = f"Order {order_id.upper()}: Payment completed. No dues remaining."
                print(response)
                speak(response)
                return response
            else:
                response = f"Order {order_id.upper()}: Payment pending. Amount Due: ₹{amount_due}"
                print(response)
                speak(response)

                # Ask if the user wants to send an email reminder
                speak("Kya aap customer ko payment reminder bhejna chahenge? (Haan ya Nahi)")
                user_response = recognize_speech().lower()

                if "haan" in user_response or "yes" in user_response:
                    send_payment_reminder(customer_name, customer_email, order_id, amount_due)
                else:
                    speak("Thik hai, reminder nahi bheja gaya.")

                return response

    speak("Invalid Order ID.")
    return "Invalid Order ID."

def send_payment_reminder(name, email, order_id, amount_due):
    """Function to send an email reminder for pending payments."""
    subject = f"Payment Reminder: Order {order_id}"
    body = f"""
    Dear {name},

    This is a reminder that your payment of ₹{amount_due} for Order {order_id} is still pending.
    Kindly make the payment at your earliest convenience.

    If you have already made the payment, please disregard this message.

    Thank you,
    Your Company Name
    """

    # Since emails are dummy, print the email content instead of sending
    print(f"\n (TEST) Email to {email} - {subject}\n{body}\n")
    speak(f" Payment reminder email bhej diya gaya hai {name} ko.")

def pending_payments():
    """Sends payment reminders to all customers with pending payments."""
    df = pd.read_csv("customer_orders.csv")

    # Filter only pending payments
    pending_customers = df[df["Status"] == "Pending"]

    if pending_customers.empty:
        print(" No pending payments. All customers have paid.")
        return

    # Iterate through each pending customer
    for _, row in pending_customers.iterrows():
        email = row["Email"]
        name = row["Customer Name"]
        order_id = row["Order ID"]
        amount_due = row["Amount Due"]

        subject = f"Payment Reminder: Order {order_id}"
        body = f"""
        Dear {name},

        This is a reminder that your payment of ₹{amount_due} for Order {order_id} is still pending.
        Kindly make the payment at your earliest convenience.

        If you have already made the payment, please disregard this message.

        Thank you,
        Your Company Name
        """

        # Since emails are dummy, print the email content instead of sending
        print(f"\n (TEST) Email to {email} - {subject}\n{body}\n")

    print(" All pending payment customers' mail sent successfully!")





# Main Cold Call Agent
def cold_call_agent():
    speak(random.choice(OPENING_GREETINGS))
    while True:
        user_input = recognize_speech()
        if not user_input:
            continue
        if "exit" in user_input or "thank you" in user_input or "thanks" in user_input or "thank" in user_input or "bye" in user_input:
            speak(random.choice(CLOSING_GREETINGS))
            break
        elif "order" in user_input or "payment" in user_input or "status" in user_input:
            payment_status()
        elif "interview" in user_input:
            conduct_interview()
        elif "demo" in user_input or "demonstration" in user_input or "product" in user_input:
            schedule_demo()
        else:
            speak("Kripya spasht bataye ki aap kis vishay par madad chahte hain: Payment status, Interview, ya Product Demonstration?")
    

if __name__ == "__main__":
    cold_call_agent()
