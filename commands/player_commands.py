import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

class PlayerCommands:
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data = data_manager
        self.setup_commands()
    
    def setup_commands(self):
        """Setup all player-related slash commands"""
        
        @self.bot.tree.command(name="create_player", description="Create a new player")
        @app_commands.describe(
            name="Player's name",
            value="Player's market value in Euros",
            position="Player's position (GK, DEF, MID, ATT)",
            age="Player's age",
            club_id="Club ID to assign player to (optional)",
            image="Upload player image"
        )
        async def create_player(interaction: discord.Interaction, name: str, value: int, position: str, age: int, club_id: Optional[int] = None, image: Optional[discord.Attachment] = None):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            # Validate position
            valid_positions = ['GK', 'DEF', 'MID', 'ATT']
            if position.upper() not in valid_positions:
                await interaction.response.send_message(f"❌ Invalid position! Use: {', '.join(valid_positions)}", ephemeral=True)
                return
            
            # Check if club exists if club_id provided
            if club_id:
                clubs = self.data.load_clubs()
                club = next((c for c in clubs if c['id'] == club_id), None)
                if not club:
                    await interaction.response.send_message(f"❌ Club with ID {club_id} not found!", ephemeral=True)
                    return
            
            players = self.data.load_players()
            
            # Check if player already exists
            if any(p['name'].lower() == name.lower() for p in players):
                await interaction.response.send_message(f"❌ Player '{name}' already exists!", ephemeral=True)
                return
            
            # Create new player
            player_data = {
                'id': len(players) + 1,
                'name': name,
                'value': value,
                'position': position.upper(),
                'age': age,
                'club_id': club_id,
                'created_by': interaction.user.id,
                'transfers': 0,
                'image_url': image.url if image else None
            }
            
            players.append(player_data)
            self.data.save_players(players)
            
            # Create embed response
            embed = discord.Embed(
                title="⚽ Player Created Successfully!",
                description=f"**{name}** has been added to the database!",
                color=0x00ff00
            )
            
            embed.add_field(name="💰 Value", value=f"€{value:,}", inline=True)
            embed.add_field(name="🎯 Position", value=position.upper(), inline=True)
            embed.add_field(name="🎂 Age", value=f"{age} years", inline=True)
            embed.add_field(name="🆔 Player ID", value=player_data['id'], inline=True)
            
            if club_id:
                club_name = next((c['name'] for c in clubs if c['id'] == club_id), "Unknown")
                embed.add_field(name="🏆 Club", value=club_name, inline=True)
            else:
                embed.add_field(name="🏆 Club", value="Free Agent", inline=True)
            
            if image:
                embed.set_thumbnail(url=image.url)
            
            embed.set_footer(text=f"Created by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="list_players", description="Display all players or players from a specific club")
        @app_commands.describe(club_id="Filter by club ID (optional)")
        async def list_players(interaction: discord.Interaction, club_id: Optional[int] = None):
            players = self.data.load_players()
            clubs = self.data.load_clubs()
            
            if club_id:
                players = [p for p in players if p.get('club_id') == club_id]
                club_name = next((c['name'] for c in clubs if c['id'] == club_id), f"Club {club_id}")
                title = f"⚽ Players in {club_name}"
            else:
                title = "⚽ All Players"
            
            if not players:
                embed = discord.Embed(
                    title=title,
                    description="No players found!",
                    color=0xff9900
                )
                await interaction.response.send_message(embed=embed)
                return
            
            embed = discord.Embed(
                title=title,
                description=f"Total players: {len(players)}",
                color=0x0099ff
            )
            
            # Sort players by value (highest first)
            players.sort(key=lambda x: x.get('value', 0), reverse=True)
            
            for player in players[:20]:  # Show top 20 players
                club_name = "Free Agent"
                if player.get('club_id'):
                    club_name = next((c['name'] for c in clubs if c['id'] == player['club_id']), "Unknown Club")
                
                embed.add_field(
                    name=f"{player['name']} (ID: {player['id']})",
                    value=f"💰 €{player['value']:,} | {player['position']} | Age {player['age']}\n🏆 {club_name}",
                    inline=True
                )
            
            if len(players) > 20:
                embed.set_footer(text=f"Showing top 20 of {len(players)} players")
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="player_info", description="Get detailed information about a specific player")
        @app_commands.describe(player_id="ID of the player to view")
        async def player_info(interaction: discord.Interaction, player_id: int):
            players = self.data.load_players()
            clubs = self.data.load_clubs()
            transfers = self.data.load_transfers()
            
            player = next((p for p in players if p['id'] == player_id), None)
            if not player:
                await interaction.response.send_message(f"❌ Player with ID {player_id} not found!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"⚽ {player['name']}",
                description=f"Player ID: {player['id']}",
                color=0x0099ff
            )
            
            if player.get('image_url'):
                embed.set_thumbnail(url=player['image_url'])
            
            embed.add_field(name="💰 Value", value=f"€{player['value']:,}", inline=True)
            embed.add_field(name="🎯 Position", value=player['position'], inline=True)
            embed.add_field(name="🎂 Age", value=f"{player['age']} years", inline=True)
            
            # Club info
            if player.get('club_id'):
                club_name = next((c['name'] for c in clubs if c['id'] == player['club_id']), "Unknown Club")
                embed.add_field(name="🏆 Current Club", value=club_name, inline=True)
            else:
                embed.add_field(name="🏆 Current Club", value="Free Agent", inline=True)
            
            # Transfer history
            player_transfers = [t for t in transfers if t.get('player_id') == player_id]
            embed.add_field(name="🔄 Transfers", value=str(len(player_transfers)), inline=True)
            
            # Recent transfers
            if player_transfers:
                recent_transfers = sorted(player_transfers, key=lambda x: x.get('timestamp', 0), reverse=True)[:3]
                transfer_text = []
                for transfer in recent_transfers:
                    from_club = "Free Agent"
                    to_club = "Free Agent"
                    if transfer.get('from_club_id'):
                        from_club = next((c['name'] for c in clubs if c['id'] == transfer['from_club_id']), "Unknown")
                    if transfer.get('to_club_id'):
                        to_club = next((c['name'] for c in clubs if c['id'] == transfer['to_club_id']), "Unknown")
                    transfer_text.append(f"• {from_club} → {to_club} (€{transfer.get('fee', 0):,})")
                
                embed.add_field(name="📈 Recent Transfers", value="\n".join(transfer_text), inline=False)
            
            creator = self.bot.get_user(player.get('created_by'))
            if creator:
                embed.set_footer(text=f"Created by {creator.display_name}")
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="update_player_value", description="Update a player's market value")
        @app_commands.describe(
            player_id="ID of the player",
            new_value="New market value in Euros"
        )
        async def update_player_value(interaction: discord.Interaction, player_id: int, new_value: int):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            players = self.data.load_players()
            player = next((p for p in players if p['id'] == player_id), None)
            
            if not player:
                await interaction.response.send_message(f"❌ Player with ID {player_id} not found!", ephemeral=True)
                return
            
            old_value = player['value']
            player['value'] = new_value
            self.data.save_players(players)
            
            embed = discord.Embed(
                title="💰 Player Value Updated",
                description=f"**{player['name']}** value has been updated!",
                color=0x00ff00
            )
            embed.add_field(name="Old Value", value=f"€{old_value:,}", inline=True)
            embed.add_field(name="New Value", value=f"€{new_value:,}", inline=True)
            embed.add_field(name="Change", value=f"€{new_value - old_value:+,}", inline=True)
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="transfer_player", description="Transfer a player between clubs")
        @app_commands.describe(
            player_id="ID of the player to transfer",
            to_club_id="ID of the destination club",
            transfer_fee="Transfer fee in Euros"
        )
        async def transfer_player(interaction: discord.Interaction, player_id: int, to_club_id: int, transfer_fee: int):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            players = self.data.load_players()
            clubs = self.data.load_clubs()
            transfers = self.data.load_transfers()
            
            player = next((p for p in players if p['id'] == player_id), None)
            to_club = next((c for c in clubs if c['id'] == to_club_id), None)
            
            if not player:
                await interaction.response.send_message(f"❌ Player with ID {player_id} not found!", ephemeral=True)
                return
            
            if not to_club:
                await interaction.response.send_message(f"❌ Club with ID {to_club_id} not found!", ephemeral=True)
                return
            
            # Check if destination club has enough budget
            if to_club['budget'] < transfer_fee:
                await interaction.response.send_message(f"❌ {to_club['name']} doesn't have enough budget! (Has: €{to_club['budget']:,}, Needs: €{transfer_fee:,})", ephemeral=True)
                return
            
            # Get source club info
            from_club = None
            if player.get('club_id'):
                from_club = next((c for c in clubs if c['id'] == player['club_id']), None)
            
            # Update club budgets
            to_club['budget'] -= transfer_fee
            if from_club:
                from_club['budget'] += transfer_fee
            
            # Record transfer
            transfer_record = {
                'id': len(transfers) + 1,
                'player_id': player_id,
                'from_club_id': player.get('club_id'),
                'to_club_id': to_club_id,
                'fee': transfer_fee,
                'timestamp': discord.utils.utcnow().timestamp(),
                'processed_by': interaction.user.id
            }
            
            transfers.append(transfer_record)
            
            # Update player's club
            player['club_id'] = to_club_id
            player['transfers'] = player.get('transfers', 0) + 1
            
            # Save all data
            self.data.save_players(players)
            self.data.save_clubs(clubs)
            self.data.save_transfers(transfers)
            
            # Create embed response
            embed = discord.Embed(
                title="🔄 Player Transfer Completed!",
                description=f"**{player['name']}** has been transferred!",
                color=0x00ff00
            )
            
            from_club_name = from_club['name'] if from_club else "Free Agent"
            embed.add_field(name="From", value=from_club_name, inline=True)
            embed.add_field(name="To", value=to_club['name'], inline=True)
            embed.add_field(name="💰 Fee", value=f"€{transfer_fee:,}", inline=True)
            
            if from_club:
                embed.add_field(name=f"{from_club['name']} Budget", value=f"€{from_club['budget']:,}", inline=True)
            embed.add_field(name=f"{to_club['name']} Budget", value=f"€{to_club['budget']:,}", inline=True)
            
            embed.set_footer(text=f"Transfer #{transfer_record['id']} | Processed by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="release_player", description="Release a player from their club")
        @app_commands.describe(player_id="ID of the player to release")
        async def release_player(interaction: discord.Interaction, player_id: int):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            players = self.data.load_players()
            clubs = self.data.load_clubs()
            
            player = next((p for p in players if p['id'] == player_id), None)
            if not player:
                await interaction.response.send_message(f"❌ Player with ID {player_id} not found!", ephemeral=True)
                return
            
            if not player.get('club_id'):
                await interaction.response.send_message(f"❌ {player['name']} is already a free agent!", ephemeral=True)
                return
            
            club = next((c for c in clubs if c['id'] == player['club_id']), None)
            club_name = club['name'] if club else "Unknown Club"
            
            # Release player
            player['club_id'] = None
            self.data.save_players(players)
            
            embed = discord.Embed(
                title="🆓 Player Released",
                description=f"**{player['name']}** has been released from **{club_name}**!",
                color=0xff9900
            )
            embed.add_field(name="Player Value", value=f"€{player['value']:,}", inline=True)
            embed.add_field(name="Status", value="Free Agent", inline=True)
            
            await interaction.response.send_message(embed=embed)
