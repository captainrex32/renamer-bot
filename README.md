# Telegram File Renamer and Converter Bot

This is a Telegram bot that renames files or videos and converts images or audio files to video format (MP4). It’s hosted on Render’s free web service.

## What It Does
- *Rename Files/Videos*: Send /rename, upload a file (e.g., MP4, JPG, PDF), and type a new name (e.g., newname.mp4). The bot sends back the renamed file.
- *Convert to Video*: Send /convert, upload an image (e.g., JPG) or audio (e.g., MP3), and get an MP4 video (e.g., a 30-second loop for images).
- *Help*: Send /help for instructions.

## How to Use
1. Open Telegram and search for the bot (e.g., @MyFileRenamerBot).
2. Send /start to begin.
3. Use /rename or /convert and follow the bot’s prompts.
4. Files must be under 50MB (Telegram’s limit).

## Setup
- The bot is built with Python, Flask, and FFmpeg.
- It’s deployed on Render using a Docker setup.
- Files in this repository:
  - bot.py: The main bot program.
  - requirements.txt: Lists the tools needed.
  - Dockerfile: Sets up the bot on Render.
  - README.md: This file.

## Notes
- Hosted on Render’s free tier, so it may sleep when not in use.
- Contact the owner for issues or to get the bot’s Telegram username.
