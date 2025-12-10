
def add_artists(dictionary, name, test_number: int):
    dictionary[name] = {
        # general artist info
        "albums_on_record": ["WEWE", "WWWe"],
        "id_aoty": test_number,
        "picked": True,

        # listeners information
        "starting_listeners": None,
        "weekly": [],
        "matchup_listeners": test_number,
        "yearly_listeners_total": test_number,

        # listeners score
        "weekly_listeners_score": test_number,
        "matchup_listeners_score": test_number,
        "total_listeners_score": test_number,

        # album score information
        "new_album_score": test_number,
        "new_album_name": "",

        # album score
        "week_album_score": test_number,
        "matchup_album_score": test_number,
        "total_album_score": test_number,

        # billboard score information
        "songs_on_billboard": [],

        # billboard scores
        "week_billboard_score": test_number,
        "matchup_billboard_score": test_number,
        "total_billboard_score": test_number,

        # change scores information
        "week_listeners_change": test_number,

        # change scores
        "week_score_change": test_number,
        "matchup_change_score": test_number,
        "total_score_change": test_number,

        # year long artist scores
        "week_total_score": test_number,
        "matchup_total_score": test_number,
        "year_total_score": test_number
    }


p1_artists = {}
add_artists(p1_artists, "kys", 88)
add_artists(p1_artists, "cool", 3)
add_artists(p1_artists, "ponster", 91)
p2_artists = {}
add_artists(p2_artists, "john", 10)
add_artists(p2_artists, "nice", 170)
add_artists(p2_artists, "wew", 7)

# print(p1_artists)
# print(p2_artists)


def swap_artists(player_1: dict, player_2: dict, artist_1, artist_2):
    player_1[artist_2] = player_2.pop(artist_2)
    player_2[artist_1] = player_1.pop(artist_1)
    print(player_1)
    print(f"\n\n")
    print(player_2)
    return None


swap_artists(p1_artists, p2_artists, "cool", "john")

# print(p1_artists)
# print(p2_artists)
