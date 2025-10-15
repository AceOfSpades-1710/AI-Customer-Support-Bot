# AI Customer Support Bot

This repository contains an AI-powered customer support bot built with Flask, integrated with the Groq LLM, and featuring contextual memory and session tracking using Neon Postgres. The bot provides FAQ-based responses, escalation suggestions, and a responsive chat interface.

## Description

"AI Customer Support Bot with contextual memory, FAQ support, session tracking on Neon Postgres, and a responsive chat interface."

## Features

- **Contextual Memory**: Remembers the entire conversation history within a session, allowing the bot to reference previous messages (e.g., recalling your name or preferences).
- **FAQ Support**: Answers common questions using a predefined `faqs.json` dataset.
- **Escalation**: Suggests escalating to a human agent for complex queries.
- **Session Management**: Tracks multiple chat sessions with previews in a sidebar, stored in Neon Postgres for scalability.
- **Responsive Interface**: Optional frontend with a clean chat UI, supporting new chats and session switching.
- **Cloud Database**: Migrated from local SQLite to Neon Postgres for robust session storage.

## Prerequisites

- Python 3.9+
- Virtual environment (recommended)
- Neon Postgres account (free tier available at [console.neon.tech](https://console.neon.tech))
- Groq API key (sign up at [console.groq.com](https://console.groq.com))

## Installation

1. **Clone the Repository**:
git clone https://github.com/your-username/ai-customer-support-bot.git
cd ai-customer-support-bot

2. **Set Up Virtual Environment**:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


3. **Install Dependencies**:
pip install flask groq dotenv psycopg2-binary -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=100


4. **Configure Environment Variables**:
- Create a `.env` file in the root directory.
- Add the following:
    OPENAI_API_KEY=your_groq_api_key_here
    NEON_KEY=your_connection_string

- Replace `your_groq_api_key_here` with your Groq API key.
- Replace the `NEON_KEY` value with your Neon Postgres connection string (from Neon dashboard > Connection Details).

5. **Prepare FAQ Data**:
- Ensure `faqs.json` exists in the root directory with a structure like:
```json
{
  "faqs": [
    {"question": "What is your return policy?", "answer": "Returns are accepted within 30 days."},
    {"question": "How do I contact support?", "answer": "Email us at support@example.com."}
  ]
}
```

## Usage

1. **Run the Application**:
   python3 app.py


2. **Access the Bot**:
- Open your browser and go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).
- Start chatting! Use the "+ New Chat" button to begin a new session.

3. **Test Features**:
- Say "My name is Alice" and later "What is my name?" to test memory.
- Ask "How to fix my spaceship?" to trigger escalation.
- Switch sessions via the sidebar to see stored history.

## Database Setup

- **Migration**: Switched from local SQLite (sessions.db) to Neon Postgres for scalable session tracking.
- **Connection**: Set NEON_KEY in .env with your Neon connection string.
- **Install**: pip install psycopg2-binary.
- **Schema**: sessions table with session_id (PK) and history (TEXT for chat logs).

## Video Demo Link

## Project Structure

```mermaid
graph TD
    A[AI Customer Care Bot] --> B(app.py)
    A --> C(database.py)
    A --> D(faqs.json)
    A --> E(.env)
    A --> F(static)
    F --> G(index.html)

