#!/usr/bin/env python3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import csv
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def setup_spotify_client():
    """Set up and return authenticated Spotify client"""
    scope = "user-library-read"
    
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=scope
    )
    
    return spotipy.Spotify(auth_manager=sp_oauth)

def fetch_liked_songs(sp, limit=None):
    """Fetch liked songs from Spotify with rate limiting"""
    songs = []
    offset = 0
    batch_size = 50  # Spotify API max per request
    total_fetched = 0
    
    # Get total number of liked songs
    first_batch = sp.current_user_saved_tracks(limit=1)
    total_songs = first_batch['total']
    
    if limit:
        total_to_fetch = min(limit, total_songs)
    else:
        total_to_fetch = total_songs
    
    print(f"Total liked songs: {total_songs}")
    print(f"Fetching: {total_to_fetch} songs")
    
    while total_fetched < total_to_fetch:
        # Calculate how many to fetch in this batch
        current_batch_size = min(batch_size, total_to_fetch - total_fetched)
        
        try:
            # Fetch batch with rate limiting
            results = sp.current_user_saved_tracks(limit=current_batch_size, offset=offset)
            
            for idx, item in enumerate(results['items']):
                track = item['track']
                if track:  # Sometimes track can be None
                    # Extract release year from album release date
                    release_year = 'Unknown'
                    if track.get('album') and track['album'].get('release_date'):
                        release_date = track['album']['release_date']
                        # Release date can be YYYY, YYYY-MM, or YYYY-MM-DD
                        release_year = release_date.split('-')[0] if release_date else 'Unknown'
                    
                    song_data = {
                        'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown Artist',
                        'song': track['name'],
                        'album': track['album']['name'] if track['album'] else 'Unknown Album',
                        'year': release_year,
                        'added_at': item['added_at']
                    }
                    songs.append(song_data)
            
            total_fetched += len(results['items'])
            offset += current_batch_size
            
            # Progress update
            print(f"Fetched {total_fetched}/{total_to_fetch} songs...")
            
            # Rate limiting: wait 0.1 seconds between requests
            time.sleep(0.1)
            
            # Break if we've reached the end
            if not results['next']:
                break
                
        except spotipy.SpotifyException as e:
            if e.http_status == 429:  # Rate limit exceeded
                retry_after = int(e.headers.get('Retry-After', 5))
                print(f"Rate limit hit. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"Spotify API error: {e}")
                break
        except Exception as e:
            print(f"Error fetching songs: {e}")
            break
    
    return songs

def save_to_csv(songs, filename=None):
    """Save songs to CSV file with artist, song title, album, year, date added"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"spotify_liked_songs_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Artist', 'Song Title', 'Album', 'Year', 'Date Added'])
        
        for song in songs:
            # Format the date added to be more readable
            date_added = song['added_at'].split('T')[0] if 'T' in song['added_at'] else song['added_at']
            writer.writerow([
                song['artist'],
                song['song'],
                song['album'],
                song['year'],
                date_added
            ])
    
    print(f"\nSaved {len(songs)} songs to {filename}")
    return filename

def save_detailed_csv(songs, filename=None):
    """Save songs to detailed CSV file with all fields"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"spotify_liked_songs_detailed_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['artist', 'song', 'album', 'year', 'added_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(songs)
    
    print(f"Saved detailed data to {filename}")
    return filename

def main():
    parser = argparse.ArgumentParser(description='Fetch liked songs from Spotify')
    parser.add_argument('-l', '--limit', type=int, help='Number of songs to fetch (for testing)')
    parser.add_argument('-o', '--output', help='Output CSV filename')
    parser.add_argument('-d', '--detailed', action='store_true', help='Save detailed CSV with additional fields')
    
    args = parser.parse_args()
    
    # Setup Spotify client
    print("Authenticating with Spotify...")
    sp = setup_spotify_client()
    
    try:
        # Test authentication
        user = sp.current_user()
        print(f"Authenticated as: {user['display_name']}")
    except Exception as e:
        print(f"Authentication failed: {e}")
        print("\nMake sure you have:")
        print("1. Created a .env file with your Spotify credentials")
        print("2. Set up a Spotify app at https://developer.spotify.com/dashboard")
        return
    
    # Fetch songs
    print("\nFetching liked songs...")
    songs = fetch_liked_songs(sp, limit=args.limit)
    
    if songs:
        # Save to CSV
        save_to_csv(songs, args.output)
        
        # Optionally save detailed version
        if args.detailed:
            save_detailed_csv(songs)
    else:
        print("No songs fetched.")

if __name__ == "__main__":
    main()