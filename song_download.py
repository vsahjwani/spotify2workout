import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
from time import sleep
from dotenv import load_dotenv
import os

load_dotenv()

if not os.getenv("CLIENT_ID") or not os.getenv("CLIENT_SECRET"):
    raise ValueError("Spotify credentials not found in .env!")

# STEP 1: AUTHENTICATE PROPERLY
client_id = os.getenv('CLIENT_ID')  # Double-check these in Spotify Dashboard
client_secret = os.getenv('CLIENT_SECRET')  # Ensure they're correct

# Configure with increased timeout and automatic retry
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

sp = spotipy.Spotify(
    auth_manager=auth_manager,
    requests_timeout=15,
    retries=10,
    status_retries=10,
    status_forcelist=[429, 500, 502, 503, 504]
)

# STEP 2: Define list of artists
artists = ["Lady Gaga", "Daft Punk", "Beyoncé"]

# STEP 3: IMPROVED function with market parameter and better error handling
def get_top_danceable_songs(artist_name):
    try:
        # Search for artist with market specification
        results = sp.search(q=f"artist:{artist_name}", type='artist', limit=1, market='US')
        items = results['artists']['items']
        if not items:
            print(f"Artist not found: {artist_name}")
            return []
        artist_id = items[0]['id']

        # Get top tracks WITH EXPLICIT MARKET PARAMETER
        top_tracks = sp.artist_top_tracks(artist_id, country='US')['tracks']
        if not top_tracks:
            print(f"No tracks found for {artist_name} in US market")
            return []
            
        track_ids = [track['id'] for track in top_tracks if track.get('id')]

        # Process audio features in smaller chunks with longer delays
        chunk_size = 5  # Reduced chunk size to minimize request size
        audio_features = []
        
        for i in range(0, len(track_ids), chunk_size):
            chunk = track_ids[i:i + chunk_size]
            if not chunk:
                continue

            max_retries = 5  # Increased retry attempts
            for attempt in range(max_retries):
                try:
                    features = sp.audio_features(chunk)
                    if features and None not in features:
                        audio_features.extend(features)
                        break
                    else:
                        print(f"Partial features received for {artist_name}, attempt {attempt + 1}")
                        time.sleep(2 ** attempt)  # Exponential backoff
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for {artist_name}: {str(e)}")
                    time.sleep(2 ** attempt + 5)  # Longer delay between attempts
            else:
                print(f"Failed to get features for {artist_name} after {max_retries} attempts")
                return []

        # Safely combine data with length check
        dance_data = []
        min_length = min(len(top_tracks), len(audio_features))
        for i in range(min_length):
            track = top_tracks[i]
            features = audio_features[i]
            if features and 'danceability' in features:
                dance_data.append({
                    "track_name": track["name"],
                    "danceability": features["danceability"],
                    "artist": artist_name,
                    "preview_url": track["preview_url"],
                    "spotify_url": track["external_urls"]["spotify"]
                })

        # Return sorted results
        return sorted(dance_data, key=lambda x: x["danceability"], reverse=True)[:5]

    except Exception as e:
        print(f"Critical error processing {artist_name}: {str(e)}")
        return []

# STEP 4: Process artists with rate limit protection
all_data = {}
for index, artist in enumerate(artists):
    print(f"Processing {index + 1}/{len(artists)}: {artist}")
    all_data[artist] = get_top_danceable_songs(artist)
    
    # Rate limit protection between artists
    if index < len(artists) - 1:
        sleep(5)  # 5-second cooldown between artists

# STEP 5: Save results
with open("top_danceable_songs.json", "w") as f:
    json.dump(all_data, f, indent=4, ensure_ascii=False)

print("Successfully saved danceability data!")