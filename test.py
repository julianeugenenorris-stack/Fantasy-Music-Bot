import billboard

chart = billboard.ChartData('hot-100')

billboard_artists = []
billboard_songs = []
special_artists = ["the Creator"]
for entry in chart[0:]:
    title = entry.title
    artist: str = entry.artist

    if artist.split(", ") in special_artists:
        artist.remove(",")

    artist_replace: str = artist.replace(" & ", ", ").replace(" And ", ", ")

    artist_split_1: str = artist_replace.split(":")[0]
    artist_split_2: str = artist_split_1.split(" Featuring ")[0]
    artist_split_3: str = artist_split_2.split(" With ")[0]
    artist_split_4: str = artist_split_3.split(" Feat. ")[0]
    artist_split_5: str = artist_split_4.split(" Feat ")[0]

    artists: list = artist_split_5.split(", ")
    billboard_artists.append(artists)
    billboard_songs.append(title)

for count, title in enumerate(billboard_songs):
    print(f"Title: {title}, Artists: {billboard_artists[count]}")
