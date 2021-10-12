from dotenv import load_dotenv, find_dotenv
import requests, os, random

load_dotenv(find_dotenv()) # Loads API keys
spotify_id = os.getenv("SPOTIFY_ID")
spotify_secret = os.getenv("SPOTIFY_SECRET")

auth_url="https://accounts.spotify.com/api/token" 
artist_url="https://api.spotify.com/v1/artists/"
search_url="https://api.spotify.com/v1/search"


def get_token():
    '''Gets access token'''
    auth = requests.post(auth_url,
        {
            'grant_type' : 'client_credentials',
            'client_id' : spotify_id,
            'client_secret' : spotify_secret,
        }
    )
    auth_json=auth.json()
    auth_token = auth_json["access_token"] # authorization token
    return auth_token
headers = {
    'Authorization': f'Bearer {get_token()}'
} # header for all requests
def update_token():
    '''Updates access token'''
    global headers 
    headers = {
        'Authorization': f'Bearer {get_token()}'
    }
def get_song(songs):
    '''
    Returns a random song from the list of top songs.     
    '''
    song = songs[random.randint(0,len(songs)-1)]
    
    #Sets null preview to Never going to give you up
    if not song["preview"]:
        song["preview"] = "https://p.scdn.co/mp3-preview/22bf10aff02db272f0a053dff5c0063d729df988?cid=0205bae2d141422e989258f24b431c8c"
    return song
    

def get_songs(artist):
    '''
    Returns a list of top songs given an artist
    '''
    while(True): 
        song_response = requests.get(
            artist_url+artist+"/top-tracks"+"?market=US",
            headers=headers,
        ).json()
        if "error" in song_response: #updates access token
            update_token()
        else:
            break
    songs = []
    for track in song_response["tracks"]:#For each track
        songs.append(
            {"name":track["name"],
            "id":track["id"],
            "preview":track["preview_url"],
            "image":track["album"]["images"][0]["url"],
            },
        )
    return songs
    
def get_artist(artist_name):
    '''
    Returns an artist id and name given an artist name
    '''
    data={
        "q":artist_name,
        "type":"artist",
        "market":"US"
    }
    while(True):
        response_json=requests.get(
            search_url,
            data,
            headers=headers,
        ).json()
        if "error" in response_json: #updates access token
            update_token()
        else:
            break
    if response_json["artists"]["items"] == []:#if no match for artist query
        return "0gxyHStUsqpMadRV0Di1Qt","Rick Astley"
    else:
        artist=response_json["artists"]["items"][0]
        artist_id = artist["id"]
        name = artist["name"]
        return artist_id,name
