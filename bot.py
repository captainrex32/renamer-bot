# bot.py
import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from flask import Flask
from threading import Thread
import subprocess
import requests
from io import BytesIO

# Initialize Flask app for Render to ping
app = Flask(__name__)

# Bot states for conversation (used for rename and convert processes)
NEW_NAME, CONVERT_FILE = range(2)

# Get bot token from environment variable (set in Render)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telegram.Bot(token=BOT_TOKEN)

# Welcome message when user starts the bot
def start(update, context):
    update.message.reply_text(
        "Hi! I can rename files/videos or convert files to video format. Use /rename to rename a file, /convert to convert a file to video, or /help for more info."
    )

# Help message to guide users
def help_command(update, context):
    update.message.reply_text(
        "Use /rename to rename a file or video.\nUse /convert to convert a file to video format (e.g., image to MP4).\nSend a file after the command."
    )

# Start renaming process
def rename(update, context):
    update.message.reply_text("Please send the file or video you want to rename.")
    return NEW_NAME

# Receive file for renaming
def receive_file_for_rename(update, context):
    if update.message.document or update.message.video or update.message.photo:
        update.message.reply_text("Please send the new name for the file (e.g., newname.mp4).")
        if update.message.document:
            context.user_data['file_id'] = update.message.document.file_id
            context.user_data['file_type'] = 'document'
        elif update.message.video:
            context.user_data['file_id'] = update.message.video.file_id
            context.user_data['file_type'] = 'video'
        elif update.message.photo:
            context.user_data['file_id'] = update.message.photo[-1].file_id
            context.user_data['file_type'] = 'photo'
        return NEW_NAME
    else:
        update.message.reply_text("Please send a valid file or video.")
        return ConversationHandler.END

# Rename the file and send it back
def rename_file(update, context):
    new_name = update.message.text
    file_id = context.user_data.get('file_id')
    file_type = context.user_data.get('file_type')
    
    # Ensure the new name has a valid extension
    if not new_name.endswith(('.mp4', '.jpg', '.png', '.pdf', '.docx')):
        update.message.reply_text("Please include a valid file extension (e.g., newname.mp4).")
        return ConversationHandler.END

    # Download the file
    file = bot.get_file(file_id)
    file_url = file.file_path
    file_data = requests.get(file_url).content
    
    # Save temporarily
    temp_file = "temp_file"
    with open(temp_file, 'wb') as f:
        f.write_data(file_data)
    
    # Rename and send back
    new_file_path = new_name
    os.rename(temp_file, new_file_path)
    
    with open(new_file_path, 'rb') as f:
        if file_type == 'video':
            update.message.reply_video(video=f, filename=new_name)
        else:
            update.message.reply_document(document=f, filename=new_name)
    
    # Clean up
    os.remove(new_file_path)
    update.message.reply_text(f"File renamed to {new_name} and sent back!")
    return ConversationHandler.END

# Start conversion process
def convert(update, context):
    update.message.reply_text("Please send the file you want to convert to video (e.g., image or audio).")
    return CONVERT_FILE

# Convert file to video
def convert_file_to_video(update, context):
    if update.message.document or update.message.photo or update.message.audio:
        file_id = update.message.document.file_id if update.message.document else update.message.photo[-1].file_id if update.message.photo else update.message.audio.file_id
        file_type = 'document' if update.message.document else 'photo' if update.message.photo else 'audio'
        
        # Download the file
        file = bot.get_file(file_id)
        file_url = file.file_path
        file_data = requests.get(file_url).content
        
        # Save temporarily
        temp_file = "input_file"
        with open(temp_file, 'wb') as f:
            f.write_data)
        
        # Convert to video using FFmpeg
        output_file = "output.mp4"
        if file_type == 'photo':
            # Convert image to 30-second video
            command = f"ffmpeg -loop 1 -i {temp_file} -c:v libx264 -t 30 -pix_fmt yuv420p {output_file}"
        elif file_type == 'audio':
            # Convert audio to video with black background
            command = f"ffmpeg -i {temp_file} -c:a aac -c:v libx264 -f mp4 -s 640x480 -t 30 {output_file}"
        else:
            update.message.reply_text("Unsupported file type for conversion.")
            os.remove(temp_file)
            return ConversationHandler.END
        
        try:
            subprocess.run(command, shell=True, check=True)
            with open(output_file, 'rb') as f:
                update.message.reply_video(video=f, filename="converted_video.mp4")
            update.message.reply_text("File converted to video and sent back!")
        except subprocess.CalledProcessError:
            update.message.reply_text("Error converting file. Please try again.")
        
        # Clean up
        os.remove(temp_file)
        if os.path.exists(output_file):
            os.remove(output_file)
        return ConversationHandler.END
    else:
        update.message.reply_text("Please send a valid file (image or audio).")
        return ConversationHandler.END

# Cancel operation
def cancel(update, context):
    update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# Flask route to keep Render happy
@app.route('/')
def home():
    return "Bot is running!"

# Run Flask in a separate thread
def run_flask():
    # Use Render's PORT or default to 8443 (Telegram-compatible port)
    port = int(os.environ.get('PORT', 8443))
    app.run(host='0.0.0.0', port=port, debug=False)

# Main bot function
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Set up conversation handler for renaming
    rename_conv = ConversationHandler(
        entry_points=[CommandHandler('rename', rename)],
        states={
            NEW_NAME: [MessageHandler(Filters.document | Filters.video | Filters.photo, receive_file_for_rename),
                       MessageHandler(Filters.text & ~Filters.command, rename_file)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Set up conversation handler for converting
    convert_conv = ConversationHandler(
        entry_points=[CommandHandler('convert', convert)],
        states={
            CONVERT_FILE: [MessageHandler(Filters.document | Filters.photo | Filters.audio, convert_file_to_video)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Add handlers to dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(rename_conv)
    dp.add_handler(convert_conv)

    # Start Flask in a thread
    Thread(target=run_flask).start()

    # Start polling (simpler than webhooks)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
