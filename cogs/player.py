from cogs.scraper import get_artist_id, get_all_artist_albums


class Player:
    def __init__(self, user_id: int, user_name: str, team_name: str = None):
        """
        :param user_id: The player's discord id.
        :type user_id: int
        :param name: The player's discord name.
        :type name: str
        """
        self.user_id = user_id
        self.name = user_name
        self.team_name = team_name

        self.artists: list = []

        self.artist_info: dict = {}
        """self.artist_scores = {
            "artist_name": {
                "weekly": [...],      # raw weekly scores
                "monthly": [...],     # rolling monthly totals
                "yearly_total": 0       # accumulated total for the year
                "id_aoty": get_artist_id(name.lower()),
                "albums_on_record": get_all_artist_albums(),
                "picked": True,         # selected in draft
                "new_album_aoty_score": 0,
                "new_album_score": 0,
                "total_billboard_score": 0,     # total artist listeners score
                "week_billboard_score": 0,      # points from billboard last update
                "songs_on_billboard": [...],    # songs on billboard last update
                "starting_listeners": None,     # listeners at start of season or when picked up
                "total_score_change": 0         # all weeks change score
            }
        """

        self.total_listeners = 0
        self.weekly_listeners = 0

        self.total_change_listeners = 0

        # total season long scores for all artists
        self.total_listeners_score = 0
        self.weekly_listeners_score = 0
        self.monthly_listeners_score = 0
        self.aoty_score = 0
        self.billboard_score = 0
        self.change_score = 0

        # matchup scoring, resets every new matchup
        self.matchup_total_score = 0

        self.record = [0, 0]  # [win, loss]

    def get_artists_information(self):
        return self.artist_info

    def get_all_artists(self):
        return self.artists

    def get_artist(self, name: str):
        return self.artist_info.get(name)

    def get_total_listeners(self):
        return self.total_listeners

    def get_weekly_listeners(self):
        return self.weekly_listeners

    def get_aoty_score(self):
        return self.aoty_score

    def get_id(self):
        return self.user_id

    def get_weekly_listeners_score(self):
        return self.weekly_listeners_score

    def get_change_score(self):
        return self.change_score

    def get_billboard_score(self):
        return self.billboard_score

    def add_change_score(self, score: float):
        self.change_score += score

    def set_total_change_listeners(self, score):
        self.total_change_listeners = score

    def set_weekly_listeners_score(self, score: float):
        self.weekly_listeners_score = score

    def set_monthly_listeners_score(self, score: float):
        self.monthly_listeners_score = score

    def add_total_listeners_score(self, weekly_score_total: float):
        self.total_listeners_score += weekly_score_total

    def add_aoty_score(self, score: int):
        self.aoty_score += score

    def draft_artist(self, name: str):
        self.artists.append(name)
        id = get_artist_id(name.lower())
        self.artist_info[name] = {
            "albums_on_record": get_all_artist_albums(id),
            "starting_listeners": None,
            "weekly": [],
            "monthly": [],
            "weekly_score": 0,
            "monthly_score": 0,
            "yearly_total": 0,
            "id_aoty": id,
            "picked": True,
            "new_album_aoty_score": 0,
            "new_album_score": 0,
            "new_album_name": "",
            "total_billboard_score": 0,
            "week_billboard_score": 0,
            "songs_on_billboard": [],
            "score_change": 0,
            "listeners_change": 0,
            "week_total_score": 0
        }

    def set_billboard_score(self, score: int):
        self.billboard_score = score

    def set_artist(self, name: str, location: int):
        if len(self.artists) >= location:
            self.artists[location] = name

    def ensure_artist(self, name):
        if name not in self.artist_info:
            id = get_artist_id(name.lower())
            self.artist_info[name] = {
                "weekly": [],
                "monthly": [],
                "yearly_total": 0,
                "id_aoty": id,
                "albums_on_record": get_all_artist_albums(id),
                "picked": True
            }
