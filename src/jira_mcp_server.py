from mcp.server.fastmcp import FastMCP
from src.jira_client import JiraClient
import json

# Create an MCP server
mcp = FastMCP("Jira Evaluator Server")

# Initialize Jira client
jira = JiraClient()

@mcp.tool()
def get_ticket(ticket_id: str) -> str:
    """
    Fetches a Jira ticket by ID and returns title, description, type, and acceptance criteria.
    """
    ticket = jira.get_ticket(ticket_id)
    return ticket.model_dump_json(indent=2)

@mcp.tool()
def get_acceptance_criteria(ticket_id: str) -> str:
    """
    Returns only the acceptance criteria for a given Jira ticket.
    """
    ticket = jira.get_ticket(ticket_id)
    return json.dumps(ticket.acceptance_criteria, indent=2)

@mcp.tool()
def get_ticket_type(ticket_id: str) -> str:
    """
    Returns the type of the Jira ticket (e.g., Story, Bug, Task).
    """
    ticket = jira.get_ticket(ticket_id)
    return ticket.ticket_type

if __name__ == "__main__":
    mcp.run(transport="stdio")
