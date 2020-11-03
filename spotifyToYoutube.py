import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import sys
import urllib
import youtube
import os

# Opening our JSON configuration file (which has our tokens).
with open(os.path.split(os.path.abspath(__file__))[0] + '/' + 'config.json', encoding='utf-8-sig') as json_file:
    APIs = json.load(json_file)


def getTracks(playlistURL):
    # Creating and authenticating our Spotify app.
    client_credentials_manager = SpotifyClientCredentials(APIs['spotify']['client_id'],
                                                          APIs['spotify']['client_secret'])
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Getting a playlist type
    playlist_type = playlistURL[::-1]
    playlist_type = playlist_type[playlist_type.index('/') + 1:playlist_type.index('moc.') - 1][::-1]

    # Getting a playlist.
    if playlist_type == 'album':
        results = spotify.album_tracks(album_id=playlistURL)
    elif playlist_type == 'track':
        results = {'items': [spotify.track(track_id=playlistURL)]}
    elif playlist_type == 'playlist':
        results = spotify.user_playlist_tracks(playlist_id=playlistURL)
    else:
        return None

    trackList = []
    # For each track in the playlist.
    for i in results['items']:
        # In case there's only one artist.
        if playlist_type == 'playlist':
            i = i['track']
        if len(i['artists']) == 1:
            # We add trackName - artist.
            trackList.append(i['name'] + ' - ' + i['artists'][0]['name'])
        # In case there's more than one artist.
        else:
            nameString = ''
            # For each artist in the track.
            for index, b in enumerate(i['artists']):
                nameString += (b['name'])
                # If it isn't the last artist.
                if len(i['artists']) - 1 != index:
                    nameString += ', '
            # Adding the track to the list.
            trackList.append(i['name'] + ' - ' + nameString)

    return trackList


def searchYoutubeAlternative(songName):
    # YouTube will block you if you query too many songs using this search.
    textToSearch = songName
    query = urllib.parse.quote(textToSearch)
    url = 'https://www.youtube.com/results?search_query=' + query
    response = str(requests.get(url).content)
    start_scope = 'videoId'
    response = response[response.index(start_scope) + len(start_scope) + 3:]
    response = response[0: response.index('"')]
    return 'https://www.youtube.com/watch?v=' + response


def searchYoutube(songName):
    try:
        api = youtube.API(client_id=APIs['youtube']['client_id'],
                          client_secret=APIs['youtube']['client_secret'],
                          api_key=APIs['youtube']['api_key'])
        video = api.get('search', q=songName, maxResults=1, type='video', order='relevance')
        return 'https://www.youtube.com/watch?v=' + video['items'][0]['id']['videoId']
    except youtube.exceptions.YouTubeException:
        return searchYoutubeAlternative(songName)


if __name__ == '__main__':
    if '-t' in sys.argv:
        spotify_url = sys.argv[sys.argv.index('-t') + 1]
    else:
        spotify_url = str(input('Insert Spotify playlist / album / track URL: '))
    tracks = getTracks(spotify_url)
    songs = [searchYoutube(track) for track in tracks]
    for song in songs:
        print(song)
