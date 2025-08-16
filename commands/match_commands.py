import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import asyncio

class MatchCommands:
    def __init__(self, bot, data_manager, scheduler):
        self.bot = bot
        self.data = data_manager
        self.scheduler = scheduler
        self.setup_commands()
    
    def setup_commands(self):
        """Setup all match-related slash commands"""
        
        @self.bot.tree.command(name="create_match", description="Schedule a new match between two clubs")
        @app_commands.describe(
            club1_id="ID of the first club",
            club2_id="ID of the second club",
            year="Year of the match",
            month="Month of the match (1-12)",
            day="Day of the match",
            hour="Hour of the match (0-23)",
            minute="Minute of the match (0-59)"
        )
        async def create_match(interaction: discord.Interaction, club1_id: int, club2_id: int, year: int, month: int, day: int, hour: int, minute: int):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            clubs = self.data.load_clubs()
            matches = self.data.load_matches()
            
            # Validate clubs
            club1 = next((c for c in clubs if c['id'] == club1_id), None)
            club2 = next((c for c in clubs if c['id'] == club2_id), None)
            
            if not club1:
                await interaction.response.send_message(f"❌ Club with ID {club1_id} not found!", ephemeral=True)
                return
            
            if not club2:
                await interaction.response.send_message(f"❌ Club with ID {club2_id} not found!", ephemeral=True)
                return
            
            if club1_id == club2_id:
                await interaction.response.send_message("❌ A club cannot play against itself!", ephemeral=True)
                return
            
            # Validate date
            try:
                match_datetime = datetime(year, month, day, hour, minute)
                if match_datetime <= datetime.now():
                    await interaction.response.send_message("❌ Match date must be in the future!", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("❌ Invalid date/time provided!", ephemeral=True)
                return
            
            # Create match
            match_data = {
                'id': len(matches) + 1,
                'club1_id': club1_id,
                'club2_id': club2_id,
                'datetime': match_datetime.isoformat(),
                'status': 'scheduled',
                'created_by': interaction.user.id,
                'notified': False,
                'reminder_sent': False
            }
            
            matches.append(match_data)
            self.data.save_matches(matches)
            
            # Schedule reminder
            await self.scheduler.schedule_match_reminder(match_data)
            
            # Create embed response
            embed = discord.Embed(
                title="⚽ Match Scheduled!",
                description=f"**{club1['name']}** vs **{club2['name']}**",
                color=0x00ff00
            )
            
            embed.add_field(name="🏆 Home Team", value=club1['name'], inline=True)
            embed.add_field(name="🏆 Away Team", value=club2['name'], inline=True)
            embed.add_field(name="🆔 Match ID", value=match_data['id'], inline=True)
            
            embed.add_field(name="📅 Date", value=match_datetime.strftime("%B %d, %Y"), inline=True)
            embed.add_field(name="⏰ Time", value=match_datetime.strftime("%H:%M"), inline=True)
            embed.add_field(name="📢 Status", value="Scheduled", inline=True)
            
            embed.set_footer(text=f"Match created by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            
            # Send private messages to club representatives (if they have a role/member assigned)
            try:
                # This is a simplified approach - in a real bot, you'd want to have a system
                # to associate clubs with Discord users/roles
                await self.send_match_notification(interaction, club1, club2, match_datetime, match_data['id'])
            except Exception as e:
                print(f"Error sending match notifications: {e}")
        
        @self.bot.tree.command(name="list_matches", description="Display all scheduled matches")
        @app_commands.describe(status="Filter by match status (optional)")
        async def list_matches(interaction: discord.Interaction, status: str = None):
            matches = self.data.load_matches()
            clubs = self.data.load_clubs()
            
            if status:
                matches = [m for m in matches if m.get('status', '').lower() == status.lower()]
            
            if not matches:
                embed = discord.Embed(
                    title="⚽ Scheduled Matches",
                    description="No matches found!",
                    color=0xff9900
                )
                await interaction.response.send_message(embed=embed)
                return
            
            # Sort matches by date
            matches.sort(key=lambda x: x.get('datetime', ''))
            
            embed = discord.Embed(
                title="⚽ Scheduled Matches",
                description=f"Total matches: {len(matches)}",
                color=0x0099ff
            )
            
            for match in matches[:10]:  # Show next 10 matches
                club1 = next((c for c in clubs if c['id'] == match['club1_id']), {'name': 'Unknown'})
                club2 = next((c for c in clubs if c['id'] == match['club2_id']), {'name': 'Unknown'})
                
                try:
                    match_dt = datetime.fromisoformat(match['datetime'])
                    date_str = match_dt.strftime("%b %d, %Y at %H:%M")
                except:
                    date_str = "Invalid date"
                
                embed.add_field(
                    name=f"Match {match['id']}: {club1['name']} vs {club2['name']}",
                    value=f"📅 {date_str}\n📢 Status: {match.get('status', 'Unknown').title()}",
                    inline=False
                )
            
            if len(matches) > 10:
                embed.set_footer(text=f"Showing next 10 of {len(matches)} matches")
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="match_info", description="Get detailed information about a specific match")
        @app_commands.describe(match_id="ID of the match to view")
        async def match_info(interaction: discord.Interaction, match_id: int):
            matches = self.data.load_matches()
            clubs = self.data.load_clubs()
            
            match = next((m for m in matches if m['id'] == match_id), None)
            if not match:
                await interaction.response.send_message(f"❌ Match with ID {match_id} not found!", ephemeral=True)
                return
            
            club1 = next((c for c in clubs if c['id'] == match['club1_id']), {'name': 'Unknown Club'})
            club2 = next((c for c in clubs if c['id'] == match['club2_id']), {'name': 'Unknown Club'})
            
            try:
                match_dt = datetime.fromisoformat(match['datetime'])
                date_str = match_dt.strftime("%B %d, %Y")
                time_str = match_dt.strftime("%H:%M")
                
                # Calculate time until match
                time_diff = match_dt - datetime.now()
                if time_diff.total_seconds() > 0:
                    days = time_diff.days
                    hours, remainder = divmod(time_diff.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    time_until = f"{days}d {hours}h {minutes}m"
                else:
                    time_until = "Match time has passed"
            except:
                date_str = "Invalid date"
                time_str = "Invalid time"
                time_until = "Unknown"
            
            embed = discord.Embed(
                title=f"⚽ Match {match_id}",
                description=f"**{club1['name']}** vs **{club2['name']}**",
                color=0x0099ff
            )
            
            embed.add_field(name="🏆 Home Team", value=club1['name'], inline=True)
            embed.add_field(name="🏆 Away Team", value=club2['name'], inline=True)
            embed.add_field(name="📢 Status", value=match.get('status', 'Unknown').title(), inline=True)
            
            embed.add_field(name="📅 Date", value=date_str, inline=True)
            embed.add_field(name="⏰ Time", value=time_str, inline=True)
            embed.add_field(name="⏳ Time Until Match", value=time_until, inline=True)
            
            embed.add_field(name="🔔 Notifications", value="Sent" if match.get('notified') else "Pending", inline=True)
            embed.add_field(name="⏰ Reminder", value="Sent" if match.get('reminder_sent') else "Pending", inline=True)
            
            creator = self.bot.get_user(match.get('created_by'))
            if creator:
                embed.set_footer(text=f"Match created by {creator.display_name}")
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="cancel_match", description="Cancel a scheduled match")
        @app_commands.describe(match_id="ID of the match to cancel")
        async def cancel_match(interaction: discord.Interaction, match_id: int):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            matches = self.data.load_matches()
            clubs = self.data.load_clubs()
            
            match = next((m for m in matches if m['id'] == match_id), None)
            if not match:
                await interaction.response.send_message(f"❌ Match with ID {match_id} not found!", ephemeral=True)
                return
            
            if match.get('status') == 'cancelled':
                await interaction.response.send_message(f"❌ Match {match_id} is already cancelled!", ephemeral=True)
                return
            
            # Update match status
            match['status'] = 'cancelled'
            self.data.save_matches(matches)
            
            club1 = next((c for c in clubs if c['id'] == match['club1_id']), {'name': 'Unknown Club'})
            club2 = next((c for c in clubs if c['id'] == match['club2_id']), {'name': 'Unknown Club'})
            
            embed = discord.Embed(
                title="❌ Match Cancelled",
                description=f"**{club1['name']}** vs **{club2['name']}** has been cancelled!",
                color=0xff0000
            )
            embed.add_field(name="Match ID", value=match_id, inline=True)
            embed.add_field(name="Cancelled by", value=interaction.user.display_name, inline=True)
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="update_match_status", description="Update the status of a match")
        @app_commands.describe(
            match_id="ID of the match",
            new_status="New status (scheduled, live, finished, cancelled)"
        )
        async def update_match_status(interaction: discord.Interaction, match_id: int, new_status: str):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Only administrators can use this command!", ephemeral=True)
                return
            
            valid_statuses = ['scheduled', 'live', 'finished', 'cancelled']
            if new_status.lower() not in valid_statuses:
                await interaction.response.send_message(f"❌ Invalid status! Use: {', '.join(valid_statuses)}", ephemeral=True)
                return
            
            matches = self.data.load_matches()
            clubs = self.data.load_clubs()
            
            match = next((m for m in matches if m['id'] == match_id), None)
            if not match:
                await interaction.response.send_message(f"❌ Match with ID {match_id} not found!", ephemeral=True)
                return
            
            old_status = match.get('status', 'unknown')
            match['status'] = new_status.lower()
            self.data.save_matches(matches)
            
            club1 = next((c for c in clubs if c['id'] == match['club1_id']), {'name': 'Unknown Club'})
            club2 = next((c for c in clubs if c['id'] == match['club2_id']), {'name': 'Unknown Club'})
            
            embed = discord.Embed(
                title="📢 Match Status Updated",
                description=f"**{club1['name']}** vs **{club2['name']}**",
                color=0x00ff00
            )
            embed.add_field(name="Match ID", value=match_id, inline=True)
            embed.add_field(name="Old Status", value=old_status.title(), inline=True)
            embed.add_field(name="New Status", value=new_status.title(), inline=True)
            
            await interaction.response.send_message(embed=embed)
    
    async def send_match_notification(self, interaction, club1, club2, match_datetime, match_id):
        """Send private match notifications to club role members"""
        try:
            guild = interaction.guild
            if not guild:
                return
            
            # Create notification message text
            match_message = f"""
⚽ **New Match Scheduled!**

🏆 **Teams:** {club1['name']} vs {club2['name']}
📅 **Date:** {match_datetime.strftime("%B %d, %Y")}
⏰ **Time:** {match_datetime.strftime("%H:%M")}
🆔 **Match ID:** {match_id}

🔥 Good luck to both teams!
            """.strip()
            
            sent_to_members = 0
            
            # Send private messages to club1 role members
            if club1.get('role_id'):
                role1 = guild.get_role(club1['role_id'])
                if role1 and role1.members:
                    for member in role1.members:
                        try:
                            await member.send(f"🏆 **{club1['name']}** - Match Notification\n\n{match_message}")
                            sent_to_members += 1
                        except discord.Forbidden:
                            # User has DMs disabled
                            continue
                        except Exception as e:
                            print(f"Error sending DM to {member.display_name}: {e}")
                            continue
            
            # Send private messages to club2 role members
            if club2.get('role_id'):
                role2 = guild.get_role(club2['role_id'])
                if role2 and role2.members:
                    for member in role2.members:
                        try:
                            await member.send(f"🏆 **{club2['name']}** - Match Notification\n\n{match_message}")
                            sent_to_members += 1
                        except discord.Forbidden:
                            # User has DMs disabled
                            continue
                        except Exception as e:
                            print(f"Error sending DM to {member.display_name}: {e}")
                            continue
            
            # Send confirmation message to admin
            if sent_to_members > 0:
                await interaction.followup.send(f"✅ Match notifications sent to {sent_to_members} members via DM!", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ No notifications sent (clubs without roles or members have DMs disabled)", ephemeral=True)
            
        except Exception as e:
            print(f"Error sending match notifications: {e}")
