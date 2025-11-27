	import os
import logging
import random
import asyncio
import datetime
import requests
from telegram import Bot
from telegram.error import TelegramError
import discord
from discord.ext import tasks, commands

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

QUOTE_API_URL = 'https://type.fit/api/quotes'

def fetch_random_quote() -> str:
    """Retrieve a random motivational quote from a public API."""
    try:
        response = requests.get(QUOTE_API_URL, timeout=10)
        response.raise_for_status()
        quotes = response.json()
        quote_obj = random.choice(quotes)
        text = quote_obj.get('text', '').strip()
        author = quote_obj.get('author', 'Unknown')
        return f"\"{text}\" - {author}"
    except Exception as e:
        logger.error(f'Failed to fetch quote: {e}')
        return "Stay positive and keep moving forward!"

async def send_telegram_message(token: str, chat_id: str, message: str):
    """Send a message via Telegram Bot API."""
    bot = Bot(token=token)
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info('Telegram message sent')
    except TelegramError as e:
        logger.error(f'Telegram send error: {e}')

class DiscordQuoteBot(commands.Cog):
    def __init__(self, bot: commands.Bot, channel_id: int):
        self.bot = bot
        self.channel_id = channel_id
        self.daily_quote.start()

    def cog_unload(self):
        self.daily_quote.cancel()

    @tasks.loop(hours=24)
    async def daily_quote(self):
        """Task that runs once every 24 hours to post a quote."""
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.channel_id)
        if channel is None:
            logger.error('Discord channel not found')
            return
        quote = fetch_random_quote()
        try:
            await channel.send(quote)
            logger.info('Discord quote sent')
        except Exception as e:
            logger.error(f'Discord send error: {e}')

    @daily_quote.before_loop
    async def before_daily_quote(self):
        """Wait until the next full hour before starting the loop to align daily schedule."""
        now = datetime.datetime.utcnow()
        next_hour = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        wait_seconds = (next_hour - now).total_seconds()
        logger.info(f'Waiting {wait_seconds:.0f} seconds to start Discord daily task')
        await asyncio.sleep(wait_seconds)

async def main():
    # Load configuration from environment variables
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    discord_token = os.getenv('DISCORD_TOKEN')
    discord_channel_id = os.getenv('DISCORD_CHANNEL_ID')

    if not all([telegram_token, telegram_chat_id, discord_token, discord_channel_id]):
        logger.error('Missing one or more required environment variables: TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, DISCORD_TOKEN, DISCORD_CHANNEL_ID')
        return

    # Prepare Discord bot
    intents = discord.Intents.default()
    discord_bot = commands.Bot(command_prefix='!', intents=intents)
    discord_bot.add_cog(DiscordQuoteBot(discord_bot, int(discord_channel_id)))

    # Schedule Telegram daily message using asyncio task
    async def telegram_daily_task():
        while True:
            now = datetime.datetime.utcnow()
            # Compute seconds until next 09:00 UTC (adjust as needed)
            target = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now >= target:
                target += datetime.timedelta(days=1)
            wait_seconds = (target - now).total_seconds()
            logger.info(f'Waiting {wait_seconds:.0f} seconds for next Telegram quote')
            await asyncio.sleep(wait_seconds)
            quote = fetch_random_quote()
            await send_telegram_message(telegram_token, telegram_chat_id, quote)

    # Run both bots concurrently
    await asyncio.gather(
        discord_bot.start(discord_token),
        telegram_daily_task()
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Shutdown requested by user')
