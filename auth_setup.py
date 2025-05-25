#!/usr/bin/env python3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

def setup_spotify_auth():
    """Set up Spotify authentication and return authenticated client"""
    scope = "user-library-read"
    
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=scope
    )
    
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    
    # Test authentication
    try:
        user = sp.current_user()
        print(f"Successfully authenticated as: {user['display_name']}")
        return sp
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

if __name__ == "__main__":
    setup_spotify_auth()