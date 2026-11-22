# to pass all tools to the separate file to avoid confusing all functions in main.py

import os
import json
import subprocess
from datetime import datetime
import psutil

def check_server_health(server_name: str) -> str:
    """Checks the CPU, memory, and online status of a specific server.
    Args:
        server_name (str): The name or ID of the server to check (e.g. 'localhost', 'prod-db-01')
    """
    name = server_name.lower().strip()

    # 1. Реальная проверка моего ноутбука на Debian
    if name in ["localhost", "debian", "local", "igor-vostro5490"]:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        return json.dumps({
            "server": server_name,
            "status": "ONLINE (Real Debian)",
            "cpu": f"{cpu}%",
            "memory": f"{memory}%"
        })

    # 2. Тестовые серверы
    mock_servers = {
        "prod-db-01": {"status": "ONLINE", "cpu": "78%", "memory": "64%"},
        "web-main": {"status": "ONLINE", "cpu": "22%", "memory": "41%"},
        "backup-node": {"status": "WARNING", "cpu": "95%", "memory": "89%"},
        "backup_node": {"status": "WARNING", "cpu": "95%", "memory": "89%"}
    }
    
    data = mock_servers.get(name)
    if not data:
        return json.dumps({"error": f"Server '{server_name}' not found."})
    
    return json.dumps({"server": server_name, **data})


def create_ticket(server_name: str, priority: str, issue_description: str) -> str:
    """Opens a support ticket, logs it locally, and shows a desktop notification on Debian.
    Args:
        server_name (str): Name of the affected server.
        priority (str): Ticket priority (e.g., 'LOW', 'MEDIUM', 'HIGH').
        issue_description (str): Detailed description of the problem.
    """
    ticket_id = f"INC-{datetime.now().strftime('%H%M%S')}"
    ticket_data = {
        "ticket_id": ticket_id,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "server": server_name,
        "priority": priority.upper(),
        "issue": issue_description
    }

    # 1. Сохраняем тикет в файл tickets.log в папке проекта
    with open("tickets.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(ticket_data, ensure_ascii=False) + "\n")

    # 2. Показываем всплывающее уведомление на рабочем столе Debian
    urgency = "critical" if priority.upper() == "HIGH" else "normal"
    try:
        subprocess.run([
            "notify-send",
            "-u", urgency,
            f"Ticket {ticket_id} [{priority.upper()}]",
            f"Server: {server_name}\n{issue_description}"
        ], check=False)
    except FileNotFoundError:
        pass  # If the notify-send utility is not installed, the ticket will still be saved to the file

    return json.dumps({
        "status": "CREATED",
        "ticket_id": ticket_id,
        "message": f"Ticket {ticket_id} logged to tickets.log and desktop alert sent."
    })
