import asyncio
import json
import os
import logging
import re
from pathlib import Path
from typing import TypeVar, TypedDict, Optional
import graypy
from datetime import datetime

T = TypeVar('T')

class DebugLine(TypedDict):
    game_time: str
    game_step: int
    step_length: str
    minerals: str
    gas: str
    supply_used: int
    supply_capacity: int
    source_file: str
    line_number: int
    message: str

class LogMonitor:
    def __init__(self, log_file_path: str, graylog_host: str, graylog_port: int):
        self.log_file_path = log_file_path
        # Set up proper logging with graypy
        self.logger = logging.getLogger('starcraft_bot_controller')
        self.logger.setLevel(logging.INFO)
        # Add a default stdout handler
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(stdout_handler)
        # Add graypy handler
        handler = graypy.GELFUDPHandler(graylog_host, graylog_port)
        self.logger.addHandler(handler)
        self.current_match_id: int | None = None
        self.monitor_task: asyncio.Task[None] | None = None
        self.process: asyncio.subprocess.Process | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self.logger.info("LogMonitor.__init__ completed")

    def _parse_debug_line(self, line: str) -> Optional[DebugLine]:
        """Parse a debug line into structured data."""
        # Improved regex: allow for any whitespace (spaces/tabs) between columns
        pattern = (
            r'(\d{2}:\d{2})\s+'         # game_time
            r'(\d+)\s+'                 # game_step
            r'(\d+ms)\s+'               # step_length
            r'(\d+M)\s+'                # minerals
            r'(\d+G)\s+'                # gas
            r'(\d+)\s*/\s*(\d+)U\s+' # supply used/capacity (allow spaces around /)
            r'([^\s:]+(?:\.[^\s:]+)*):' # source_file (allow dots, no spaces or colons)
            r'(\d+)\s+'                 # line_number
            r'(.*)'                       # message
        )
        match = re.match(pattern, line.strip())
        if not match:
            return None
        return {
            'game_time': match.group(1),
            'game_step': int(match.group(2)),
            'step_length': match.group(3),
            'minerals': match.group(4),
            'gas': match.group(5),
            'supply_used': int(match.group(6)),
            'supply_capacity': int(match.group(7)),
            'source_file': match.group(8),
            'line_number': int(match.group(9)),
            'message': match.group(10)
        }

    def _get_next_match_id(self) -> int:
        """Get the next match ID by incrementing the last match's 'match' field from results.json."""
        try:
            with open('results.json', 'r') as f:
                results = json.load(f)
                last_match = results['results'][-1]
                return last_match.get('match', 0) + 1
        except (FileNotFoundError, json.JSONDecodeError, IndexError, KeyError):
            return 1

    async def _monitor_log_file(self) -> None:
        """Monitor the log file and forward entries to Graylog using tail -f."""
        self.logger.info(f"Starting log monitoring for file: {self.log_file_path}")
        while True:
            try:
                self.logger.info(f"Attempting to start tail -f process for {self.log_file_path}")
                # Start tail -f process
                self.process = await asyncio.create_subprocess_exec(
                    'tail', '-f', self.log_file_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                self.logger.info("tail -f process started successfully")

                # Read output line by line
                while True:
                    if self.process.stdout is None:
                        self.logger.warning("Process stdout is None, breaking")
                        break
                    line = await self.process.stdout.readline()
                    if not line:
                        self.logger.warning("No more lines to read, breaking")
                        break
                    
                    line_str = line.decode().strip()
                    if not line_str:
                        continue

                    self.logger.debug(f"Read line: {line_str[:100]}...")  # Print first 100 chars of line

                    # Parse the debug line
                    debug_data = self._parse_debug_line(line_str)
                    self.logger.debug(f"Debug data: {debug_data}")
                    # Log to Graylog with extra fields
                    extra = {
                        'match_id': self.current_match_id,
                        'source': 'starcraft_bot_controller',
                        'host': os.uname().nodename
                    }
                    
                    # Add parsed debug data if available
                    if debug_data:
                        extra.update({
                            'game_time': debug_data['game_time'],
                            'game_step': debug_data['game_step'],
                            'step_length': debug_data['step_length'],
                            'minerals': debug_data['minerals'],
                            'gas': debug_data['gas'],
                            'supply_used': debug_data['supply_used'],
                            'supply_capacity': debug_data['supply_capacity'],
                            'source_file': debug_data['source_file'],
                            'line_number': debug_data['line_number']
                        })
                        # Use the parsed message
                        message = debug_data['message']
                    else:
                        # Use the raw line if it doesn't match the debug format
                        message = line_str

                    self.logger.info(message, extra=extra)
                    self.logger.debug("GELF message emitted")

            except Exception as e:
                self.logger.error(f"Error in log monitoring: {e}")
                if self.process:
                    self.process.terminate()
                await asyncio.sleep(5)  # Wait before retrying
                continue

    def start_monitoring(self) -> None:
        """Start the log monitoring process."""
        self.logger.info("start_monitoring called")
        try:
            self._loop = asyncio.get_event_loop()
            self.logger.info("Got existing event loop")
        except RuntimeError:
            self.logger.info("No event loop found, creating new one")
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        
        if self.monitor_task is None or self.monitor_task.done():
            self.logger.info("Creating new monitor task")
            self.monitor_task = self._loop.create_task(self._monitor_log_file())
            self.logger.info("Monitor task created")
            
            # Run the task in the background
            def run_task():
                try:
                    if self._loop and self.monitor_task:
                        self._loop.run_until_complete(self.monitor_task)
                except asyncio.CancelledError:
                    self.logger.info("Monitor task was cancelled")
                except Exception as e:
                    self.logger.error(f"Error in monitor task: {e}")
            
            import threading
            thread = threading.Thread(target=run_task, daemon=True)
            thread.start()
            self.logger.info("Monitor task started in background thread")

    def stop_monitoring(self) -> None:
        """Stop the log monitoring process."""
        self.logger.info("stop_monitoring called")
        if self.process:
            self.logger.info("Terminating tail process")
            self.process.terminate()
        if self.monitor_task and not self.monitor_task.done():
            self.logger.info("Cancelling monitor task")
            self.monitor_task.cancel()
            if self._loop:
                self.logger.info("Running until monitor task completes")
                self._loop.run_until_complete(self.monitor_task)

    def update_match_id(self) -> None:
        """Update the current match ID."""
        self.logger.info("update_match_id called")
        self.current_match_id = self._get_next_match_id()
        self.logger.info(f"Updated match_id to: {self.current_match_id}") 