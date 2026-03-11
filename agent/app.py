import asyncio
import os

from agent.mcp_client import MCPClient
from agent.dial_client import DialClient
from agent.models.message import Message, Role
from agent.prompts import SYSTEM_PROMPT


# Read API key from environment variable
API_KEY = os.getenv("DIAL_API_KEY")
ENDPOINT = "https://ai-proxy.lab.epam.com"


async def main():

    if not API_KEY:
        raise ValueError("DIAL_API_KEY environment variable is not set")

    # Connect to MCP server
    async with MCPClient(mcp_server_url="http://localhost:8005/mcp") as mcp_client:

        # Get MCP resources
        resources = await mcp_client.get_resources()

        print("\nAvailable MCP Resources:")
        for r in resources:
            print(r)

        # Get MCP tools
        tools = await mcp_client.get_tools()

        print("\nAvailable MCP Tools:")
        for t in tools:
            print(t)

        # Create Dial client
        dial_client = DialClient(
            api_key=API_KEY,
            endpoint=ENDPOINT,
            tools=tools,
            mcp_client=mcp_client
        )

        # Message history
        messages = [
            Message(
                role=Role.SYSTEM,
                content=SYSTEM_PROMPT
            )
        ]

        # Load MCP prompts
        prompts = await mcp_client.get_prompts()

        for p in prompts:
            prompt_text = await mcp_client.get_prompt(p.name)

            messages.append(
                Message(
                    role=Role.USER,
                    content=prompt_text
                )
            )

        print("\nChat started (type 'exit' to quit)\n")

        while True:

            user_input = input("You: ")

            if user_input.lower() == "exit":
                break

            messages.append(
                Message(
                    role=Role.USER,
                    content=user_input
                )
            )

            response = await dial_client.get_completion(messages)

            print("\nAssistant:", response.content)

            messages.append(response)


if __name__ == "__main__":
    asyncio.run(main())