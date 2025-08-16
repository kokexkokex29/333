import discord
from discord.ext import commands
from discord import app_commands
from collections import defaultdict
import json

class StatsCommands:
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data = data_manager
        self.setup_commands()
    
    def setup_commands(self):
        """Setup all statistics-related slash commands"""
        
        @self.bot.tree.command(name="league_stats", description="Display comprehensive league statistics")
        async def league_stats(interaction: discord.Interaction):
            clubs = self.data.load_clubs()
            players = self.data.load_players()
            transfers = self.data.load_transfers()
            matches = self.data.load_matches()
            
            if not clubs:
                await interaction.response.send_message("❌ No clubs found in the database!", ephemeral=True)
                return
            
            # Calculate statistics
            total_players = len(players)
            total_transfers = len(transfers)
            total_matches = len(matches)
            total_budget = sum(club.get('budget', 0) for club in clubs)
            total_player_value = sum(player.get('value', 0) for player in players)
            
            # Find richest and poorest clubs
            richest_club = max(clubs, key=lambda x: x.get('budget', 0))
            poorest_club = min(clubs, key=lambda x: x.get('budget', 0))
            
            # Find most valuable player
            most_valuable_player = max(players, key=lambda x: x.get('value', 0)) if players else None
            
            embed = discord.Embed(
                title="📊 League Statistics",
                description="Comprehensive overview of the football league",
                color=0x0099ff
            )
            
            embed.add_field(name="🏆 Total Clubs", value=str(len(clubs)), inline=True)
            embed.add_field(name="⚽ Total Players", value=str(total_players), inline=True)
            embed.add_field(name="🔄 Total Transfers", value=str(total_transfers), inline=True)
            
            embed.add_field(name="⚽ Scheduled Matches", value=str(total_matches), inline=True)
            embed.add_field(name="💰 Total League Budget", value=f"€{total_budget:,}", inline=True)
            embed.add_field(name="💎 Total Player Value", value=f"€{total_player_value:,}", inline=True)
            
            embed.add_field(name="🥇 Richest Club", value=f"{richest_club['name']}\n€{richest_club['budget']:,}", inline=True)
            embed.add_field(name="🥉 Poorest Club", value=f"{poorest_club['name']}\n€{poorest_club['budget']:,}", inline=True)
            
            if most_valuable_player:
                embed.add_field(name="💎 Most Valuable Player", value=f"{most_valuable_player['name']}\n€{most_valuable_player['value']:,}", inline=True)
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="top_players", description="Display top players by market value")
        @app_commands.describe(limit="Number of players to show (default: 10)")
        async def top_players(interaction: discord.Interaction, limit: int = 10):
            players = self.data.load_players()
            clubs = self.data.load_clubs()
            
            if not players:
                await interaction.response.send_message("❌ No players found in the database!", ephemeral=True)
                return
            
            # Sort players by value
            sorted_players = sorted(players, key=lambda x: x.get('value', 0), reverse=True)
            top_players = sorted_players[:min(limit, 25)]  # Max 25 players
            
            embed = discord.Embed(
                title=f"💎 Top {len(top_players)} Players by Value",
                description="Most valuable players in the league",
                color=0xffd700
            )
            
            for i, player in enumerate(top_players, 1):
                club_name = "Free Agent"
                if player.get('club_id'):
                    club = next((c for c in clubs if c['id'] == player['club_id']), None)
                    if club:
                        club_name = club['name']
                
                embed.add_field(
                    name=f"{i}. {player['name']}",
                    value=f"💰 €{player['value']:,}\n🎯 {player['position']} | Age {player['age']}\n🏆 {club_name}",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="club_rankings", description="Display clubs ranked by total value")
        async def club_rankings(interaction: discord.Interaction):
            clubs = self.data.load_clubs()
            players = self.data.load_players()
            
            if not clubs:
                await interaction.response.send_message("❌ No clubs found in the database!", ephemeral=True)
                return
            
            # Calculate total value for each club (budget + player values)
            club_values = []
            for club in clubs:
                club_players = [p for p in players if p.get('club_id') == club['id']]
                total_player_value = sum(p.get('value', 0) for p in club_players)
                total_value = club['budget'] + total_player_value
                
                club_values.append({
                    'club': club,
                    'player_count': len(club_players),
                    'player_value': total_player_value,
                    'total_value': total_value
                })
            
            # Sort by total value
            club_values.sort(key=lambda x: x['total_value'], reverse=True)
            
            embed = discord.Embed(
                title="🏆 Club Rankings by Total Value",
                description="Clubs ranked by budget + player values",
                color=0xffd700
            )
            
            for i, club_data in enumerate(club_values, 1):
                club = club_data['club']
                embed.add_field(
                    name=f"{i}. {club['name']}",
                    value=f"💰 Budget: €{club['budget']:,}\n💎 Players: €{club_data['player_value']:,}\n🔥 Total: €{club_data['total_value']:,}\n👥 Squad: {club_data['player_count']} players",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="transfer_activity", description="Display recent transfer activity")
        @app_commands.describe(limit="Number of transfers to show (default: 10)")
        async def transfer_activity(interaction: discord.Interaction, limit: int = 10):
            transfers = self.data.load_transfers()
            players = self.data.load_players()
            clubs = self.data.load_clubs()
            
            if not transfers:
                await interaction.response.send_message("❌ No transfers found in the database!", ephemeral=True)
                return
            
            # Sort transfers by timestamp (most recent first)
            sorted_transfers = sorted(transfers, key=lambda x: x.get('timestamp', 0), reverse=True)
            recent_transfers = sorted_transfers[:min(limit, 20)]  # Max 20 transfers
            
            embed = discord.Embed(
                title=f"🔄 Recent Transfer Activity",
                description=f"Latest {len(recent_transfers)} transfers",
                color=0x00ff00
            )
            
            for transfer in recent_transfers:
                player = next((p for p in players if p['id'] == transfer['player_id']), None)
                if not player:
                    continue
                
                from_club_name = "Free Agent"
                to_club_name = "Free Agent"
                
                if transfer.get('from_club_id'):
                    from_club = next((c for c in clubs if c['id'] == transfer['from_club_id']), None)
                    if from_club:
                        from_club_name = from_club['name']
                
                if transfer.get('to_club_id'):
                    to_club = next((c for c in clubs if c['id'] == transfer['to_club_id']), None)
                    if to_club:
                        to_club_name = to_club['name']
                
                embed.add_field(
                    name=f"Transfer #{transfer['id']}: {player['name']}",
                    value=f"📤 From: {from_club_name}\n📥 To: {to_club_name}\n💰 Fee: €{transfer['fee']:,}",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="position_stats", description="Display player statistics by position")
        async def position_stats(interaction: discord.Interaction):
            players = self.data.load_players()
            
            if not players:
                await interaction.response.send_message("❌ No players found in the database!", ephemeral=True)
                return
            
            # Group players by position
            position_stats = defaultdict(list)
            for player in players:
                position = player.get('position', 'Unknown')
                position_stats[position].append(player)
            
            embed = discord.Embed(
                title="🎯 Player Statistics by Position",
                description="Breakdown of players by their positions",
                color=0x0099ff
            )
            
            for position, position_players in position_stats.items():
                count = len(position_players)
                avg_value = sum(p.get('value', 0) for p in position_players) / count if count > 0 else 0
                avg_age = sum(p.get('age', 0) for p in position_players) / count if count > 0 else 0
                most_valuable = max(position_players, key=lambda x: x.get('value', 0))
                
                embed.add_field(
                    name=f"{position} ({count} players)",
                    value=f"📊 Avg Value: €{avg_value:,.0f}\n🎂 Avg Age: {avg_age:.1f} years\n⭐ Top: {most_valuable['name']} (€{most_valuable['value']:,})",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="age_analysis", description="Display age analysis of all players")
        async def age_analysis(interaction: discord.Interaction):
            players = self.data.load_players()
            
            if not players:
                await interaction.response.send_message("❌ No players found in the database!", ephemeral=True)
                return
            
            # Age group analysis
            age_groups = {
                'Youth (16-21)': [p for p in players if 16 <= p.get('age', 0) <= 21],
                'Prime (22-29)': [p for p in players if 22 <= p.get('age', 0) <= 29],
                'Veteran (30+)': [p for p in players if p.get('age', 0) >= 30]
            }
            
            # Overall stats
            ages = [p.get('age', 0) for p in players if p.get('age', 0) > 0]
            avg_age = sum(ages) / len(ages) if ages else 0
            youngest = min(players, key=lambda x: x.get('age', 100))
            oldest = max(players, key=lambda x: x.get('age', 0))
            
            embed = discord.Embed(
                title="🎂 Age Analysis",
                description="Age distribution and statistics",
                color=0x9932cc
            )
            
            embed.add_field(name="📊 Average Age", value=f"{avg_age:.1f} years", inline=True)
            embed.add_field(name="👶 Youngest Player", value=f"{youngest['name']} ({youngest['age']} years)", inline=True)
            embed.add_field(name="👴 Oldest Player", value=f"{oldest['name']} ({oldest['age']} years)", inline=True)
            
            for group_name, group_players in age_groups.items():
                count = len(group_players)
                if count > 0:
                    avg_value = sum(p.get('value', 0) for p in group_players) / count
                    embed.add_field(
                        name=group_name,
                        value=f"👥 {count} players\n💰 Avg Value: €{avg_value:,.0f}",
                        inline=True
                    )
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="compare_clubs", description="Compare two clubs side by side")
        @app_commands.describe(
            club1_id="ID of the first club",
            club2_id="ID of the second club"
        )
        async def compare_clubs(interaction: discord.Interaction, club1_id: int, club2_id: int):
            clubs = self.data.load_clubs()
            players = self.data.load_players()
            
            club1 = next((c for c in clubs if c['id'] == club1_id), None)
            club2 = next((c for c in clubs if c['id'] == club2_id), None)
            
            if not club1:
                await interaction.response.send_message(f"❌ Club with ID {club1_id} not found!", ephemeral=True)
                return
            
            if not club2:
                await interaction.response.send_message(f"❌ Club with ID {club2_id} not found!", ephemeral=True)
                return
            
            # Get players for each club
            club1_players = [p for p in players if p.get('club_id') == club1_id]
            club2_players = [p for p in players if p.get('club_id') == club2_id]
            
            # Calculate stats
            club1_player_value = sum(p.get('value', 0) for p in club1_players)
            club2_player_value = sum(p.get('value', 0) for p in club2_players)
            
            club1_avg_age = sum(p.get('age', 0) for p in club1_players) / len(club1_players) if club1_players else 0
            club2_avg_age = sum(p.get('age', 0) for p in club2_players) / len(club2_players) if club2_players else 0
            
            embed = discord.Embed(
                title="⚖️ Club Comparison",
                description=f"**{club1['name']}** vs **{club2['name']}**",
                color=0xff6b6b
            )
            
            embed.add_field(
                name=f"🏆 {club1['name']}",
                value=f"💰 Budget: €{club1['budget']:,}\n👥 Players: {len(club1_players)}\n💎 Squad Value: €{club1_player_value:,}\n🎂 Avg Age: {club1_avg_age:.1f}",
                inline=True
            )
            
            embed.add_field(name="⚡", value="**VS**", inline=True)
            
            embed.add_field(
                name=f"🏆 {club2['name']}",
                value=f"💰 Budget: €{club2['budget']:,}\n👥 Players: {len(club2_players)}\n💎 Squad Value: €{club2_player_value:,}\n🎂 Avg Age: {club2_avg_age:.1f}",
                inline=True
            )
            
            # Determine advantages
            advantages = []
            if club1['budget'] > club2['budget']:
                advantages.append(f"💰 {club1['name']} has higher budget")
            elif club2['budget'] > club1['budget']:
                advantages.append(f"💰 {club2['name']} has higher budget")
            
            if club1_player_value > club2_player_value:
                advantages.append(f"💎 {club1['name']} has more valuable squad")
            elif club2_player_value > club1_player_value:
                advantages.append(f"💎 {club2['name']} has more valuable squad")
            
            if len(club1_players) > len(club2_players):
                advantages.append(f"👥 {club1['name']} has larger squad")
            elif len(club2_players) > len(club1_players):
                advantages.append(f"👥 {club2['name']} has larger squad")
            
            if advantages:
                embed.add_field(name="📈 Key Differences", value="\n".join(advantages), inline=False)
            
            await interaction.response.send_message(embed=embed)
