from flask import Flask, render_template, redirect, request, session, make_response, url_for
import spotipy
from spotipy import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import requests, json, pickle, random
from secret import *

app = Flask(__name__, static_url_path='/static')
app.secret_key = app_secret


API_BASE = 'https://accounts.spotify.com'
REDIRECT = 'https://catch-ify.herokuapp.com/api_callback'
# REDIRECT = 'http://localhost:5000/api_callback'
SCOPE = 'user-top-read'
SHOW_DIALOG = False

# authorization-code-flow Step 1. Have your application request authorization; 
# the user logs in and authorizes access
@app.route("/")
def verify():
    auth_url = f'{API_BASE}/authorize?client_id={CID}&response_type=code&redirect_uri={REDIRECT}&scope={SCOPE}&show_dialog={SHOW_DIALOG}'
    print(auth_url)
    return redirect(auth_url)

# authorization-code-flow Step 2.
# Have your application request refresh and access tokens;
# Spotify returns access and refresh tokens
@app.route("/api_callback")
def api_callback():
    session.clear()
    code = request.args.get('code')

    auth_token_url = f"{API_BASE}/api/token"
    res = requests.post(auth_token_url, data={
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":"https://catch-ify.herokuapp.com/api_callback",
        # "redirect_uri":"http://localhost:5000/api_callback",
        "client_id":CID,
        "client_secret":SECRET
        })

    res_body = res.json()
    print(res.json())
    session["toke"] = res_body.get("access_token")

    return redirect("index")


@app.route('/index/')    
def index():
    return render_template('index.html')

@app.route('/more/', methods=['GET','POST'])
def more():
    sp = spotipy.Spotify(auth=session['toke'])
    top_artists = sp.current_user_top_artists(limit= 10, offset= 0, time_range='medium_term')
    artist_list = []
    total_tracks = 10
    artist_list = []
    song_list = []
    seed = []

# Code to get playlist image
#     playlist = sp.playlist("https://open.spotify.com/playlist/09l51K6fpy1loJlp8QJ68Q?si=57ff8bc5a0964044")
#     cover1 = playlist['images'][0]['url']
#     print(cover1)

    x = 0
    while len(artist_list) <= 4:
        for x in range(10):
            artist_id = top_artists['items'][x]['id']
            related = sp.artist_related_artists(artist_id)

            for j in range(3):
                artist = related['artists'][j]
                artist_add = [artist['id']]

                if len(artist_list) > 4:
                    break
                if artist_add[0] not in artist_list and artist_add[0] not in top_artists:
                    artist_list.append(artist_add[0])

    artist1 = sp.artist(artist_list[0])
    artist1_img = artist1["images"][0]["url"]
    artist1_name = artist1['name']
    artist1_link = artist1['external_urls']['spotify']

    artist2 = sp.artist(artist_list[1])
    artist2_img = artist2["images"][0]["url"]
    artist2_name = artist2['name']
    artist2_link = artist2['external_urls']['spotify']

    artist3 = sp.artist(artist_list[2])
    artist3_img = artist3["images"][0]["url"]
    artist3_name = artist3['name']
    artist3_link = artist3['external_urls']['spotify']

    artist4 = sp.artist(artist_list[3])
    artist4_img = artist4["images"][0]["url"]
    artist4_name = artist4['name']
    artist4_link = artist4['external_urls']['spotify']

    artist5 = sp.artist(artist_list[4])
    artist5_img = artist5["images"][0]["url"]
    artist5_name = artist5['name']
    artist5_link = artist5['external_urls']['spotify']
   
    if request.method == "POST":
        if (request.form.get("isRandom")) == "True":
            seed = sp.recommendation_genre_seeds()['genres']
            seeds = []
            for x in range(5):
                seeds.append(seed[random.randint(0,20)])

            print(seeds)
            recommend_list = sp.recommendations(seed_artists=None, seed_genres=seeds, seed_tracks=None, limit=10, country="CA")
            print(recommend_list)
            for h in range(10):
                this_song_track = [recommend_list['tracks'][h]]
                song_list += this_song_track

    if request.method == "POST":
        varNext = "Next"
        if (request.form.get("isRandom")) == "False":
            global index
            index = int(request.form.get("index"))
            with open("test.txt", "rb") as fp:   # Unpickling
                song_list = pickle.load(fp)
            length = len(song_list)

            if index == length - 1:
                varNext = "Home"

            if index > length - 1:
                return redirect(url_for('index'))
        # User opens results for first time
        else:
            index = 0
            with open("test.txt", "wb") as fp:   #Pickling
                pickle.dump(song_list, fp)
        # Show song data for this song
        print(song_list)
        recommend = song_list[index]
        image = recommend['album']['images'][0]['url']
        artist = recommend['album']['artists'][0]['name']
        name = recommend['name']
        preview = recommend['preview_url']  
        link = recommend['external_urls']['spotify']
        length = len(song_list)

        index += 1
        return render_template("results.html", song_list = song_list, image = image, artist = artist, name = name, preview = preview, index = index, link = link, length = length, varNext = varNext)


    return render_template('more.html', artist1_img = artist1_img, artist1_name = artist1_name, artist1_link = artist1_link, artist2_img = artist2_img, artist2_name = artist2_name, artist2_link = artist2_link, artist3_img = artist3_img, artist3_name = artist3_name, artist3_link = artist3_link, artist4_img = artist4_img, artist4_name = artist4_name, artist4_link = artist4_link, artist5_img = artist5_img, artist5_name = artist5_name, artist5_link = artist5_link)

@app.route('/results/', methods=['GET','POST'])
def results():
    difference = 0.1
    total_tracks = 10
    artist_list = []
    song_list = []

    sp = spotipy.Spotify(auth=session['toke'])
    top_tracks = sp.current_user_top_tracks(limit=total_tracks, offset=0, time_range='medium_term')
    top_artists = sp.current_user_top_artists(limit= 5, offset= 0, time_range='medium_term')

    score_total = 0
    i = 0

    if request.method == "POST":
        if (request.form.get("isOption")) == "True":
            if (request.form.get("optionButton")) == "Danceability":
                option = "danceability"
            if (request.form.get("optionButton")) == "Energy":
                option = "energy"
            if (request.form.get("optionButton")) == "Mood":
                option = "valence"
            if (request.form.get("optionButton")) == "Tempo":
                option = "tempo"
                difference = 20
            if (request.form.get("optionButton")) == "Don't Care":
                option = "dc"
            
            if option != "dc":
                for tracks in top_tracks:
                    while i < total_tracks:
                        track_id = top_tracks['items'][i]['id']
                        option_score = sp.audio_features(track_id)[0][option]
                        score_total += option_score
                        i += 1
                score_total /= total_tracks
                score_total = round(score_total, 3)  

            x = 0
            while x < 5:
                artist_id = top_artists['items'][x]['id']
                related = sp.artist_related_artists(artist_id)
                for j in range(3):
                    artist = related['artists'][j]
                    artist_add = [artist['id']]
                    
                    if artist_add[0] not in artist_list and artist_add[0] not in related:
                        artist_list += artist_add
                x += 1
                
            artist_length = len(artist_list)
            for s in range(artist_length):
                song = (artist_list[s])
                songs = sp.artist_top_tracks(song)
                # Prevent 5 songs from same artist
                add_counter = 0
                len_songs = len(songs['tracks'])
                if len_songs >= 5:
                    len_songs = 5

                if option == "dc":
                    for h in range(len_songs):
                        this_song = [songs['tracks'][h]['id']]
                        this_song_track = [songs['tracks'][h]]
                        if this_song_track[0] not in song_list and add_counter < 1 and len(song_list) < 10:
                            song_list += this_song_track
                            add_counter += 1
                else:
                    for h in range(len_songs):
                        this_song = [songs['tracks'][h]['id']]
                        this_song_track = [songs['tracks'][h]]
                        this_score = sp.audio_features(this_song)[0][option]
                        # check song dance score and only add if its above dance score avg
                        if abs(this_score - score_total) < difference:
                            if this_song_track[0] not in song_list and add_counter < 1 and len(song_list) < 10:
                                song_list += this_song_track
                                add_counter += 1
            
            length = len(song_list)

        if (request.form.get("isOption")) == "False":
            option = (request.form.get("option"))

    # Next Button
    if request.method == "POST":
        varNext = "Next"
        if (request.form.get("isOption")) == "False":
            global index
            index = int(request.form.get("index"))
            with open("test.txt", "rb") as fp:   # Unpickling
                song_list = pickle.load(fp)
            length = len(song_list)

            if index == length - 1:
                varNext = "Home"

            if index > length - 1:
                return redirect(url_for('index'))
        # User opens results for first time
        else:
            index = 0
            with open("test.txt", "wb") as fp:   #Pickling
                pickle.dump(song_list, fp)
    
    # Show song data for this song
    recommend = song_list[index]
    image = recommend['album']['images'][0]['url']
    artist = recommend['album']['artists'][0]['name']
    name = recommend['name']
    preview = recommend['preview_url']
    link = recommend['external_urls']['spotify']

    index += 1
    return render_template("results.html", song_list = song_list, recommend = recommend, image = image, artist = artist, name = name, preview = preview, index = index, option = option, length = length, link = link, varNext = varNext)

@app.route('/genres/', methods=['GET','POST'])
def genres():
    difference = 0.1
    total_tracks = 10
    artist_list = []
    song_list = []
    seed = []
    sp = spotipy.Spotify(auth=session['toke'])
    
    if request.method == "POST":
        if (request.form.get("isGenre")) == "True":
            if (request.form.get("genreButton")) == "Rap":
                seed = ["spotify:artist:4r63FhuTkUYltbVAg5TQnk","spotify:artist:5f7VJjfbwm532GiveGC0ZK", "spotify:artist:46SHBwWsqBkxI7EeeBEQG7", "spotify:artist:6oMuImdp5ZcFhWP0ESe6mG"]
            if (request.form.get("genreButton")) == "Pop":
                seed = ["spotify:artist:1uNFoZAHBGtllmzznpCI3s", "spotify:artist:6M2wZ9GZgrQXHCFfjv46we", "spotify:artist:7tYKF4w9nC0nq9CsPZTHyP", "spotify:artist:66CXWjxzNUsdJxJ2JdwvnR", "spotify:artist:4nDoRrQiYLoBzwC5BhVJzF"]
            if (request.form.get("genreButton")) == "Lo-Fi":
                seed = ["spotify:album:2GVJP6iEMAeVVbh6wpWqhl", "spotify:artist:0liH4Jfiz66Rqjz4DH3JZk", "spotify:artist:0HCAzT0cSCpiNje7AcAQaD", "spotify:artist:4iHB5bp1wwN5qTbVPaBykO"]
            if (request.form.get("genreButton")) == "Dubstep":
                seed = ["spotify:artist:5he5w2lnU9x7JFhnwcekXX", "spotify:artist:4Pn0zmbERg32YIOjl2nOQf", "spotify:artist:32IXja3Y6CPvnAtTHD2bWg", "spotify:artist:07OF36h5y4S6s9ckQliaj3"]
            if (request.form.get("genreButton")) == "K-Pop":
                seed = ["spotify:artist:3Nrfpe0tUJi4K4DXYWgMUX", "spotify:artist:7n2Ycct7Beij7Dj7meI4X0", "spotify:artist:41MozSoPIsD1dJM0CLPjZF", "spotify:artist:1z4g3DjTBBZKhvAroFlhOM"]
            if (request.form.get("genreButton")) == "Classical":
                seed = ["spotify:artist:2wOqMjp9TyABvtHdOSOTUS", "spotify:artist:5aIqB5nVVvmFsvSdExz408", "spotify:artist:2uFUBdaVGtyMqckSeCl0Qj", "spotify:artist:4NJhFmfw43RLBLjQvxDuRS"]
            if (request.form.get("genreButton")) == "R&B":
                seed = ["spotify:artist:2EMAnMvWE2eb56ToJVfCWs", "spotify:artist:7bWXoXVgDSWw6lWZD4fCb6", "spotify:artist:1W7FNibLa0O0b572tB2w7t", "spotify:artist:2joIhhX3Feq47H4QXVDOr3"]
            if (request.form.get("genreButton")) == "Kids":
                seed = ["spotify:artist:5ZiVNVZ2yPcn7SsdMISFHa", "spotify:artist:7CdGfkCRgPhElnqy3HPJ4a", "spotify:artist:1qKLikeNYpQFSsDAjg7HpI", "spotify:artist:2TCyfTG9UWaZYgbg0bmFmG"]
            if (request.form.get("genreButton")) == "Chill":
                seed = ["spotify:artist:7e1ICztHM2Sc4JNLxeMXYl", "spotify:artist:7cSbcJTJBBSXDjRNR2qD61", "spotify:artist:3ycxRkcZ67ALN3GQJ57Vig", "spotify:artist:2FwDTncULUnmANIh7qKa5z"]
            if (request.form.get("genreButton")) == "Blues":
                seed = ["spotify:artist:7EynH3keqfKUmauyaeZoxv", "spotify:artist:5xLSa7l4IV1gsQfhAMvl0U", "spotify:artist:5v8WPpMk60cqZbuZLdXjKY", "spotify:artist:48nwxUvPJZkm8uPa7xMzmj"]
            if (request.form.get("genreButton")) == "Jazz":
                seed = ["spotify:artist:0fTHKjepK5HWOrb2rkS5Em", "spotify:artist:4DuZTASH5eSyd0K73W6fuZ", "spotify:artist:2EsmKkHsXK0WMNGOtIhbxr", "spotify:artist:04gDigrS5kc9YWfZHwBETP"]
            if (request.form.get("genreButton")) == "Rock-n-Roll":
                seed = ["spotify:artist:711MCceyCBcFnzjGY4Q7Un","spotify:artist:3qm84nBOXUEQ2vnTfUTTFC","spotify:artist:4opTS86dN9uO313J9CE8xg","spotify:artist:1dfeR4HaWDbWqFHLkxsg1d"]
            
            recommend_list = sp.recommendations(seed_artists=seed, seed_genres=None, seed_tracks=None, limit=10, country="CA")
            for h in range(10):
                this_song_track = [recommend_list['tracks'][h]]
                song_list += this_song_track
        
    if request.method == "POST":
        varNext = "Next"
        if (request.form.get("isGenre")) == "False":
            global index
            index = int(request.form.get("index"))
            with open("test.txt", "rb") as fp:   # Unpickling
                song_list = pickle.load(fp)
            length = len(song_list)

            if index == length - 1:
                varNext = "Home"

            if index > length - 1:
                return redirect(url_for('index'))
        # User opens results for first time
        else:
            index = 0
            with open("test.txt", "wb") as fp:   #Pickling
                pickle.dump(song_list, fp)
    # Show song data for this song
    recommend = song_list[index]
    image = recommend['album']['images'][0]['url']
    artist = recommend['album']['artists'][0]['name']
    name = recommend['name']
    preview = recommend['preview_url']  
    link = recommend['external_urls']['spotify']
    length = len(song_list)

    index += 1
    return render_template("results.html", song_list = song_list, image = image, artist = artist, name = name, preview = preview, index = index, link = link, length = length, varNext = varNext)

if __name__ == "__main__":
    app.secret_key = app_secret
    app.run(debug=True)
