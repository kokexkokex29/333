import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from typing import Optional

class AdminCommands:
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data = data_manager
        self.setup_commands()
    
    def setup_commands(self):
        """Setup all admin-related slash commands"""
        
        @self.bot.tree.command(name="reset_all", description="Reset all data (clubs, players, matches, transfers)")
        async def reset_all(interaction: discord.Interaction):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            # Create confirmation embed
            embed = discord.Embed(
                title="⚠️ DANGER: Reset All Data",
                description="This will permanently delete ALL data including:\n• All clubs\n• All players\n• All matches\n• All transfers",
                color=0xff0000
            )
            embed.add_field(name="❌ This action cannot be undone!", value="Type 'CONFIRM RESET' to proceed", inline=False)
            
            # Create a view with buttons for confirmation
            view = ResetConfirmationView(self.data)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        @self.bot.tree.command(name="backup_data", description="Create a backup of all data")
        async def backup_data(interaction: discord.Interaction):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            try:
                # Load all data
                clubs = self.data.load_clubs()
                players = self.data.load_players()
                matches = self.data.load_matches()
                transfers = self.data.load_transfers()
                
                # Create backup data structure
                backup_data = {
                    'clubs': clubs,
                    'players': players,
                    'matches': matches,
                    'transfers': transfers,
                    'backup_info': {
                        'created_by': interaction.user.id,
                        'created_at': discord.utils.utcnow().isoformat(),
                        'total_clubs': len(clubs),
                        'total_players': len(players),
                        'total_matches': len(matches),
                        'total_transfers': len(transfers)
                    }
                }
                
                # Convert to JSON string
                backup_json = json.dumps(backup_data, indent=2)
                
                # Create file-like object
                backup_file = discord.File(
                    fp=discord.utils.BytesIO(backup_json.encode()),
                    filename=f"backup_{discord.utils.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                )
                
                embed = discord.Embed(
                    title="💾 Data Backup Created",
                    description="Complete backup of all bot data",
                    color=0x00ff00
                )
                embed.add_field(name="📊 Clubs", value=str(len(clubs)), inline=True)
                embed.add_field(name="⚽ Players", value=str(len(players)), inline=True)
                embed.add_field(name="🏟️ Matches", value=str(len(matches)), inline=True)
                embed.add_field(name="🔄 Transfers", value=str(len(transfers)), inline=True)
                embed.set_footer(text=f"Backup created by {interaction.user.display_name}")
                
                await interaction.response.send_message(embed=embed, file=backup_file)
                
            except Exception as e:
                await interaction.response.send_message(f"❌ Error creating backup: {str(e)}", ephemeral=True)
        
        @self.bot.tree.command(name="system_info", description="Display bot system information")
        async def system_info(interaction: discord.Interaction):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            # Load data counts
            clubs = self.data.load_clubs()
            players = self.data.load_players()
            matches = self.data.load_matches()
            transfers = self.data.load_transfers()
            
            # Calculate file sizes
            def get_file_size(filepath):
                try:
                    return os.path.getsize(filepath)
                except:
                    return 0
            
            clubs_size = get_file_size('data/clubs.json')
            players_size = get_file_size('data/players.json')
            matches_size = get_file_size('data/matches.json')
            transfers_size = get_file_size('data/transfers.json')
            
            embed = discord.Embed(
                title="🖥️ System Information",
                description="Bot database and system status",
                color=0x0099ff
            )
            
            embed.add_field(
                name="📊 Database Statistics",
                value=f"🏆 Clubs: {len(clubs)}\n⚽ Players: {len(players)}\n🏟️ Matches: {len(matches)}\n🔄 Transfers: {len(transfers)}",
                inline=True
            )
            
            embed.add_field(
                name="💾 File Sizes",
                value=f"📁 clubs.json: {clubs_size} bytes\n📁 players.json: {players_size} bytes\n📁 matches.json: {matches_size} bytes\n📁 transfers.json: {transfers_size} bytes",
                inline=True
            )
            
            embed.add_field(
                name="🤖 Bot Status",
                value=f"🟢 Online\n🏓 Latency: {round(self.bot.latency * 1000)}ms\n🏠 Guilds: {len(self.bot.guilds)}",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="embed_with_image", description="Create a custom embed with image upload")
        @app_commands.describe(
            title="Embed title",
            description="Embed description",
            color="Embed color (hex code without #, e.g., ff0000)",
            image="Upload an image from your album"
        )
        async def embed_with_image(interaction: discord.Interaction, title: str, description: str, color: Optional[str] = None, image: Optional[discord.Attachment] = None):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            # Parse color
            embed_color = 0x0099ff  # Default blue
            if color:
                try:
                    embed_color = int(color, 16)
                except ValueError:
                    await interaction.response.send_message("❌ Invalid color format! Use hex without # (e.g., ff0000)", ephemeral=True)
                    return
            
            # Create embed
            embed = discord.Embed(
                title=title,
                description=description,
                color=embed_color
            )
            
            # Add image if provided
            if image:
                embed.set_image(url=image.url)
                embed.add_field(name="📷 Image", value="Uploaded from album", inline=False)
            
            # Add additional information
            embed.add_field(name="👤 Created by", value=interaction.user.mention, inline=True)
            embed.add_field(name="📅 Created at", value=discord.utils.format_dt(discord.utils.utcnow(), 'F'), inline=True)
            embed.add_field(name="🤖 Bot", value=self.bot.user.mention, inline=True)
            
            embed.set_footer(text=f"Custom embed • Created by {interaction.user.display_name}")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="rename_club", description="Rename an existing club")
        @app_commands.describe(
            club_id="ID of the club to rename",
            new_name="New name for the club"
        )
        async def rename_club(interaction: discord.Interaction, club_id: int, new_name: str):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            clubs = self.data.load_clubs()
            club = next((c for c in clubs if c['id'] == club_id), None)
            
            if not club:
                await interaction.response.send_message(f"❌ Club with ID {club_id} not found!", ephemeral=True)
                return
            
            # Check if new name already exists
            if any(c['name'].lower() == new_name.lower() and c['id'] != club_id for c in clubs):
                await interaction.response.send_message(f"❌ A club named '{new_name}' already exists!", ephemeral=True)
                return
            
            old_name = club['name']
            club['name'] = new_name
            self.data.save_clubs(clubs)
            
            embed = discord.Embed(
                title="✏️ Club Renamed",
                description="Club name has been updated successfully!",
                color=0x00ff00
            )
            embed.add_field(name="Old Name", value=old_name, inline=True)
            embed.add_field(name="New Name", value=new_name, inline=True)
            embed.add_field(name="Club ID", value=club_id, inline=True)
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="rename_player", description="Rename an existing player")
        @app_commands.describe(
            player_id="ID of the player to rename",
            new_name="New name for the player"
        )
        async def rename_player(interaction: discord.Interaction, player_id: int, new_name: str):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            players = self.data.load_players()
            player = next((p for p in players if p['id'] == player_id), None)
            
            if not player:
                await interaction.response.send_message(f"❌ Player with ID {player_id} not found!", ephemeral=True)
                return
            
            # Check if new name already exists
            if any(p['name'].lower() == new_name.lower() and p['id'] != player_id for p in players):
                await interaction.response.send_message(f"❌ A player named '{new_name}' already exists!", ephemeral=True)
                return
            
            old_name = player['name']
            player['name'] = new_name
            self.data.save_players(players)
            
            embed = discord.Embed(
                title="✏️ Player Renamed",
                description="Player name has been updated successfully!",
                color=0x00ff00
            )
            embed.add_field(name="Old Name", value=old_name, inline=True)
            embed.add_field(name="New Name", value=new_name, inline=True)
            embed.add_field(name="Player ID", value=player_id, inline=True)
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="update_player_age", description="Update a player's age")
        @app_commands.describe(
            player_id="ID of the player",
            new_age="New age for the player"
        )
        async def update_player_age(interaction: discord.Interaction, player_id: int, new_age: int):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            if new_age < 16 or new_age > 45:
                await interaction.response.send_message("❌ Age must be between 16 and 45!", ephemeral=True)
                return
            
            players = self.data.load_players()
            player = next((p for p in players if p['id'] == player_id), None)
            
            if not player:
                await interaction.response.send_message(f"❌ Player with ID {player_id} not found!", ephemeral=True)
                return
            
            old_age = player.get('age', 0)
            player['age'] = new_age
            self.data.save_players(players)
            
            embed = discord.Embed(
                title="🎂 Player Age Updated",
                description=f"**{player['name']}** age has been updated!",
                color=0x00ff00
            )
            embed.add_field(name="Old Age", value=f"{old_age} years", inline=True)
            embed.add_field(name="New Age", value=f"{new_age} years", inline=True)
            embed.add_field(name="Change", value=f"{new_age - old_age:+d} years", inline=True)
            
            await interaction.response.send_message(embed=embed)

class ResetConfirmationView(discord.ui.View):
    def __init__(self, data_manager):
        super().__init__(timeout=60)
        self.data = data_manager
    
    @discord.ui.button(label="CONFIRM RESET", style=discord.ButtonStyle.danger, emoji="💀")
    async def confirm_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Reset all data files
        self.data.save_clubs([])
        self.data.save_players([])
        self.data.save_matches([])
        self.data.save_transfers([])
        
        embed = discord.Embed(
            title="💀 ALL DATA RESET",
            description="All data has been permanently deleted!",
            color=0xff0000
        )
        embed.add_field(name="✅ Reset Complete", value="• All clubs deleted\n• All players deleted\n• All matches deleted\n• All transfers deleted", inline=False)
        embed.set_footer(text=f"Reset performed by {interaction.user.display_name}")
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Reset Cancelled",
            description="No data was modified.",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=None)
