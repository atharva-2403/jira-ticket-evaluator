from mcp.server.fastmcp import FastMCP
from src.jira_client import fetch_ticket
import json

# Initialize FastMCP server
mcp = FastMCP("Jira Evaluator")

@mcp.tool()
def get_ticket(ticket_id: str) -> str:
    """
    Fetches a Jira ticket by ID and returns title, description, and acceptance criteria.
    """
    try:
        data = fetch_ticket(ticket_id)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error fetching ticket {ticket_id}: {str(e)}"

@mcp.tool()
def get_acceptance_criteria(ticket_id: str) -> str:
    """
    Returns only the acceptance criteria list for a given Jira ticket.
    """
    try:
        data = fetch_ticket(ticket_id)
        return json.dumps(data.get("acceptance_criteria", []), indent=2)
    except Exception as e:
        return f"Error fetching AC for {ticket_id}: {str(e)}"

@mcp.tool()
def get_ticket_type(ticket_id: str) -> str:
    """
    Returns the type of the Jira ticket (e.g., Story, Bug, Task).
    """
    try:
        data = fetch_ticket(ticket_id)
        return data.get("ticket_type", "Unknown")
    except Exception as e:
        return f"Error fetching ticket type for {ticket_id}: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
