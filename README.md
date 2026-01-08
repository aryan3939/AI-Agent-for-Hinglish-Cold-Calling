# AI Agent for Hinglish Cold Calling

## Project Description
This project implements an AI-powered agent designed for conducting human-like cold calls in Hinglish. The agent can:
1. **Schedule product demos** for an ERP system.
2. **Conduct candidate interviews** by asking relevant questions and recording responses and can also schedule interviews.
3. **Follow up on payments/orders** by checking status and sending reminders.

The agent is capable of understanding context, personalizing interactions, and exhibiting human-like conversational abilities in Hinglish. It leverages **LLM-based dialogue generation, speech recognition, and text-to-speech synthesis** to enable realistic conversations.

---
## Setup Instructions
### 1. Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Virtual environment (optional but recommended)
- API access credentials for Google Calendar
- Required Python libraries (see `requirements.txt`)

### 2. Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/aryan3939/AI-Agent-for-Hinglish-Cold-Calling.git
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Mac/Linux
   venv\Scripts\activate  # On Windows
   ```
3. Install dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
4. **Download Google Service Account JSON and Set Permissions:**
   - Go to **Google Cloud Console**: https://console.cloud.google.com/
   - Navigate to **IAM & Admin > Service Accounts**.
   - Select your project and create a new service account.
   - Assign **Editor** and **Calendar API permissions** to the service account.
   - Generate a **JSON key file** and download it.
   - Move this file to your project directory and set its path in the `.env` file.
   - **Provide access to the client email in the JSON file** by sharing calendar access with this email.
   - Enable **Google Calendar API** in the Google Cloud Console to allow scheduling functionality.

5. Create a `.env` file for storing API keys and credentials securely. Refer to `.env.example` for required variables.
6. Run the AI agent:
   ```bash
   python agent.py
   ```

---
## Environment Variables
Create a `.env` file and define the following variables:
```
GOOGLE_API_KEY="your_google_api_key_here"
GOOGLE_SERVICE_ACCOUNT_JSON="path_to_your_service_account.json"
```

---
## Models & Technologies Used
- **Google Gemini API (2.0 Flash Model)** for language understanding and response generation.
- **Speech Recognition** (Google's STT) for converting user speech into text.
- **gTTS** for text-to-speech output.
- **Google Calendar API** for scheduling interviews and demos.
- **Pandas** for handling customer and order data.
- **LangChain** for AI-driven agent design.
- **Pygame** for audio playback.

---
## How the AI Agent Performs These Tasks
1. **Demo Scheduling:**
   - The agent interacts with the user in Hinglish and asks for a suitable date and time for a product demonstration.
   - It then schedules the demo using the **Google Calendar API** and confirms the appointment.

2. **Candidate Interviewing:**
   - The agent asks for the candidate’s name and position.
   - It generates interview questions using **Google Gemini 2.0 Flash Model**.
   - The interview is conducted, and responses are stored in the chat history.
   - If the user prefers to schedule the interview for later, the agent schedules it via **Google Calendar API**.

3. **Payment/Order Follow-up:**
   - The agent asks the user whether they want to check a specific order or send reminders to all pending customers.
   - It retrieves order details from a **dummy dataset** (created using `create_dummy_customers.py`).
   - If payment is pending, it asks whether a reminder email should be sent.
   - **Note:** Since dummy emails are used, the system **does not actually send emails** but prints a success message if no errors occur.

---
## Managing Scheduled Events
- **View Scheduled Events:** Run `fetch_event.py` to list upcoming events from Google Calendar.
- **Delete an Event:** Use `delete_event.py` to remove a specific event by providing the event ID.

---
## Features Implemented
 **Speech-to-text and text-to-speech**
 **Cold call decision-making (demo, interview, or payment follow-up)**
 **Google Calendar integration for scheduling**
 **LLM-driven conversational AI (Google Gemini 2.0 Flash Model)**
 **Handling payment reminders via order data**
 **Order status retrieval and confirmation before sending reminders**

### Partial Implementations / Improvements Needed
 **Enhanced state management** (currently minimal tracking of user inputs)
 **Sentiment analysis** (future enhancement for better user response handling)
 **Improved Hinglish response accuracy** (could be fine-tuned)

---
## Files Overview
| File | Description |
|------|------------|
| `agent.py` | Main AI agent script |
| `create_dummy_customers.py` | Generates dummy customer order data |
| `delete_event.py` | Deletes scheduled events from Google Calendar |
| `fetch_event.py` | Fetches upcoming events from Google Calendar |
| `requirements.txt` | List of required Python packages |
| `.env.example` | Sample environment variable file |

---
## Running Tests
To test the AI agent, run:
```bash
python agent.py
```
It will prompt the user to choose an action and respond accordingly.


