import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import pandas as pd
import time
from datetime import datetime



# --- Configuration ---
OWNER_NAME = "YOUR_SPOTIFY_USERNAME"
TARGET_PLAYLIST_NAME = "YOUR_TARGET_PLAYLIST_NAME"
EXCLUDED_PLAYLISTS = [
    "YOUR_EXCLUDED_PLAYLIST_NAME_1",
    "YOUR_EXCLUDED_PLAYLIST_NAME_2",
    "YOUR_EXCLUDED_PLAYLIST_NAME_3",
]


# IMPORTANT: This is the redirect URI that Spotify will redirect to after authentication.
# Use something like http://127.0.0.1:8080/callback for local development.
YOUR_REDIRECT_URI = "http://127.0.0.1:8080/callback"

# add the target playlist to the excluded playlists
EXCLUDED_PLAYLISTS.append(TARGET_PLAYLIST_NAME)

# --- Authentication ---
# This script needs permission to read user playlists and modify public playlists.
client_id = os.environ.get("SPOTIPY_CLIENT_ID")
client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
if not client_id or not client_secret:
    print("Error: Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables.")
    exit()

scope = "playlist-read-private playlist-modify-public"
auth_manager = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=YOUR_REDIRECT_URI,
    scope=scope,
    requests_timeout=20
)
sp = spotipy.Spotify(auth_manager=auth_manager)
user_id = sp.current_user()['id']
# -------------------------


# --------------------

# --- Step 1: Fetch all tracks from source playlists ---
print(f"Fetching all tracks from playlists owned by '{OWNER_NAME}'...")
all_tracks_data = []
source_playlists = sp.user_playlists(user_id)

if source_playlists and source_playlists['items']:
    for playlist in source_playlists['items']:
        if playlist['owner']['display_name'] == OWNER_NAME:
            if playlist['name'] in EXCLUDED_PLAYLISTS:
                print(f"--> Skipping excluded playlist: {playlist['name']}")
                continue

            print(f"--> Processing source playlist: {playlist['name']}")
            results = sp.playlist_items(playlist['id'])
            tracks = results['items']
            while results['next']:
                results = sp.next(results)
                tracks.extend(results['items'])

            for item in tracks:
                track = item['track']
                if track and track['uri']:
                    all_tracks_data.append({
                        'Track Name': track['name'],
                        'Artist(s)': ", ".join([artist['name'] for artist in track['artists']]),
                        'Date Added': item['added_at'],
                        'Spotify URI': track['uri']
                    })

if not all_tracks_data:
    print("No songs found in the source playlists. Exiting.")
    exit()

# Create a master DataFrame of all songs and sort them
master_df = pd.DataFrame(all_tracks_data)
master_df['Date Added'] = pd.to_datetime(master_df['Date Added'])
master_df.sort_values(by='Date Added', ascending=True, inplace=True)
print(f"\nFound a total of {len(master_df)} songs across all source playlists.")

# --- Step 2: Find the target playlist and determine what to add ---
print(f"\nSearching for target playlist: '{TARGET_PLAYLIST_NAME}'...")
target_playlist_id = None
user_playlists = sp.current_user_playlists()
for playlist in user_playlists['items']:
    if playlist['name'] == TARGET_PLAYLIST_NAME:
        target_playlist_id = playlist['id']
        break

songs_to_add_df = pd.DataFrame()

if target_playlist_id:
    print(f"Found existing playlist. Checking for new songs to update...")
    playlist_details = sp.playlist(target_playlist_id)
    track_count = playlist_details['tracks']['total']
    
    if track_count > 0:
        offset = max(0, track_count - 100)
        last_page = sp.playlist_items(target_playlist_id, offset=offset)
        last_track_item = last_page['items'][-1]
        last_song_timestamp = pd.to_datetime(last_track_item['added_at'])
        print(f"Timestamp of last song in playlist: {last_song_timestamp}")
        
        songs_to_add_df = master_df[master_df['Date Added'] > last_song_timestamp]
    else:
        print("Playlist is empty. Will add all songs.")
        songs_to_add_df = master_df
else:
    print(f"Playlist not found. Creating a new playlist named '{TARGET_PLAYLIST_NAME}'...")
    new_playlist = sp.user_playlist_create(
        user=user_id,
        name=TARGET_PLAYLIST_NAME,
        public=True,
        description=f"All songs from {OWNER_NAME}'s playlists, sorted chronologically."
    )
    target_playlist_id = new_playlist['id']
    print(f"Successfully created playlist.")
    songs_to_add_df = master_df

# --- Step 3: Add the necessary songs ---
if songs_to_add_df.empty:
    print("\nNo new songs to add. Your playlist is already up to date!")
    exit()

print(f"\nPreparing to add {len(songs_to_add_df)} new song(s) to the playlist.")
track_uris_to_add = songs_to_add_df['Spotify URI'].tolist()

for i, uri in enumerate(track_uris_to_add):
    track_name = songs_to_add_df.iloc[i]['Track Name']
    print(f"Adding ({i+1}/{len(track_uris_to_add)}): {track_name}")
    sp.playlist_add_items(target_playlist_id, [uri])
    time.sleep(0.5)

print("\nPlaylist management complete!")
print(f"Successfully added {len(track_uris_to_add)} song(s).") 