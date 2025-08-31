import json
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
import logging

logger = logging.getLogger("NewsAgent")

class NewsAgentExecutor(AgentExecutor):
    def __init__(self, tracker):
        self.tracker = tracker
        logger.info("NewsAgentExecutor initialized with tracker.")

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        logger.info("AgentExecutor.execute called.")
        country = None
        if context.message and context.message.parts:
            for part in context.message.parts:
                text = None
                if hasattr(part, "text") and part.text:
                    text = part.text
                elif hasattr(part, "root") and hasattr(part.root, "text") and part.root.text:
                    text = part.root.text
                if text:
                    country = text.strip()
                    break
        if not country:
            result = "No country provided."
        else:
            news_list = await self.tracker.get_and_clear_news(country)
            if news_list:
                result = json.dumps({country: news_list}, indent=2)
            else:
                result = f"No news available for {country}."
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        logger.warning("Cancellation not supported.")
        raise Exception('cancel not supported')
