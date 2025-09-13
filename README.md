# AI Scheduling Assistant for Google Calendar

This project is a full-stack, AI-powered chatbot that acts as a personal scheduling assistant. It allows users to manage their Google Calendar through a simple, conversational web interface, translating natural language commands into specific calendar actions.

The application leverages the power of the Google Gemini API to understand complex, multi-event requests and integrates directly with the Google Calendar API to perform actions in real-time.

## ✨ Features

* **Natural Language Processing:** Add, delete, and list calendar events using everyday language.
* **Complex Parsing:** Can process an entire week's schedule from a single block of text and add each event individually.
* **Multi-Functionality:** Supports creating, deleting, and listing events with contextual understanding.
* **Direct Google Calendar Integration:** All actions are reflected immediately in the user's specified Google Calendar.
* **Modern Chat Interface:** A clean, responsive, and user-friendly chat UI for seamless interaction.

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Backend:** Python, Google Cloud Functions (2nd Gen, running on Cloud Run)
* **AI & APIs:**
    * **Google Gemini API:** For state-of-the-art natural language understanding and JSON generation.
    * **Google Calendar API:** For creating, managing, and reading calendar events.
* **Platform & Tools:**
    * **Google Cloud Platform:** For hosting the serverless backend, managing authentication, and logging.
    * **Google Cloud IAM:** For secure service account management.
    * **GitHub Pages:** For hosting the static frontend.

## 🚀 Setup and Deployment Guide

Follow these steps to deploy your own instance of the AI Scheduling Assistant.

### Prerequisites

* A Google Cloud Project with billing enabled.
* The `gcloud` command-line tool installed and configured.
* Python 3.9+ installed locally.
* A personal Google Calendar you want to manage.

### 1. Backend Setup

1.  **Enable APIs:** In your Google Cloud project, enable the **Google Calendar API** and the **Vertex AI API** (which provides access to Gemini).
2.  **Create a Service Account:**
    * Navigate to **IAM & Admin > Service Accounts**.
    * Create a new service account (e.g., `schedule-bot-account`).
    * Generate a **JSON key** for this service account and download it. Rename this file to `credentials.json`.
3.  **Share Your Calendar:**
    * Open your `credentials.json` file and copy the `client_email`.
    * Go to your Google Calendar settings and find the specific calendar you want to use.
    * Under "Share with specific people or groups," add the `client_email` and give it **"Make changes to events"** permission.
4.  **Prepare Backend Code:**
    * Place your `main.py` and `credentials.json` files in a new directory.
    * Create a file named `requirements.txt` in the same directory with the following content:
        ```
        google-api-python-client
        google-auth-httplib2
        google-auth-oauthlib
        google-generativeai
        Flask
        ```
5.  **Deploy to Google Cloud:**
    * Open your terminal or the Google Cloud Shell and navigate to your backend directory.
    * Run the following command to deploy the function. Remember to set your Gemini API key as an environment variable.
        ```
        gcloud functions deploy process-schedule-request \
          --gen2 \
          --runtime=python311 \
          --region=us-west1 \
          --source=. \
          --entry-point=process_schedule_request \
          --trigger-http \
          --allow-unauthenticated \
          --set-env-vars=GEMINI_API_KEY=YOUR_GEMINI_API_KEY
        ```
    * After deployment, copy the **HTTPS Trigger URL**. This is your backend endpoint.

### 2. Frontend Setup

1.  **Configure the URL:**
    * Open the `script.js` file.
    * Find the `backendUrl` constant and paste the Trigger URL you copied from the backend deployment.
2.  **Deploy Frontend:**
    * Host the frontend files (`index.html`, `style.css`, `script.js`) on any static hosting provider, such as GitHub Pages or Netlify.

## 💬 How to Use

Interact with the bot using natural language. Here are some examples:

* **To add a single event:**
    > `Schedule a team meeting tomorrow at 3 PM for one hour.`
* **To list events:**
    > `What's on my schedule for today?`
* **To delete an event:**
    > `Delete the 10am project sync on Monday.`
* **To add an entire week's schedule:**
    > `Add my schedule for the week: - Monday: Gym from 6 PM to 7 PM. - Tuesday: Dentist appointment at 10 AM. - Wednesday: Lunch with Alex from 1 PM to 2 PM.`

## 🧠 Project Evolution & Key Learnings

This project evolved significantly from a simple script to a multi-functional AI assistant. The key challenges and learning experiences were:

* **Authentication:** Mastered the distinction between user-based OAuth and server-to-server authentication with Service Accounts, a critical concept for building backend applications that interact with Google services.
* **Cloud Deployment & Debugging:** Gained hands-on experience deploying a serverless Python application and debugging a range of real-world HTTP errors (400, 404, 500) related to cloud permissions, IAM roles, and CORS policies.
* **Advanced Prompt Engineering:** Learned to iteratively refine the prompt sent to the Gemini model, transforming it from a simple instruction-follower into a sophisticated parsing engine capable of classifying intent (add/delete/list) and handling complex, unstructured data with high accuracy.
