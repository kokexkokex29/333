import asyncio
import discord
from datetime import datetime, timedelta
from typing import Dict, Any

class MatchScheduler:
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data = data_manager
        self.active_reminders = {}
        self.is_running = False
    
    async def start(self):
        """Start the scheduler background task"""
        if not self.is_running:
            self.is_running = True
            asyncio.create_task(self.scheduler_loop())
            print("Match scheduler started")
    
    async def scheduler_loop(self):
        """Main scheduler loop that runs every minute"""
        while self.is_running:
            try:
                await self.check_match_reminders()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def check_match_reminders(self):
        """Check for matches that need reminders"""
        matches = self.data.load_matches()
        current_time = datetime.now()
        
        for match in matches:
            if match.get('status') != 'scheduled':
                continue
            
            try:
                match_datetime = datetime.fromisoformat(match['datetime'])
                time_diff = match_datetime - current_time
                
                # Send reminder 5 minutes before match
                if (4 * 60 <= time_diff.total_seconds() <= 6 * 60 and 
                    not match.get('reminder_sent', False)):
                    await self.send_match_reminder(match)
                    match['reminder_sent'] = True
                    self.data.save_matches(matches)
            
            except Exception as e:
                print(f"Error processing match {match.get('id', 'unknown')}: {e}")
    
    async def send_match_reminder(self, match: Dict[Any, Any]):
        """Send match reminder notifications"""
        try:
            clubs = self.data.load_clubs()
            club1 = next((c for c in clubs if c['id'] == match['club1_id']), None)
            club2 = next((c for c in clubs if c['id'] == match['club2_id']), None)
            
            if not club1 or not club2:
                return
            
            match_datetime = datetime.fromisoformat(match['datetime'])
            
            # Create reminder embed
            embed = discord.Embed(
                title="⚠️ Match Reminder",
                description=f"**{club1['name']}** vs **{club2['name']}**",
                color=0xff9900
            )
            
            embed.add_field(name="⏰ Starting In", value="5 minutes", inline=True)
            embed.add_field(name="📅 Time", value=match_datetime.strftime("%H:%M"), inline=True)
            embed.add_field(name="🆔 Match ID", value=match['id'], inline=True)
            
            embed.add_field(name="🏆 Teams", value=f"{club1['name']} vs {club2['name']}", inline=False)
            embed.set_footer(text="Good luck to both teams!")
            
            # Send to all channels where the bot has permission
            # In a real implementation, you'd want to configure specific channels
            for guild in self.bot.guilds:
                try:
                    # Find a channel to send the reminder
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            await channel.send(embed=embed)
                            break
                except Exception as e:
                    print(f"Error sending reminder to guild {guild.id}: {e}")
            
            print(f"Match reminder sent for match {match['id']}")
            
        except Exception as e:
            print(f"Error sending match reminder: {e}")
    
    async def schedule_match_reminder(self, match: Dict[Any, Any]):
        """Schedule a specific match reminder"""
        try:
            match_datetime = datetime.fromisoformat(match['datetime'])
            reminder_time = match_datetime - timedelta(minutes=5)
            current_time = datetime.now()
            
            if reminder_time > current_time:
                delay = (reminder_time - current_time).total_seconds()
                
                # Store the reminder task
                task = asyncio.create_task(self._delayed_reminder(delay, match))
                self.active_reminders[match['id']] = task
                
                print(f"Scheduled reminder for match {match['id']} in {delay} seconds")
        
        except Exception as e:
            print(f"Error scheduling match reminder: {e}")
    
    async def _delayed_reminder(self, delay: float, match: Dict[Any, Any]):
        """Execute a delayed reminder"""
        try:
            await asyncio.sleep(delay)
            await self.send_match_reminder(match)
            
            # Update match data to mark reminder as sent
            matches = self.data.load_matches()
            for m in matches:
                if m['id'] == match['id']:
                    m['reminder_sent'] = True
                    break
            self.data.save_matches(matches)
            
            # Remove from active reminders
            if match['id'] in self.active_reminders:
                del self.active_reminders[match['id']]
        
        except asyncio.CancelledError:
            print(f"Reminder cancelled for match {match['id']}")
        except Exception as e:
            print(f"Error in delayed reminder: {e}")
    
    def cancel_match_reminder(self, match_id: int):
        """Cancel a scheduled match reminder"""
        if match_id in self.active_reminders:
            self.active_reminders[match_id].cancel()
            del self.active_reminders[match_id]
            print(f"Cancelled reminder for match {match_id}")
    
    async def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        
        # Cancel all active reminders
        for task in self.active_reminders.values():
            task.cancel()
        self.active_reminders.clear()
        
        print("Match scheduler stopped")
