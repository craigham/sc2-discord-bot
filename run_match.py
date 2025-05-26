from collections import namedtuple
from pathlib import Path
import random
import json
import discord
import asyncio
from dotenv import load_dotenv
import os
from log_monitor import LogMonitor

# Load environment variables from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PLAYER1 = os.getenv('PLAYER1')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
GRAYLOG_HOST = os.getenv('GRAYLOG_HOST', None)
GRAYLOG_PORT = int(os.getenv('GRAYLOG_PORT', '12201'))
MAPS_PATH = './maps'
LADDERBOTS_TYPE = {"BinaryCpp": "cpplinux", "Python": "python", "DotNetCore": "dotnetcore"}
MAP_FILE_EXT = 'SC2Map'

BOTS = sorted((x.name for x in Path('./bots').iterdir() if not x.is_file()))
MAPS = sorted(file.name.rstrip('AIE.SC2Map') for file in Path('./maps').iterdir()
                  if file.is_file()
                  and file.name.split('.')[-1] == 'SC2Map'
                  and not file.name.startswith('.'))

SC2Match = namedtuple('SC2Match', ['map', 'bot1', 'bot2', 'priority'])

def get_results_json():
    with open('results.json', 'r') as results_file:
        return json.load(results_file)['results']
        
def get_bot_exe_type(bot_name):
    try:
        with open(f'bots/{bot_name}/ladderbots.json', 'r') as results_file:
            bot_info = json.load(results_file)
            bot_type = bot_info['Bots'][bot_name]['Type']
            return LADDERBOTS_TYPE[bot_type]
    except FileNotFoundError:
        return "python"

class Sc2Runner(discord.Client):
    def __init__(self, bot_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot_name = bot_name
        self.match_queue = []
        self.queue_task = None
        self.current_match = None
        self.channel_id = None
        
        # Initialize log monitor
        if GRAYLOG_HOST:
            print(f"GRAYLOG_HOST is set to: {GRAYLOG_HOST}")
            log_path = os.path.join('logs', 'bot_controller1', 'TBone', 'stderr.log')
            print(f'Initializing log monitor with path: {log_path} and host: {GRAYLOG_HOST} and port: {GRAYLOG_PORT}')
            self.log_monitor = LogMonitor(log_path, GRAYLOG_HOST, GRAYLOG_PORT)
            print("LogMonitor instance created, starting monitoring...")
            self.log_monitor.start_monitoring()
            print("LogMonitor start_monitoring called")
        else:
            print("GRAYLOG_HOST not set, skipping log monitor initialization")

    def queue_match(self, opponent, map_name):
        self.match_queue.append(SC2Match(map_name, self.bot_name, opponent, 3))

    async def process_queue(self):
        while True:
            if self.match_queue:
                match = self.match_queue.pop(0)
                self.current_match = match
                await self.do_match(match)
                print(f'Match ended: {match}')
                await self.report_result(match)
                self.current_match = None                
                
            await asyncio.sleep(3)  # Sleep to prevent tight loop

    async def report_result(self, match:SC2Match):
        match_results = get_results_json()[-1]
        match_results['opponent'] = match.bot2
        match_results['map'] = match.map
        formatted_results = f"**Match Results:**\n```json\n{json.dumps(match_results, indent=4)}\n```"        
        if self.channel_id:
            channel = self.get_channel(self.channel_id)
            await channel.send(formatted_results)

    async def do_match(self, match:SC2Match):        
        # Update match ID before starting the match
        self.log_monitor.update_match_id()
        
        matchString = f"1,{match.bot1},T,python,2,{match.bot2},T,{get_bot_exe_type(match.bot2)},{match.map}"
        with open("matches", "w") as f:
            f.write(f"{matchString}")
        command = f'docker-compose -f docker-compose-host-network.yml up'
        process = await asyncio.create_subprocess_shell(command, shell=True, executable='/bin/bash')
        await process.communicate()

    async def setup_hook(self):
        self.queue_task = self.loop.create_task(self.process_queue())  
        

    async def find_channel_id(self):
        print('waiting for ready')
        await self.wait_until_ready()        
        for guild in self.guilds:
            channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
            if channel:
                self.channel_id = channel.id
                print(f'Channel id: {self.channel_id}')
                break      
        
        
# channel = await self.fetch_channel(CHANNEL_ID)
# await channel.send(f'Bot {self.bot_name} is ready to queue matches')

    async def close(self):
        """Clean up resources when the client is closing."""
        self.log_monitor.stop_monitoring()
        await super().close()

intents = discord.Intents.default()
intents.message_content = True
client = Sc2Runner(PLAYER1, intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.find_channel_id()

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
            the_map = random.choice(MAPS)
        await message.channel.send(f'Queueing match against: {opponent} on map: {the_map}')
        client.queue_match(opponent, the_map + 'AIE')
    elif message.content.startswith('!bots'):
        await message.channel.send(f'{BOTS}')
    elif message.content.startswith('!maps'):
        await message.channel.send(f'{MAPS}')
    elif message.content.startswith('!queue'):
        await message.channel.send(f'Current: {client.current_match} - Queue: {client.match_queue}')
    elif message.content.startswith('!last_match'):
        await message.channel.send(f'{get_results_json()[-1]}')

client.run(DISCORD_TOKEN)
