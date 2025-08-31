import aiohttp
import logging
import json

logger = logging.getLogger("NewsAgent")

class NewsAgent:
    """News Agent that fetches news from an MCP server via JSON-RPC."""

    def __init__(self, mcp_url: str):
        self.mcp_url = mcp_url
        logger.info(f"NewsAgent initialized with MCP URL: {self.mcp_url}")

    async def fetch_news(self, query: str) -> str:
        logger.info(f"Fetching news for query: {query}")
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "search_perplexity",
                "arguments": {
                    "messages": [
                        {"role": "user", "content": f"{query}, remove citations and dont use markdown"}
                    ],
                    "output_format": "json"
                }
            }
        }
        logger.debug(f"Payload for MCP request: {payload}")
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                logger.info(f"Sending POST to MCP server: {self.mcp_url}")
                headers = {"Content-Type": "application/json"}
                async with session.post(self.mcp_url, json=payload, headers=headers) as resp:
                    logger.info(f"MCP server responded with status: {resp.status}")
                    if resp.status != 200:
                        logger.error(f"Failed to fetch news: {resp.status}")
                        return f"Failed to fetch news: {resp.status}"
                    data = await resp.json()
                    logger.debug(f"Response JSON from MCP: {data}")
                    if "error" in data:
                        logger.error(f"Error from MCP: {data['error']}")
                        return f"Error from MCP: {data['error']}"
                    logger.info("Successfully fetched news from MCP.")
                    # Updated extraction for new MCP response format
                    result = data.get("result", None)
                    if result is None:
                        return "No news found."
                    if isinstance(result, dict) and 'content' in result:
                        content_list = result['content']
                        if isinstance(content_list, list) and len(content_list) > 0:
                            text = content_list[0].get('text', None)
                            if text:
                                return text
                    if isinstance(result, str):
                        return result
                    return json.dumps(result, indent=2)
        except Exception as e:
            logger.exception(f"Exception while fetching news: {e}")
            return f"Exception while fetching news: {e}"
