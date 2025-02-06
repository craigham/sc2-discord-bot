
import subprocess
from pathlib import Path
from random import choice
import json
import discord

player1 = 'TBone'
MAPS_PATH = './maps'
LADDERBOTS_TYPE = {"BinaryCpp": "cpplinux", "Python":"python", "DotNetCore": "dotnetcore"}
MAP_FILE_EXT = 'SC2Map'
NUM_GAMES_TO_PLAY = 1
DISCORD_TOKEN = '<Token>'
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return    
    if message.content.startswith('!match'):
        _, opponent, the_map = message.content.split()
        await message.channel.send(f'Starting match against: {opponent} on map: {the_map}')
        await do_match(opponent, the_map + 'AIE')                
        await message.channel.send(f'{get_game_result()}')
    elif message.content.startswith('!bots'): 
        await message.channel.send(f'{get_bot_list()}')
    elif message.content.startswith('!maps'):        
        await message.channel.send(f'{get_map_list()}')
        
def get_game_result():
    with open('results.json' , 'r') as results_file:
        game_results = json.load(results_file)        
        return game_results['results'][-1]
        
def get_bot_list():
    return sorted((x.name for x in Path('./bots').iterdir() if not x.is_file()))
    
def get_map_list():    
    return sorted(file.name.rstrip('AIE.SC2Map') for file in Path('./maps').iterdir() 
                                    if file.is_file() 
                                    and file.name.split('.')[-1] == 'SC2Map'
                                    and not file.name.startswith('.')
            )

async def do_match(opponent, map_name):    
    matchString: str = f"1,{player1},T,python,2,{opponent},T,{get_bot_exe_type(opponent)},{map_name}"
    with open("matches", "w") as f:
        f.write(f"{matchString}")

    command = f'docker-compose -f docker-compose-host-network.yml up'
    subprocess.run(command, shell=True, executable='/bin/bash')
        
def get_bot_exe_type(bot_name):
    try:
        with open(f'bots/{bot_name}/ladderbots.json' , 'r') as results_file:
            bot_info = json.load(results_file)
            bot_type = bot_info['Bots'][bot_name]['Type']
            return LADDERBOTS_TYPE[bot_type]
    except FileNotFoundError:
        return "python"

client.run(DISCORD_TOKEN)


