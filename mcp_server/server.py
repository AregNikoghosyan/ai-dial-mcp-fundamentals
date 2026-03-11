from pathlib import Path
from mcp.server.fastmcp import FastMCP
from models.user_info import UserSearchRequest, UserCreate, UserUpdate
from user_client import UserClient


mcp = FastMCP(
    name="users-management-mcp-server",
    host="0.0.0.0",
    port=8005,
)

user_client = UserClient()


# ==================== TOOLS ====================

@mcp.tool(description="Get user by id from user service")
async def get_user_by_id(user_id: str) -> str:
    user = await user_client.get_user(int(user_id))
    return str(user)


@mcp.tool(description="Delete user from the system")
async def delete_user(user_id: str) -> str:
    result = await user_client.delete_user(int(user_id))
    return str(result)


@mcp.tool(description="Search users by name, surname, email or gender")
async def search_user(request: UserSearchRequest) -> str:
    result = await user_client.search_users(
        name=request.name,
        surname=request.surname,
        email=request.email,
        gender=request.gender,
    )
    return str(result)


@mcp.tool(description="Add new user into the system")
async def add_user(user: UserCreate) -> str:
    result = await user_client.add_user(user)
    return str(result)


@mcp.tool(description="Update user information")
async def update_user(user_id: str, user: UserUpdate) -> str:
    result = await user_client.update_user(int(user_id), user)
    return str(result)


# ==================== MCP RESOURCES ====================

@mcp.resource(
    uri="users-management://flow-diagram",
    mime_type="image/png",
    description="Flow diagram of users management MCP server"
)
async def get_flow_diagram() -> bytes:
    file_path = Path(__file__).parent / "flow.png"
    return file_path.read_bytes()


# ==================== MCP PROMPTS ====================

@mcp.prompt(description="Helps users formulate effective search queries")
async def user_search_prompt() -> str:
    return """
You are helping users search through a dynamic user database.

Available fields:
- name
- surname
- email
- gender

Use partial matches where possible.
Combine filters when needed.
Search is case-insensitive.
"""


@mcp.prompt(description="Guides creation of realistic user profiles")
async def user_create_prompt() -> str:
    return """
You are helping create realistic user profiles.

Required fields:
- name
- surname
- email
- about_me

Optional fields:
- phone
- gender
- company
- salary
- address

Ensure email uniqueness and realistic data.
"""


if __name__ == "__main__":
    mcp.run(transport="streamable-http")