import asyncio
from typing import Dict, List
import logging

logger = logging.getLogger("NewsTracker")

from news_agent import NewsAgent


class NewsTracker:
    def __init__(self, agent: NewsAgent, countries: List[str]):
        self.agent = agent
        self.countries = countries
        self.news: Dict[str, List[str]] = {country: [] for country in countries}
        self.missed_cycles: Dict[str, int] = {country: 0 for country in countries}
        self._lock = asyncio.Lock()
        self._task = None

    async def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def _run(self):
        while True:
            await self.update_all_news()
            await asyncio.sleep(30)

    async def update_all_news(self):
        for country in self.countries:
            async with self._lock:
                news_count = len(self.news[country])
            if news_count >= 3:
                logger.info(f"Skipping fetch for {country}: already have 3 news items.")
                continue
            query = f"Latest financial news about {country} that will affect tarriffs and trade policies with {country}"
            try:
                news = await self.agent.fetch_news(query)
                logger.info(f"Fetched news for {country}: {news}")
            except Exception as e:
                news = f"Error fetching news: {e}"
                logger.error(f"Error fetching news for {country}: {e}")
            async with self._lock:
                if news and news not in self.news[country]:
                    self.news[country].append(news)
                    logger.info(f"Stored news for {country}: {self.news[country]}")
            logger.info(f"Updated news for {country}")
        # Log the full tracking list after all updates
        logger.info(f"Current tracking list: {self.news}")

    async def get_and_clear_news(self, country: str) -> List[str]:
        async with self._lock:
            news_list = self.news.get(country, [])
            self.news[country] = []
            self.missed_cycles[country] = 0  # Reset missed cycles on access
            return news_list

    async def get_and_clear_all_news(self) -> Dict[str, List[str]]:
        async with self._lock:
            all_news = {country: news[:] for country, news in self.news.items()}
            for country in self.countries:
                self.news[country] = []
                self.missed_cycles[country] = 0
            return all_news
