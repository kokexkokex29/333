import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

class ClubCommands:
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data = data_manager
        self.setup_commands()
    
    def setup_commands(self):
        """Setup all club-related slash commands"""
        
        @self.bot.tree.command(name="create_club", description="Create a new football club")
        @app_commands.describe(
            name="Name of the club",
            budget="Initial budget in Euros",
            image="Upload club logo/image"
        )
        async def create_club(interaction: discord.Interaction, name: str, budget: int, image: Optional[discord.Attachment] = None):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            # Check if club already exists
            clubs = self.data.load_clubs()
            if any(club['name'].lower() == name.lower() for club in clubs):
                await interaction.response.send_message(f"❌ Club '{name}' already exists!", ephemeral=True)
                return
            
            # Create new club
            club_data = {
                'id': len(clubs) + 1,
                'name': name,
                'budget': budget,
                'players': [],
                'created_by': interaction.user.id,
                'image_url': image.url if image else None
            }
            
            clubs.append(club_data)
            self.data.save_clubs(clubs)
            
            # Create embed response
            embed = discord.Embed(
                title="🏆 Club Created Successfully!",
                description=f"**{name}** has been established!",
                color=0x00ff00
            )
            embed.add_field(name="💰 Budget", value=f"€{budget:,}", inline=True)
            embed.add_field(name="👥 Players", value="0", inline=True)
            embed.add_field(name="🆔 Club ID", value=club_data['id'], inline=True)
            
            if image:
                embed.set_thumbnail(url=image.url)
            
            embed.set_footer(text=f"Created by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="list_clubs", description="Display all football clubs")
        async def list_clubs(interaction: discord.Interaction):
            clubs = self.data.load_clubs()
            
            if not clubs:
                embed = discord.Embed(
                    title="🏆 Football Clubs",
                    description="No clubs have been created yet!",
                    color=0xff9900
                )
                await interaction.response.send_message(embed=embed)
                return
            
            embed = discord.Embed(
                title="🏆 Football Clubs",
                description=f"Total clubs: {len(clubs)}",
                color=0x0099ff
            )
            
            for club in clubs:
                players_count = len(club.get('players', []))
                embed.add_field(
                    name=f"{club['name']} (ID: {club['id']})",
                    value=f"💰 Budget: €{club['budget']:,}\n👥 Players: {players_count}",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="club_info", description="Get detailed information about a specific club")
        @app_commands.describe(club_id="ID of the club to view")
        async def club_info(interaction: discord.Interaction, club_id: int):
            clubs = self.data.load_clubs()
            players = self.data.load_players()
            
            club = next((c for c in clubs if c['id'] == club_id), None)
            if not club:
                await interaction.response.send_message(f"❌ Club with ID {club_id} not found!", ephemeral=True)
                return
            
            # Get club players
            club_players = [p for p in players if p.get('club_id') == club_id]
            total_player_value = sum(p.get('value', 0) for p in club_players)
            
            embed = discord.Embed(
                title=f"🏆 {club['name']}",
                description=f"Club ID: {club['id']}",
                color=0x0099ff
            )
            
            if club.get('image_url'):
                embed.set_thumbnail(url=club['image_url'])
            
            embed.add_field(name="💰 Budget", value=f"€{club['budget']:,}", inline=True)
            embed.add_field(name="👥 Players", value=str(len(club_players)), inline=True)
            embed.add_field(name="💎 Total Player Value", value=f"€{total_player_value:,}", inline=True)
            
            if club_players:
                player_list = "\n".join([f"• {p['name']} (€{p['value']:,})" for p in club_players[:10]])
                if len(club_players) > 10:
                    player_list += f"\n... and {len(club_players) - 10} more"
                embed.add_field(name="🎯 Squad", value=player_list, inline=False)
            
            creator = self.bot.get_user(club.get('created_by'))
            if creator:
                embed.set_footer(text=f"Created by {creator.display_name}")
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="update_club_budget", description="Update a club's budget")
        @app_commands.describe(
            club_id="ID of the club",
            new_budget="New budget amount in Euros"
        )
        async def update_club_budget(interaction: discord.Interaction, club_id: int, new_budget: int):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            clubs = self.data.load_clubs()
            club = next((c for c in clubs if c['id'] == club_id), None)
            
            if not club:
                await interaction.response.send_message(f"❌ Club with ID {club_id} not found!", ephemeral=True)
                return
            
            old_budget = club['budget']
            club['budget'] = new_budget
            self.data.save_clubs(clubs)
            
            embed = discord.Embed(
                title="💰 Budget Updated",
                description=f"**{club['name']}** budget has been updated!",
                color=0x00ff00
            )
            embed.add_field(name="Old Budget", value=f"€{old_budget:,}", inline=True)
            embed.add_field(name="New Budget", value=f"€{new_budget:,}", inline=True)
            embed.add_field(name="Change", value=f"€{new_budget - old_budget:+,}", inline=True)
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="delete_club", description="Delete a football club")
        @app_commands.describe(club_id="ID of the club to delete")
        async def delete_club(interaction: discord.Interaction, club_id: int):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            clubs = self.data.load_clubs()
            players = self.data.load_players()
            
            club = next((c for c in clubs if c['id'] == club_id), None)
            if not club:
                await interaction.response.send_message(f"❌ Club with ID {club_id} not found!", ephemeral=True)
                return
            
            # Remove club players
            players = [p for p in players if p.get('club_id') != club_id]
            self.data.save_players(players)
            
            # Remove club
            clubs = [c for c in clubs if c['id'] != club_id]
            self.data.save_clubs(clubs)
            
            embed = discord.Embed(
                title="🗑️ Club Deleted",
                description=f"**{club['name']}** has been deleted successfully!",
                color=0xff0000
            )
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="clear_club", description="Delete a club completely")
        @app_commands.describe(club_id="ID of the club to delete")
        async def clear_club(interaction: discord.Interaction, club_id: int):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            clubs = self.data.load_clubs()
            players = self.data.load_players()
            
            club = next((c for c in clubs if c['id'] == club_id), None)
            if not club:
                await interaction.response.send_message(f"❌ Club with ID {club_id} not found!", ephemeral=True)
                return
            
            # Find players in this club
            club_players = [p for p in players if p.get('club_id') == club_id]
            
            # Remove club players completely
            players = [p for p in players if p.get('club_id') != club_id]
            self.data.save_players(players)
            
            # Remove club
            clubs = [c for c in clubs if c['id'] != club_id]
            self.data.save_clubs(clubs)
            
            embed = discord.Embed(
                title="🗑️ Club Deleted",
                description=f"**{club['name']}** has been completely deleted!",
                color=0xff0000
            )
            embed.add_field(name="🏆 Club", value=club['name'], inline=True)
            embed.add_field(name="👥 Players Deleted", value=str(len(club_players)), inline=True)
            embed.add_field(name="📊 Status", value="Club and all players removed", inline=True)
            
            if club_players:
                if len(club_players) <= 10:
                    player_list = "\n".join([f"• {p['name']}" for p in club_players])
                    embed.add_field(name="🎯 Deleted Players", value=player_list, inline=False)
                else:
                    player_list = "\n".join([f"• {p['name']}" for p in club_players[:10]])
                    player_list += f"\n... and {len(club_players) - 10} more players"
                    embed.add_field(name="🎯 Deleted Players", value=player_list, inline=False)
            
            embed.set_footer(text=f"Club deleted by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="set_club_role", description="Assign a Discord role to a club")
        @app_commands.describe(
            club_id="ID of the club",
            role="Discord role to assign to this club"
        )
        async def set_club_role(interaction: discord.Interaction, club_id: int, role: discord.Role):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            clubs = self.data.load_clubs()
            club = next((c for c in clubs if c['id'] == club_id), None)
            
            if not club:
                await interaction.response.send_message(f"❌ Club with ID {club_id} not found!", ephemeral=True)
                return
            
            # Update club with role ID
            club['role_id'] = role.id
            club['role_name'] = role.name
            self.data.save_clubs(clubs)
            
            embed = discord.Embed(
                title="🏷️ Club Role Assigned",
                description=f"**{club['name']}** has been linked to role **{role.name}**!",
                color=0x00ff00
            )
            embed.add_field(name="🏆 Club", value=club['name'], inline=True)
            embed.add_field(name="🎭 Role", value=role.mention, inline=True)
            embed.add_field(name="👥 Members", value=str(len(role.members)), inline=True)
            
            embed.set_footer(text=f"Role assigned by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="remove_club_role", description="Remove Discord role from a club")
        @app_commands.describe(club_id="ID of the club")
        async def remove_club_role(interaction: discord.Interaction, club_id: int):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            clubs = self.data.load_clubs()
            club = next((c for c in clubs if c['id'] == club_id), None)
            
            if not club:
                await interaction.response.send_message(f"❌ Club with ID {club_id} not found!", ephemeral=True)
                return
            
            if not club.get('role_id'):
                await interaction.response.send_message(f"❌ **{club['name']}** doesn't have an assigned role!", ephemeral=True)
                return
            
            # Remove role data
            role_name = club.get('role_name', 'Unknown Role')
            club.pop('role_id', None)
            club.pop('role_name', None)
            self.data.save_clubs(clubs)
            
            embed = discord.Embed(
                title="🚫 Club Role Removed",
                description=f"Role **{role_name}** has been removed from **{club['name']}**!",
                color=0xff9900
            )
            embed.add_field(name="🏆 Club", value=club['name'], inline=True)
            embed.add_field(name="🎭 Role", value=f"~~{role_name}~~", inline=True)
            
            embed.set_footer(text=f"Role removed by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="club_roles", description="Display all clubs and their assigned roles")
        async def club_roles(interaction: discord.Interaction):
            clubs = self.data.load_clubs()
            
            if not clubs:
                await interaction.response.send_message("❌ No clubs found in the database!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🏷️ Club Roles",
                description="Clubs and their assigned Discord roles",
                color=0x0099ff
            )
            
            clubs_with_roles = 0
            for club in clubs:
                if club.get('role_id'):
                    role = interaction.guild.get_role(club['role_id']) if interaction.guild else None
                    role_text = role.mention if role else f"~~{club.get('role_name', 'Unknown')}~~ (Role Deleted)"
                    clubs_with_roles += 1
                else:
                    role_text = "*No role assigned*"
                
                embed.add_field(
                    name=f"🏆 {club['name']} (ID: {club['id']})",
                    value=f"🎭 Role: {role_text}",
                    inline=True
                )
            
            embed.set_footer(text=f"{clubs_with_roles}/{len(clubs)} clubs have assigned roles")
            
            await interaction.response.send_message(embed=embed)
