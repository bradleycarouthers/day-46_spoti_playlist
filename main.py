from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import eventlet

CLIENT_ID = "912552eabe074cfd9218c27459aaddf0"
CLIENT_SECRET = "91bdc07d5ecf45268e298038cf4dd060"

traveled_date = input("What date would you like to travel to (YYYY-MM-DD)? ")
response = requests.get(url="https://www.billboard.com/charts/hot-100/" + traveled_date)
response.raise_for_status()

billboard_site = response.text
soup = BeautifulSoup(billboard_site, "html.parser")
span_songs = soup.find_all("span", class_="chart-element__information__song")
song_titles = [song.getText() for song in span_songs]

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()['id']
song_uris = []
year = traveled_date.split("-")[0]
month = traveled_date.split("-")[1]
day = traveled_date.split("-")[2]

for song in song_titles:
    result = sp.search(q=f"track: {song} year: {year}", type="track")

    try:
        eventlet.monkey_patch()
        with eventlet.Timeout(60):
            uri = result["tracks"]['items'][0]['uri']
            song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped")
    except:
        continue

#   Creates playlist
playlist = sp.user_playlist_create(
    user=user_id,
    name=f"{year}-{month}-{day} Billboard 100",
    public=False,
    collaborative=False,
    description="This playlist reflects the billboard top 100 on the given date"
)

#   Adds songs to playlist
sp.playlist_add_items(
    playlist_id=playlist['id'],
    items=song_uris,
    position=None
)
