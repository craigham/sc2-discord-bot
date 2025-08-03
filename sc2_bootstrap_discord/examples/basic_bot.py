#!/usr/bin/env python3
"""
Basic example of using the SC2 Bootstrap Discord bot.
"""

import asyncio
import os
from dotenv import load_dotenv
import discord
from sc2_bootstrap_discord import Sc2Runner

# Load environment variables
load_dotenv()

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True

# Create the bot client
client = Sc2Runner(
    bot_name=os.getenv('PLAYER1', 'TBone'),
    graylog_host=os.getenv('GRAYLOG_HOST'),
    graylog_port=int(os.getenv('GRAYLOG_PORT', '12201')),
    log_file_path=os.getenv('LOG_FILE_PATH', 'logs/bot_controller1/TBone/stderr.log'),
    intents=intents
)

@client.event
async def on_ready():
    """Called when the bot is ready."""
    print(f'Logged in as {client.user}')
    channel_name = os.getenv('CHANNEL_NAME', 'match-runner')
    await client.find_channel_id(channel_name)
    print(f'Found channel: {channel_name}')

@client.event
async def on_message(message):
    """Handle incoming messages."""
    if message.author == client.user:
        return
    
    if message.content.startswith('!match'):
        # Parse match command: !match <opponent> [map]
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send('Usage: !match <opponent> [map]')
            return
        
        opponent = parts[1]
        the_map = parts[2] if len(parts) > 2 else "Acropolis"
        
        await message.channel.send(f'Queueing match against: {opponent} on map: {the_map}')
        client.queue_match(opponent, the_map + 'AIE')
    
    elif message.content.startswith('!help'):
        help_text = """
**SC2 Bootstrap Discord Bot Commands:**
- `!match <opponent> [map]` - Queue a match against the specified opponent (optional map)
- `!help` - Show this help message
        """
        await message.channel.send(help_text)
    
    elif message.content.startswith('!status'):
        if client.current_match:
            await message.channel.send(f'Current match: {client.current_match.bot1} vs {client.current_match.bot2} on {client.current_match.map}')
        else:
            queue_size = len(client.match_queue)
            await message.channel.send(f'No active match. Queue size: {queue_size}')

if __name__ == '__main__':
    # Run the bot
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable is required")
        exit(1)
    
    try:
        client.run(token)
    except Exception as e:
        print(f"Error running bot: {e}")
        exit(1) 