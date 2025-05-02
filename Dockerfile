# Dockerfile
FROM python:3.9-slim

# Install FFmpeg for video conversion
RUN apt-get update && apt-get install -y ffmpeg

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port for Flask
EXPOSE 8443

# Run the bot
CMD ["python", "bot.py"]
