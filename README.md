A discord bot which controls local-bootstrap to run matches by sending commands in discord.

## Necessary to run

Need to create an application and get a bot token on Discord website.

create .env file based on sample in repo.

install the requirements.  Could use virtualenv, i just install it globally because i run my bootstrap server on a virtual machine.

pip3 install -r requirements.txt or pip the libraries inside requirements.txt


## How to run

The run_match.py file should be in the root directory for the local-boostrap match runner.  

(activate venv if you set that up)

python3 run_match.py

## How to start a match 
(The bot actually listens on all channels for these commands, by convention i just do it in the match-runner channel):

!match 12PoolBot Acropolis

to create a match with a random map, omit the map.

eg. !match MicroMachine


You can queue multiple matches.

## List available bots
!bots

## List available maps
!maps

## View the match queue
!queue
