#!/usr/bin/env python3
"""
Command-line interface for SC2 Bootstrap Discord bot.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import discord
from .sc2_runner import Sc2Runner


def main():
    """Main CLI entry point."""
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = ['DISCORD_TOKEN', 'PLAYER1']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the required variables.")
        sys.exit(1)
    
    # Set up Discord intents
    intents = discord.Intents.default()
    intents.message_content = True
    
    # Create the bot client
    client = Sc2Runner(
        bot_name=os.getenv('PLAYER1'),
        graylog_host=os.getenv('GRAYLOG_HOST'),
        graylog_port=int(os.getenv('GRAYLOG_PORT', '12201')),
        log_file_path=os.getenv('LOG_FILE_PATH', 'logs/bot_controller1/TBone/stderr.log'),
        intents=intents
    )
    
    @client.event
    async def on_ready():
        print(f'Logged in as {client.user}')
        channel_name = os.getenv('CHANNEL_NAME', 'match-runner')
        await client.find_channel_id(channel_name)
    
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        
        if message.content.startswith('!match'):
            _, *match_params = message.content.split()
            if len(match_params) == 2:
                opponent, the_map = match_params
            else:
                opponent = match_params[0]
                the_map = "Acropolis"  # Default map
            await message.channel.send(f'Queueing match against: {opponent} on map: {the_map}')
            client.queue_match(opponent, the_map + 'AIE')
        elif message.content.startswith('!help'):
            help_text = """
**SC2 Bootstrap Discord Bot Commands:**
- `!match <opponent> [map]` - Queue a match against the specified opponent (optional map)
- `!help` - Show this help message
            """
            await message.channel.send(help_text)
    
    # Run the bot
    try:
        client.run(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        print(f"Error running bot: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 