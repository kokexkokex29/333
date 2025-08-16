# Discord Football Bot

A comprehensive Discord bot for managing football clubs, players, transfers, and matches. Built with Python and discord.py, featuring 15+ slash commands for complete league administration.

## Features

### 🏆 Club Management
- Create and manage football clubs
- Set club budgets in Euros
- Track club statistics and player rosters
- Compare clubs side by side

### ⚽ Player Management
- Add players with detailed information (name, value, position, age)
- Update player values and attributes
- Track player transfers and history
- Position-based statistics (GK, DEF, MID, ATT)

### 🔄 Transfer System
- Transfer players between clubs
- Realistic budget management
- Transfer fee calculations
- Complete transfer history tracking

### 🏟️ Match Scheduling
- Schedule matches between clubs
- Automatic reminder system (5 minutes before matches)
- Match status tracking (scheduled, live, finished, cancelled)
- Private notifications to team representatives

### 📊 Statistics & Analytics
- League-wide statistics
- Top players rankings
- Club comparisons
- Age analysis and position breakdowns
- Transfer activity tracking

### 🛡️ Administrative Controls
- Admin-only command access
- Complete data backup system
- Reset functionality
- Custom embeds with image uploads
- System information and monitoring

## Commands List

### Club Commands
- `/create_club` - Create a new football club
- `/list_clubs` - Display all clubs
- `/club_info` - Get detailed club information
- `/update_club_budget` - Update club budget
- `/delete_club` - Delete a club

### Player Commands
- `/create_player` - Create a new player
- `/list_players` - Display all players or filter by club
- `/player_info` - Get detailed player information
- `/update_player_value` - Update player market value
- `/transfer_player` - Transfer player between clubs
- `/release_player` - Release player to free agency

### Match Commands
- `/create_match` - Schedule a new match
- `/list_matches` - Display scheduled matches
- `/match_info` - Get detailed match information
- `/cancel_match` - Cancel a scheduled match
- `/update_match_status` - Update match status

### Statistics Commands
- `/league_stats` - Display comprehensive league statistics
- `/top_players` - Show top players by value
- `/club_rankings` - Rank clubs by total value
- `/transfer_activity` - Show recent transfers
- `/position_stats` - Statistics by player position
- `/age_analysis` - Age distribution analysis
- `/compare_clubs` - Compare two clubs

### Admin Commands
- `/reset_all` - Reset all data (with confirmation)
- `/backup_data` - Create data backup file
- `/system_info` - Display bot system information
- `/embed_with_image` - Create custom embeds with images
- `/rename_club` - Rename an existing club
- `/rename_player` - Rename an existing player
- `/update_player_age` - Update player age

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Discord Developer Account
- Bot Token from Discord Developer Portal

### Installation

1. **Clone or download the bot files**
2. **Install required packages:**
   ```bash
   pip install discord.py flask
   ```

3. **Set up Discord Bot:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to "Bot" section and create a bot
   - Copy the bot token
   - Enable "Message Content Intent" in bot settings

4. **Set environment variables:**
   ```bash
   export DISCORD_TOKEN="your_bot_token_here"
   export PORT=5000
   