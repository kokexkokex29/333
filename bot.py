import discord
from discord.ext import commands
import asyncio
import os
from utils.data_manager import DataManager
from utils.scheduler import MatchScheduler

class DiscordBot:
    def __init__(self):
        # Set up bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        # Create bot instance
        self.bot = commands.Bot(
            command_prefix='!',  # Slash commands primarily, but keeping prefix for compatibility
            intents=intents,
            help_command=None
        )
        
        # Initialize data manager and scheduler
        self.data_manager = DataManager()
        self.scheduler = MatchScheduler(self.bot, self.data_manager)
        
        # Setup events
        self.setup_events()
        
        # Load commands
        self.load_commands()
    
    def setup_events(self):
        """Setup bot events"""
        @self.bot.event
        async def on_ready():
            print(f'{self.bot.user} has connected to Discord!')
            print(f'Bot is in {len(self.bot.guilds)} guilds')
            
            # Sync slash commands
            try:
                synced = await self.bot.tree.sync()
                print(f'Synced {len(synced)} command(s)')
            except Exception as e:
                print(f'Failed to sync commands: {e}')
            
            # Start the match scheduler
            await self.scheduler.start()
        
        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.MissingPermissions):
                await ctx.send("❌ You don't have permission to use this command!")
            elif isinstance(error, commands.CommandNotFound):
                pass  # Ignore unknown commands
            else:
                print(f"Command error: {error}")
    
    def load_commands(self):
        """Load all command modules"""
        from commands.club_commands import ClubCommands
        from commands.player_commands import PlayerCommands
        from commands.match_commands import MatchCommands
        from commands.stats_commands import StatsCommands
        from commands.admin_commands import AdminCommands
        
        # Add command classes to bot
        ClubCommands(self.bot, self.data_manager)
        PlayerCommands(self.bot, self.data_manager)
        MatchCommands(self.bot, self.data_manager, self.scheduler)
        StatsCommands(self.bot, self.data_manager)
        AdminCommands(self.bot, self.data_manager)
    
    async def run(self, token):
        """Run the bot"""
        await self.bot.start(token)
