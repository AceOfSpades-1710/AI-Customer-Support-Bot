from flask import Flask, request, jsonify, send_from_directory
import json
import os
from dotenv import load_dotenv
from groq import Groq
from database import init_db, get_history, save_history
from database import get_connection
import psycopg2

load_dotenv()
app = Flask(__name__)

# Initialize Groq client
client = Groq(
    api_key=os.getenv('OPENAI_API_KEY')
)

# Load FAQs with fallback
try:
    with open('faqs.json', 'r') as f:
        faqs = json.load(f)['faqs']
except FileNotFoundError:
    faqs = []
    print("Warning: faqs.json not found, using empty FAQs.")

# Prompt template with enhanced contextual memory
PROMPT_TEMPLATE = """
You are a customer support bot. Use the following FAQs to answer questions:
{faqs}

Full conversation history:
{history}

User query: {query}

Respond based on the entire conversation history provided. If the query relates to previous messages, reference that context accurately. 
If the query matches an FAQ, respond with the answer. 
If not, or if it's complex, suggest escalating to a human agent.
Keep responses friendly, concise, and context-aware.
Suggest next actions if needed.
"""

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get('session_id', 'default')
    query = data.get('query')

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Retrieve full history
    history = get_history(session_id)
    if not history:
        history = "No previous conversation."

    # Format FAQs for prompt
    faqs_str = "\n".join([f"Q: {faq['question']}\nA: {faq['answer']}" for faq in faqs]) if faqs else "No FAQs available."
    prompt = PROMPT_TEMPLATE.format(faqs=faqs_str, history=history, query=query)

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        bot_response = response.choices[0].message.content
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({'error': f'API Error: {str(e)}'}), 500

    # Append new exchange to history
    new_history = history + f"\nUser: {query}\nBot: {bot_response}"
    save_history(session_id, new_history)

    if "escalate" in bot_response.lower() or "human" in bot_response.lower():
        bot_response += "\nEscalating to human support..."

    return jsonify({'response': bot_response})

@app.route('/sessions', methods=['GET'])
def get_sessions():
    try:
        conn = get_connection()  # Use new function
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        with conn.cursor() as cursor:
            cursor.execute('SELECT session_id, history FROM sessions')
            sessions = cursor.fetchall()
        conn.close()
        
        session_list = []
        for row in sessions:
            sid, hist = row
            lines = hist.strip().split('\n') if hist else []
            preview = "New Session"
            for line in lines:
                if line.startswith("User:"):
                    preview = line[6:].strip()[:50] + "..."
                    break
            session_list.append({'id': sid, 'preview': preview})
        
        return jsonify({'sessions': session_list})
    except psycopg2.Error as e:
        print(f"DB Error: {e}")
        return jsonify({'error': 'Database error'}), 500

@app.route('/session/<session_id>', methods=['GET'])
def get_session_history(session_id):
    try:
        history = get_history(session_id)
        lines = history.split('\n') if history else []
        formatted_history = []
        for line in lines:
            if line.startswith("User:"):
                formatted_history.append({'role': 'user', 'content': line[6:].strip()})
            elif line.startswith("Bot:"):
                formatted_history.append({'role': 'assistant', 'content': line[5:].strip()})
        
        return jsonify({'history': formatted_history})
    except Exception as e:
        print(f"History Error: {e}")
        return jsonify({'error': 'Error loading history'}), 500

@app.route('/sessions/new', methods=['POST'])
def create_new_session():
    try:
        session_id = request.json.get('session_id')
        save_history(session_id, "")  # Save empty history
        return jsonify({'session_id': session_id})
    except Exception as e:
        print(f"New Session Error: {e}")
        return jsonify({'error': 'Failed to create session'}), 500

@app.route('/')
def index():
    try:
        return send_from_directory('static', 'index.html')
    except Exception as e:
        print(f"Static File Error: {e}")
        return "<h1>Error: Could not load page. Check static/index.html</h1>", 500

if __name__ == '__main__':
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
    app.run(debug=True)