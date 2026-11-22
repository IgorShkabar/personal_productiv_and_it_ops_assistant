# my chat bot: Theme: Personal `Productivity and IT Operations Assistant`.

import os
import json
import time
from google import genai
from google.genai import types
from google.genai import errors
import datetime

# DEFINE AUTOMATION TOOLS (Python Functions)

# The AI reads the docstrings & type hints to understand WHEN & HOW to use these functions automatically.

def check_server_health(server_name: str) -> str:
    """ Checks the CPU, memory, and online status of a specific server.
    Args:
        server_name (str): The name or ID of the server to check (e.g. 'prod-db-01',  'web-main')
    """

    # Simmulated live infrastructure check
    mock_servers = {
        "prod-db-01": {"status": "ONLINE", "cpu": "78%", "memory": "64%"},
        "web-main": {"status": "ONLINE", "cpu": "22%", "memory": "41%"},
        "backup_node": {"status": "WARNING", "cpu": "95%", "memory": "89%"} 
        
    }
    data = mock_servers.get(server_name.lower())

    if not data:
        return json.dumps({"error": f"Server '{server_name}' not found."})
    return json.dumps({"server": server_name, **data})

def create_automation_ticket(title: str, priority: str, description: str) -> str:
    """ Creates a new task or support ticket in the local tracking system.
    
    Args:
        title: Short summary of the issue or task.
        priority: Priority level ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL').
        description: Detailed explanation of what needs to be done.    
    """

    ticket_d = f"TICKET--{datetime.datetime.now().strftime('%H%M%S')}"
    ticket_record = {
        "id": ticket_d,
        "timestamp": datetime.datetime.now().isoformat(),
        "title": title,
        "priority": priority.upper(),
        "description": description,
        "status": "OPEN"
    }

    # Append ticket to a local JSON log file (Workflow Persistent)
     
    with open( "tickets_log.jsonl", "a", encoding="utf-8" ) as f:
        f.write(json.dumps(ticket_record) + "\n")

    return json.dumps({"result": "Success", "ticket_id": ticket_record})

def save_summary_report(filename: str, content: str) -> str:
    """Saves markdown report or  a formatted text to the local work-space.

    Args:
        filename: Name of the file ('daily_audit.md').
        content: The full text content to write into the file.    
    """
    # Clear filename to prevent directory traversal
    safe_name = os.path.basename(filename)

    with open(safe_name, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Report successfully saved to {os.path.abspath(safe_name)}"

client = genai.Client()

# Список моделей: основная и запасная на случай перегрузки (503)
MODELS = ["gemini-3.8-flash", "gemini-3.8-flash-lite"]

def generate_with_retry(contents, config=None, retries=3):
    for model_name in MODELS:
        for attempt in range(retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config
                )
                return response
            except errors.APIError as e:
                # Если сервер перегружен (503) или превышен лимит запросов (429)
                if e.code in (503, 429):
                    wait_time = 2 ** attempt  # Ждем 1, 2, 4 секунды
                    print(f"[Warn]: {model_name} overloaded ({e.code}). Repeating in {wait_time} sec...")
                    time.sleep(wait_time)
                else:
                    raise e
        print(f"[Warn]: Switching to reserved model...")
    raise RuntimeError("All models temporarily unavailable.")


# INITIALIZE the AI Agent & workflow configuration

def run_chatbot():
    # picks up GEMINI_API_KEY automatically from environment variables 
    client = genai.Client()

    # bundle all automation func-s into a toolset
    automation_tools = [
        check_server_health,
        create_automation_ticket,
        save_summary_report
    ] 

    # Sys. instructions define the bot`s persona, rules, & workflow logic
    system_instruction = (
        "You are an intelligent IT Operations and Productivity Automation Assistant."
        "You have access to tools that check server health, log support tickets, and save reports."
        "When a user asks you to perform a multi-step workflow (check servers, " 
        "log a ticket if CPU > 80%, and save a report), execute the tools sequentially and"
        "provide a clear summary of all actions taken."
    )
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=automation_tools,
        temperature=0.2, 
        # Low temperature keeps tool execution reliable, actual and factual 
    )

    # Start a stateful chat session (the SDK hndles automatic tool execution loops)
    chat = client.chats.create(
        model="gemini-3.8-flash",
        config=config
    )

    print(" AI Automation Bot Initialized (Type 'exit' to quit)")
    print("Try asking: 'Check prod-db-01 and backup-node. If any server has CPU over 80%, open a HIGH priority ticket and save a report'")

    # CONVERSIONAL LOOP 
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input: continue

            if user_input.lower() in ["exit", "quit"]:
                print("Shutting down automation bot. Bye!")
                break

            # send message to the model; the SDK automatically executes any
            # required Python tools & feeds the results back to the model.

            response = chat.send_message(user_input)
            print(f"\nBot: {response.text}\n")

        except Exception as e:
            print(f"\n[Error]: {e}\n")

if __name__ == "__main__":
    run_chatbot()
                