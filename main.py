import os
import asyncio
import logging
from dotenv import load_dotenv
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from news_agent import NewsAgent
from news_tracker import NewsTracker
from news_agent_executor import NewsAgentExecutor

load_dotenv()
port = int(os.environ.get("PORT", 3001))

logging.basicConfig(level=logging.INFO)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
if not MCP_SERVER_URL:
    raise RuntimeError("MCP_SERVER_URL environment variable not set. Please set it in your .env file.")

COUNTRIES = ["Japan", "Germany", "Brazil", "Switzerland", "India"]

async def main():
    agent = NewsAgent(MCP_SERVER_URL)
    tracker = NewsTracker(agent, COUNTRIES)
    await tracker.start()

    skill = AgentSkill(
        id='search_financial_news_for_countries',
        name='Search Financial News for Countries',
        description='Searches external sources for information using an MCP server. Useful for retrieving up-to-date financial and business news from around the world.(Currently supports a fixed list of countries)',
        tags=['search','finance', 'news'],
        examples=[
            'China',
            'Indonesia',
            'Malaysia',
            'Vietnam',
        ],
    )

    public_agent_card = AgentCard(
        name='News Agent',
        description='An agent that fetches news from an external MCP server for a specific list of countries.',
        url='https://externalagent1-server.onrender.com',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
        supports_authenticated_extended_card=False,
    )

    request_handler = DefaultRequestHandler(
        agent_executor=NewsAgentExecutor(tracker),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
    )

    import uvicorn
    config = uvicorn.Config(server.build(), host='0.0.0.0', port=port, loop="asyncio")
    server_instance = uvicorn.Server(config)
    await server_instance.serve()

if __name__ == '__main__':
    asyncio.run(main())
