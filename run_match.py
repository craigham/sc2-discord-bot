from collections import namedtuple
from pathlib import Path
import random
import json
import discord
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PLAYER1 = os.getenv('PLAYER1')
CHANNEL_ID = os.getenv('CHANNEL_ID')

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
        match_results = f'Match results: {get_results_json()[-1]}'
        print(match_results)
        # await self.get_channel(CHANNEL_ID).send(match_results)

    async def do_match(self, match:SC2Match):        
        matchString = f"1,{match.bot1},T,python,2,{match.bot2},T,{get_bot_exe_type(match.bot2)},{match.map}"
        with open("matches", "w") as f:
            f.write(f"{matchString}")
        command = f'docker-compose -f docker-compose-host-network.yml up'
        process = await asyncio.create_subprocess_shell(command, shell=True, executable='/bin/bash')
        await process.communicate()
        
    async def setup_hook(self):
        self.queue_task = self.loop.create_task(self.process_queue())        
        
        
# channel = await self.fetch_channel(CHANNEL_ID)
# await channel.send(f'Bot {self.bot_name} is ready to queue matches')

intents = discord.Intents.default()
intents.message_content = True
client = Sc2Runner(PLAYER1, intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!match'):
        _, match_params = message.content.split()
        if len(match_params.split()) == 2:
            opponent, the_map = match_params.split()
        else:
            opponent = match_params        
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
