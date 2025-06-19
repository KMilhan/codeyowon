from __future__ import annotations

import asyncio

from mcp.server.lowlevel.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import ServerCapabilities, Tool, TextContent

from .agent import ChatSession

server = Server("yowon")
session = ChatSession()


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="openai_chat",
            description="Generate a response with OpenAI",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "user prompt"}
                },
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict | None):
    if name == "openai_chat":
        prompt = (arguments or {}).get("prompt", "")
        answer = session.ask(prompt)
        return [TextContent(text=str(answer))]
    raise ValueError(f"unknown tool: {name}")


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(
            read,
            write,
            InitializationOptions(
                server_name="yowon",
                server_version="0.1",
                capabilities=ServerCapabilities(),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
