"""
SC2 Bootstrap Discord - A Discord bot for managing StarCraft 2 matches.

This package provides a Discord bot that can queue and manage StarCraft 2 matches
using the local-bootstrap system, with integrated logging to Graylog.
"""

__version__ = "0.1.0"
__author__ = "Craig Hamilton"
__email__ = "craigh@quailholdings.com"

from .log_monitor import LogMonitor
from .sc2_runner import Sc2Runner

__all__ = ["LogMonitor", "Sc2Runner"] 