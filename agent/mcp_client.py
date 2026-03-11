from typing import Optional, Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import (
    CallToolResult,
    TextContent,
    GetPromptResult,
    ReadResourceResult,
    Resource,
    TextResourceContents,
    BlobResourceContents,
    Prompt,
)
from pydantic import AnyUrl


class MCPClient:
    """Handles MCP server connection and tool execution"""

    def __init__(self, mcp_server_url: str) -> None:
        self.mcp_server_url = mcp_server_url
        self.session: Optional[ClientSession] = None
        self._streams_context = None
        self._session_context = None

    async def __aenter__(self):

        # 1
        self._streams_context = streamablehttp_client(self.mcp_server_url)

        # 2
        read_stream, write_stream, _ = await self._streams_context.__aenter__()

        # 3
        self._session_context = ClientSession(read_stream, write_stream)

        # 4
        self.session = await self._session_context.__aenter__()

        # 5
        result = await self.session.initialize()
        print("\nMCP Server Capabilities:")
        print(result)

        # 6
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):

        if self.session and self._session_context:
            await self._session_context.__aexit__(exc_type, exc_val, exc_tb)

        if self._streams_context:
            await self._streams_context.__aexit__(exc_type, exc_val, exc_tb)

    async def get_tools(self) -> list[dict[str, Any]]:
        """Get available tools from MCP server"""

        if not self.session:
            raise RuntimeError("MCP client not connected.")

        tools = await self.session.list_tools()

        result = []

        for tool in tools.tools:
            result.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
            )

        return result

    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> Any:

        if not self.session:
            raise RuntimeError("MCP client not connected.")

        tool_result: CallToolResult = await self.session.call_tool(tool_name, tool_args)

        content = tool_result.content[0]

        print(f"    ⚙️: {content}\n")

        if isinstance(content, TextContent):
            return content.text
        else:
            return content

    async def get_resources(self) -> list[Resource]:

        if not self.session:
            raise RuntimeError("MCP client not connected.")

        try:
            resources = await self.session.list_resources()
            return resources.resources
        except Exception as e:
            print("No MCP resources available:", e)
            return []

    async def get_resource(self, uri: AnyUrl) -> str:

        if not self.session:
            raise RuntimeError("MCP client not connected.")

        result: ReadResourceResult = await self.session.read_resource(uri)

        content = result.contents[0]

        if isinstance(content, TextResourceContents):
            return content.text

        if isinstance(content, BlobResourceContents):
            return content.blob

    async def get_prompts(self) -> list[Prompt]:

        if not self.session:
            raise RuntimeError("MCP client not connected.")

        try:
            prompts = await self.session.list_prompts()
            return prompts.prompts
        except Exception as e:
            print("No MCP prompts available:", e)
            return []

    async def get_prompt(self, name: str) -> str:

        if not self.session:
            raise RuntimeError("MCP client not connected.")

        result: GetPromptResult = await self.session.get_prompt(name)

        combined_content = ""

        for message in result.messages:

            if hasattr(message, "content"):

                if isinstance(message.content, TextContent):
                    combined_content += message.content.text + "\n"

                elif isinstance(message.content, str):
                    combined_content += message.content + "\n"

        return combined_content