import os
import asyncio
from bot import DiscordBot
from keep_alive import keep_alive

def main():
    """Main entry point for the bot application"""
    # Start the keep-alive web server
    keep_alive()
    
    # Get Discord token from environment variables
    token = os.getenv('DISCORD_TOKEN', 'your_discord_bot_token_here')
    
    if token == 'your_discord_bot_token_here':
        print("WARNING: Please set DISCORD_TOKEN environment variable")
    
    # Create and run the bot
    bot = DiscordBot()
    
    try:
        # Run the bot
        asyncio.run(bot.run(token))
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot encountered an error: {e}")

if __name__ == "__main__":
    main()
