# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any required packages
RUN pip install -r requirements.txt

# Set the environment variable for the bot token
ENV TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN

# Set the environment variable for the PORT
ENV PORT 8080

# Expose port 8080 to the outside world
EXPOSE 8080

# Run the bot
CMD ["python", "bot.py"]