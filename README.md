# MindBridge

MindBridge is a student mental wellness web application that combines AI-powered support chat, daily mood tracking, and real-time risk monitoring for counsellors — all built on a serverless Azure backend.

---

## Features

### Student
- **AI Support Chat** — Conversational mental wellness assistant powered by Groq (LLaMA 3.1). Responds empathetically and flags high-risk messages automatically.
- **Daily Mood Check-in** — Log your mood (Happy, Neutral, Sad, Anxious, Angry) with an optional note each day.
- **Mood History** — View a timeline of past mood entries.
- **Dashboard** — Personalised greeting and quick access to all features.

### Counsellor
- **Risk Alert Dashboard** — Real-time view of all unresolved high-risk alerts triggered by student chat messages.
- **Alert Resolution** — Mark alerts as resolved with a single click, with a timestamp recorded automatically.
- **Alert Statistics** — At-a-glance counts for pending high-risk alerts, total active alerts, and resolved-today count.

### Auth
- **Register / Login** — Students and counsellors share the same auth page; role is selected at registration.
- Passwords are stored as SHA-256 hashes.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla HTML / CSS / JavaScript |
| Backend | Python · Azure Functions v2 (HTTP triggers) |
| AI | Groq API — `llama-3.1-8b-instant` (via OpenAI-compatible SDK) |
| Database | Azure Cosmos DB (NoSQL) |
| Hosting | Azure Functions (serverless) |

---

## Project Structure

```
MindBridge/
├── backend/
│   ├── function_app.py      # All Azure Function HTTP endpoints
│   ├── cosmos_client.py     # Cosmos DB connection helper
│   ├── host.json            # Azure Functions host config
│   ├── local.settings.json  # Local environment variables (not committed)
│   └── requirements.txt     # Python dependencies
└── frontend/
    ├── auth/                # Login & registration page
    ├── student/             # Student dashboard, chat, mood pages
    └── counsellor/          # Counsellor dashboard
```

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/enter` | Register a new student or counsellor |
| `POST` | `/api/login` | Authenticate and return user profile |
| `POST` | `/api/chat` | Send a message; get AI reply + risk flag |
| `POST` | `/api/mood` | Log today's mood entry |
| `GET`  | `/api/moods?studentId=` | Retrieve all mood entries for a student |
| `GET`  | `/api/counsellor/alerts` | List all unresolved risk alerts |
| `POST` | `/api/counsellor/resolve` | Mark a risk alert as resolved |

### Risk Detection
The chat endpoint automatically scans messages for keywords such as *suicide*, *self harm*, *hopeless*, *anxious*, *panic*, and others. Any match creates a **HIGH** risk alert visible to counsellors.

---

## Cosmos DB Containers

| Container | Purpose |
|-----------|---------|
| `users` | Student and counsellor accounts |
| `chat_summaries` | Full chat history per student |
| `moods` | Daily mood logs per student |
| `risk_alerts` | Risk alerts generated from chat |

---

## Getting Started

### Prerequisites
- Python 3.11+
- [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- An Azure Cosmos DB account
- A [Groq API key](https://console.groq.com/)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/MindBridge.git
   cd MindBridge
   ```

2. **Create and activate a virtual environment**
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Edit `backend/local.settings.json`:
   ```json
   {
     "IsEncrypted": false,
     "Values": {
       "AzureWebJobsStorage": "UseDevelopmentStorage=true",
       "FUNCTIONS_WORKER_RUNTIME": "python",
       "GROQ_API_KEY": "<your-groq-api-key>",
       "COSMOS_ENDPOINT": "<your-cosmos-endpoint>",
       "COSMOS_KEY": "<your-cosmos-key>",
       "COSMOS_DB_NAME": "<your-database-name>"
     }
   }
   ```

5. **Start the Azure Functions host**
   ```bash
   func host start
   ```

6. **Open the frontend**

   Open `frontend/auth/index.html` in your browser (or serve the `frontend/` folder with any static file server).

---

## Deployment

Deploy the backend to Azure Functions via VS Code (**Azure Functions** extension → *Deploy to Function App*) or the Azure CLI:

```bash
az functionapp deployment source config-zip \
  --resource-group <rg> \
  --name <function-app-name> \
  --src build.zip
```

Update the API base URL in the frontend JS files to point to your deployed Function App URL before hosting the static files.

---

## License

This project is licensed under the [MIT License](LICENSE).

