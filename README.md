# Spotify Playlist Manager

This project contains a set of scripts to automatically create and update a Spotify using the Spotify API (python's spotipy library) playlist based on the most recently added tracks from a user's other playlists.

📁 spotify-chronological-playlist-builder
├── 📄 README.md
├── 📄 manage_playlist.py
└── 📄 run_daily_update.sh
├── 📄 requirements.txt
└── 📄 .gitignore


## How It Works

The main script, `manage_playlist.py`, connects to the Spotify API and:
1.  Fetches all tracks from the playlists owned by a specified user.
2.  Filters out any tracks from a defined exclusion list.
3.  Searches for a target playlist (e.g., "User's Last Added Songs").
4.  If the playlist exists, it checks for the last song added and only adds newer tracks.
5.  If the playlist doesn't exist, it creates it and adds all the found tracks.
6.  Songs are always added chronologically by their "added at" date.

The `run_daily_update.sh` script is a helper designed to be run by a cron job to automate this process daily.

## Setup and Configuration

### 1. Installation

This project uses Python and requires `spotipy` and `pandas`. Install them from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Spotify API Credentials

You need to get API credentials from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/):
- Create an app.
- Note your **Client ID** and **Client Secret**.
- Go to "Edit Settings" in your app and add a **Redirect URI**. For this project, you could add something like `http://127.0.0.1:8080/callback`. If "8080" is already in use, you could use another port not used by any other application like "8081".

### 3. Load the API credentials
Add your Spotify API credentials to the terminal:
```bash
export SPOTIPY_CLIENT_ID="YOUR_CLIENT_ID"
export SPOTIPY_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

### 4. Configure the Python Script
Open `spotify-chronological-playlist-builder/manage_playlist.py` and review the settings in the **Configuration** section to ensure they match your needs. This includes the owner name, target playlist name, and excluded playlists.

#### 4.1 OWNER_NAME
The owner name is the Spotify username of the user whose playlists you want to use.
```python
OWNER_NAME = "YOUR_SPOTIFY_USERNAME"
```

#### 4.2 TARGET_PLAYLIST_NAME
The target playlist name is the name of the playlist you want to create.
```python
TARGET_PLAYLIST_NAME = "YOUR_TARGET_PLAYLIST_NAME"
```

#### 4.3 EXCLUDED_PLAYLISTS
The excluded playlists are the playlists you want to exclude from the target playlist.
```python
EXCLUDED_PLAYLISTS = [
    "YOUR_EXCLUDED_PLAYLIST_NAME_1",
    "YOUR_EXCLUDED_PLAYLIST_NAME_2",
    "YOUR_EXCLUDED_PLAYLIST_NAME_3",
]
```

#### 4.4 YOUR_REDIRECT_URI
The redirect URI is the URL that Spotify will redirect to after authentication.
```python
YOUR_REDIRECT_URI = "http://127.0.0.1:8080/callback"
```


### 5. Run the Script for the first time

Execute the script:
```bash
python3 manage_playlist.py
```

You will be redirected to a Spotify login page and will be asked to grant the necessary permissions. This happens only once.
Afterwards, your target playlist will be created and the songs will be added to it. 

### 6. Run the Script for updating the playlist

You can execute the same script as above to update the playlist. All new songs will be added to the target playlist. You don't need to login again.





------------------------------

### 7. Automation with Cron (macOS/Linux)

To run the manager script once for testing:
```bash
# Make the helper script executable
chmod +x spotify-chronological-playlist-builder/run_daily_update.sh

# Run the script
./spotify-chronological-playlist-builder/run_daily_update.sh
```
Check the `logs/` directory to see the output.

To run the script automatically every day at 8 AM:

1.  Open your crontab editor: `crontab -e`
2. If you are in vim, press `i` to enter insert mode.
3.  Add the following line, making sure to use the absolute path to your `run_daily_update.sh` script:
    ```
    0 8 * * * /path/to/your/project/spotify-chronological-playlist-builder/run_daily_update.sh
    ```
4. a) If you're in vim, press Esc, then type :wq and press Enter.
    b) If you're in nano, press Ctrl+O to save, then Ctrl+X to exit.
5.  Save and close the editor.
6.  Check if the cron job is working by running `crontab -l`.
