tickets = [
    {"id": 1, "text": "投影仪无法启动", "status": "open"},
    {"id": 2, "text": "教室门打不开", "status": "closed"},
    {"id": 3, "text": "音响没有声音", "status": "open"},
]
def filter_tickets(tickets, status):
	result = []
	for ticket in tickets:
		if ticket["status"] == status:
			result.append(ticket)
	return result
print(filter_tickets(tickets, "closed"))