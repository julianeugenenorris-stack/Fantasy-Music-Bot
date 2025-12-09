from cogs.scraper import get_artist_id, get_all_artist_albums


class Player:
    def __init__(self, user, user_id: int, user_name: str, team_name: str = None):
        """
        :param user_id: The player's discord id.
        :type user_id: int
        :param name: The player's discord name.
        :type name: str
        """
        self.user_id = user_id
        self.name = user_name
        self.team_name = team_name
        self.user_image = user.display_avatar.url

        self.artists: list = []

        self.artist_info: dict = {}
        """self.artist_scores = {
            "artist_name": {
                "weekly": [...],      # raw weekly scores
                }
        """

        # listeners for embeds
        self.total_listeners = 0
        self.matchup_listeners = 0
        self.weekly_listeners = 0
        self.weekly_change_listeners = 0

        # total season long scores for all artists
        self.total_listeners_score = 0
        self.total_aoty_score = 0
        self.total_billboard_score = 0
        self.total_change_score = 0
        self.total_score = 0

        # week totals
        self.weeks_listener_score = 0
        self.weeks_aoty_score = 0
        self.weeks_billboard_score = 0
        self.weeks_change_score = 0
        self.weeks_score = 0

        # matchup scoring, resets every new matchup
        self.matchup_listeners_score = 0
        self.matchup_aoty_score = 0
        self.matchup_billboard_score = 0
        self.matchup_change_score = 0
        self.matchup_score = 0

        self.record = [0, 0]  # [win, loss]

    def get_artist(self, name: str):
        return self.artist_info.get(name)

    def record_add_win(self):
        current_wins = self.record[0]
        current_losses = self.record[1]
        self.record = [current_wins+1, current_losses]

    def record_add_loss(self):
        current_wins = self.record[0]
        current_losses = self.record[1]
        self.record = [current_wins, current_losses+1]

    def reset_matchup(self):
        self.matchup_listeners_score = 0
        self.matchup_aoty_score = 0
        self.matchup_billboard_score = 0
        self.matchup_change_score = 0
        self.matchup_score = 0
        self.matchup_listeners = 0
        for artist in self.artists:
            info = self.artist_info.get(artist)
            info["matchup_listeners_score"] = 0
            info["matchup_album_score"] = 0
            info["matchup_change_score"] = 0
            info["matchup_total_score"] = 0
            info["matchup_billboard_score"] = 0

    def draft_artist(self, name: str):
        self.artists.append(name)
        id = get_artist_id(name.lower())
        self.artist_info[name] = {
            # general artist info
            "albums_on_record": get_all_artist_albums(id),
            "id_aoty": id,
            "picked": True,

            # listeners information
            "starting_listeners": None,
            "weekly": [],
            "matchup": [],
            "yearly_listeners_total": 0,

            # listeners score
            "weekly_listeners_score": 0,
            "matchup_listeners_score": 0,
            "total_listeners_score": 0,

            # album score information
            "new_album_score": 0,
            "new_album_name": "",

            # album score
            "week_album_score": 0,
            "matchup_album_score": 0,
            "total_album_score": 0,

            # billboard score information
            "songs_on_billboard": [],

            # billboard scores
            "week_billboard_score": 0,
            "matchup_billboard_score": 0,
            "total_billboard_score": 0,

            # change scores information
            "week_listeners_change": 0,

            # change scores
            "week_score_change": 0,
            "matchup_change_score": 0,
            "total_score_change": 0,

            # year long artist scores
            "week_total_score": 0,
            "matchup_total_score": 0,
            "year_total_score": 0
        }

    def set_artist(self, name: str, location: int):
        if len(self.artists) >= location:
            self.artists[location] = name
