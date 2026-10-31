import json

def load_tickets(path):
    tickets = []
    with open(path,encoding="utf-8") as f:
        tickets = json.load(f)
    return tickets

def save_tickets(tickets,path):
    with open(path, 'w',encoding="utf-8") as f:
        json.dump(tickets, f)

