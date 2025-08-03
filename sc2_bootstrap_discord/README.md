# SC2 Bootstrap Discord

A Discord bot for managing StarCraft 2 matches using the local-bootstrap system, with integrated logging to Graylog.

## Features

- **Discord Bot Integration**: Queue and manage StarCraft 2 matches through Discord commands
- **Graylog Logging**: Forward structured log data to Graylog for monitoring and analysis
- **Log Parsing**: Parse StarCraft 2 debug logs with structured data extraction
- **Match Management**: Track match IDs and report results automatically

## Installation

```bash
pip install sc2-bootstrap-discord
```

## Quick Start

1. Create a Discord bot and get your token from the [Discord Developer Portal](https://discord.com/developers/applications)

2. Create a `.env` file with your configuration:
```env
DISCORD_TOKEN=your_discord_bot_token
PLAYER1=your_bot_name
CHANNEL_NAME=match-runner
GRAYLOG_HOST=your.graylog.server
GRAYLOG_PORT=12201
```

3. Run the bot:
```python
from sc2_bootstrap_discord import Sc2Runner
import discord
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = Sc2Runner(
    bot_name=os.getenv('PLAYER1'),
    graylog_host=os.getenv('GRAYLOG_HOST'),
    graylog_port=int(os.getenv('GRAYLOG_PORT', '12201')),
    log_file_path='logs/bot_controller1/TBone/stderr.log',
    intents=intents
)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.find_channel_id(os.getenv('CHANNEL_NAME'))

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

client.run(os.getenv('DISCORD_TOKEN'))
```

## Usage

### Discord Commands

- `!match <opponent> [map]` - Queue a match against the specified opponent (optional map)

### Log Monitoring

The bot automatically monitors StarCraft 2 debug logs and forwards them to Graylog with structured data including:

- Game time and step information
- Resource counts (minerals, gas, supply)
- Source file and line numbers
- Log levels (INFO, DEBUG, WARNING, Level X)
- Match context

## Development

### Setup Development Environment

```bash
git clone https://github.com/craigham/sc2-discord-bot.git
cd sc2-discord-bot
pip install -e ".[dev]"
```

### Running Tests

```bash
python -m pytest tests/
```

### Code Formatting

```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

## API Reference

### Sc2Runner

The main Discord bot class for managing StarCraft 2 matches.

#### Constructor

```python
Sc2Runner(
    bot_name: str,
    graylog_host: str | None = None,
    graylog_port: int = 12201,
    log_file_path: str | None = None,
    **kwargs
)
```

#### Methods

- `queue_match(opponent: str, map_name: str)` - Queue a match
- `find_channel_id(channel_name: str)` - Find Discord channel by name

### LogMonitor

Class for monitoring and parsing StarCraft 2 debug logs.

#### Constructor

```python
LogMonitor(
    log_file_path: str,
    graylog_host: str,
    graylog_port: int
)
```

#### Methods

- `start_monitoring()` - Start log monitoring
- `stop_monitoring()` - Stop log monitoring

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Support

For support, please open an issue on GitHub or contact the maintainers. 