#!/bin/zsh

# This script sets up the environment and runs the Spotify playlist manager.

# IMPORTANT: Add your Spotify API credentials here.
export SPOTIPY_CLIENT_ID="YOUR_CLIENT_ID"
export SPOTIPY_CLIENT_SECRET="YOUR_CLIENT_SECRET"

# Navigate to the script's directory.
# This ensures that it runs in the correct context.
cd "$(dirname "$0")"

# Create a logs directory if it doesn't exist
mkdir -p logs

# Run the Python script using the python3 executable.
# We also redirect the output (stdout and stderr) to a log file.
# This lets you check if the script ran successfully later.
python3 manage_playlist.py >> logs/spotify_update_$(date +%Y%m%d).log 2>&1