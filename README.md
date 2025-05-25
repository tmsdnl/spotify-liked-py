# Spotify Liked Songs Fetcher

A Python script to fetch all your liked songs from Spotify and export them to CSV format.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a Spotify App:**
   - Go to https://developer.spotify.com/dashboard
   - Click "Create app"
   - Set the Redirect URI to: `http://127.0.0.1:8080/callback`
   - Save your Client ID and Client Secret

3. **Configure credentials:**
   - Copy `.env.example` to `.env`
   - Add your Spotify Client ID and Client Secret

## Usage

### Basic usage (fetch all liked songs):
```bash
python fetch_liked_songs.py
```

### Fetch a limited number of songs (for testing):
```bash
python fetch_liked_songs.py -l 10
```

### Specify output filename:
```bash
python fetch_liked_songs.py -o my_songs.csv
```

### Save detailed CSV with album and date info:
```bash
python fetch_liked_songs.py -d
```

### Combine options:
```bash
python fetch_liked_songs.py -l 50 -o test_songs.csv -d
```

## Output Format

The default CSV format is simple:
```
artist: song
The Beatles: Hey Jude
Queen: Bohemian Rhapsody
```

The detailed format includes:
- Artist
- Song
- Album
- Date added

## Rate Limiting

The script includes built-in rate limiting:
- 0.1 second delay between requests
- Automatic retry with backoff on rate limit errors
- Respects Spotify's Retry-After header

## First Time Setup

On first run, you'll be redirected to Spotify to authorize the app. After authorization, the script will save a token for future use.