# Discord Football Bot

## Overview

A comprehensive Discord bot for managing football clubs, players, transfers, and matches. Built with Python and discord.py, the bot provides complete league administration through 15+ slash commands. The system manages virtual football leagues with realistic budget systems, player valuations, transfer mechanics, and automated match scheduling with reminder notifications.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py Library**: Uses discord.py with slash commands for modern Discord interaction
- **Command Structure**: Modular command system organized by functionality (admin, club, player, match, stats)
- **Event-Driven Architecture**: Bot responds to Discord events and scheduled tasks
- **Administrator Permissions**: All administrative commands require Discord administrator permissions

### Data Storage
- **JSON File System**: Uses local JSON files for persistent data storage
- **Data Manager**: Centralized DataManager class handles all file operations
- **Data Categories**: Separate files for clubs, players, matches, and transfers
- **Backup System**: Built-in data backup and reset functionality

### Match Scheduling System
- **Async Scheduler**: Background task system using asyncio for match reminders
- **Automatic Notifications**: 5-minute pre-match reminders sent privately
- **Match States**: Tracks match status (scheduled, live, finished, cancelled)
- **DateTime Management**: Handles match scheduling with proper timezone handling

### Core Domain Models
- **Clubs**: Budget management in Euros, player rosters, statistics tracking, Discord role assignment
- **Players**: Market valuations, positions (GK/DEF/MID/ATT), age tracking, transfer history
- **Transfers**: Budget validation, fee calculations, complete transaction history
- **Matches**: Scheduling between clubs, status tracking, automated reminders with role notifications

### User Interface
- **Discord Embeds**: Rich formatted messages with images and structured data
- **Image Support**: Upload and display club logos and player images
- **Interactive Elements**: Confirmation dialogs for destructive operations
- **Statistics Dashboard**: Comprehensive league analytics and comparisons

### Keep-Alive System
- **Flask Web Server**: Lightweight web server for health monitoring
- **Threading**: Runs web server in separate thread from bot
- **Health Endpoints**: Status and health check endpoints for monitoring
- **Deployment Ready**: Configured for platforms like Render.com

## External Dependencies

### Discord Integration
- **discord.py**: Primary bot framework for Discord API interaction
- **Bot Permissions**: Requires guild, message content, and member intents
- **Slash Commands**: Modern Discord command interface with auto-completion

### Web Framework
- **Flask**: Lightweight web server for keep-alive functionality
- **Template Engine**: HTML templates for status page rendering
- **Threading**: Concurrent web server execution alongside bot

### Data Management
- **JSON**: Native Python JSON library for data persistence
- **File System**: Local file storage for all bot data
- **OS Module**: Environment variable management for configuration

### Async Framework
- **asyncio**: Asynchronous programming for non-blocking operations
- **Background Tasks**: Match scheduling and reminder system
- **Event Loop**: Handles concurrent Discord events and scheduled tasks

### Environment Configuration
- **Environment Variables**: DISCORD_TOKEN and PORT configuration
- **Platform Deployment**: Ready for cloud deployment platforms
- **Debug Support**: Configurable logging and error handling