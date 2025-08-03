from collections import namedtuple
from pathlib import Path
import random
import json
import discord
import asyncio
import os
from .log_monitor import LogMonitor

SC2Match = namedtuple('SC2Match', ['map', 'bot1', 'bot2', 'priority'])

class Sc2Runner(discord.Client):
    def __init__(self, bot_name: str, graylog_host: str | None = None, graylog_port: int = 12201, 
                 log_file_path: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot_name = bot_name
        self.match_queue = []
        self.queue_task = None
        self.current_match = None
        self.channel_id = None
        
        # Initialize log monitor if Graylog is configured
        if graylog_host and log_file_path:
            self.log_monitor = LogMonitor(log_file_path, graylog_host, graylog_port)
            self.log_monitor.start_monitoring()
        else:
            self.log_monitor = None

    def _get_next_match_id(self) -> int:
        """Get the next match ID by incrementing the last match's 'match' field from results.json."""
        try:
            with open('results.json', 'r') as f:
                results = json.load(f)
                last_match = results['results'][-1]
                return last_match.get('match', 0) + 1
        except (FileNotFoundError, json.JSONDecodeError, IndexError, KeyError):
            return 1

    def queue_match(self, opponent: str, map_name: str) -> None:
        """Queue a match against the specified opponent on the specified map."""
        self.match_queue.append(SC2Match(map_name, self.bot_name, opponent, 3))

    async def process_queue(self) -> None:
        """Process the match queue."""
        while True:
            if self.match_queue:
                match = self.match_queue.pop(0)
                self.current_match = match
                await self.do_match(match)
                print(f'Match ended: {match}')
                await self.report_result(match)
                self.current_match = None                
                
            await asyncio.sleep(3)  # Sleep to prevent tight loop

    async def report_result(self, match: SC2Match) -> None:
        """Report match results to Discord."""
        match_results = self._get_results_json()[-1]
        match_results['opponent'] = match.bot2
        match_results['map'] = match.map
        formatted_results = f"**Match Results:**\n```json\n{json.dumps(match_results, indent=4)}\n```"        
        if self.channel_id:
            channel = self.get_channel(self.channel_id)
            await channel.send(formatted_results)

    async def do_match(self, match: SC2Match) -> None:
        """Execute a match."""
        # Retrieve the current match ID from results.json
        current_match_id = self._get_next_match_id()
        if self.log_monitor:
            self.log_monitor.current_match_id = current_match_id
        # Send a status update to Discord
        if self.channel_id:
            channel = self.get_channel(self.channel_id)
            await channel.send(f"Match {current_match_id} started: {match.bot1} vs {match.bot2} on map {match.map}")
        
        matchString = f"1,{match.bot1},T,python,2,{match.bot2},T,{self._get_bot_exe_type(match.bot2)},{match.map}"
        with open("matches", "w") as f:
            f.write(f"{matchString}")
        command = f'docker-compose -f docker-compose-host-network.yml up'
        process = await asyncio.create_subprocess_shell(command, shell=True, executable='/bin/bash')
        await process.communicate()

    def _get_results_json(self) -> list:
        """Get results from results.json file."""
        with open('results.json', 'r') as results_file:
            return json.load(results_file)['results']
        
    def _get_bot_exe_type(self, bot_name: str) -> str:
        """Get the executable type for a bot."""
        ladderbots_type = {"BinaryCpp": "cpplinux", "Python": "python", "DotNetCore": "dotnetcore"}
        try:
            with open(f'bots/{bot_name}/ladderbots.json', 'r') as results_file:
                bot_info = json.load(results_file)
                bot_type = bot_info['Bots'][bot_name]['Type']
                return ladderbots_type[bot_type]
        except FileNotFoundError:
            return "python"

    async def setup_hook(self) -> None:
        """Set up the Discord bot hook."""
        self.queue_task = self.loop.create_task(self.process_queue())  

    async def find_channel_id(self, channel_name: str) -> None:
        """Find the Discord channel ID by name."""
        print('waiting for ready')
        await self.wait_until_ready()        
        for guild in self.guilds:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                self.channel_id = channel.id
                print(f'Channel id: {self.channel_id}')
                break      

    async def close(self) -> None:
        """Clean up resources when the client is closing."""
        if self.log_monitor:
            self.log_monitor.stop_monitoring()
        await super().close() 