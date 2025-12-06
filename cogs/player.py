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

        # listeners for embeds
        self.total_listeners = 0
        self.weekly_listeners = 0
        self.total_change_listeners = 0

        # total season long scores for all artists
        self.total_listeners_score = 0
        self.total_aoty_score = 0
        self.total_billboard_score = 0
        self.total_change_score = 0
        self.total_score = 0

        # week totals
        self.weekly_listeners_score = 0
        self.weeks_aoty_score = 0
        self.weeks_billboard_score = 0
        self.weeks_change_score = 0
        self.weeks_score = 0

        # month totals
        self.monthly_listeners_score = 0

        # matchup scoring, resets every new matchup
        self.matchup_listeners_score = 0
        self.matchup_aoty_score = 0
        self.matchup_billboard_score = 0
        self.matchup_change_score = 0
        self.matchup_score = 0

        self.record = [0, 0]  # [win, loss]

    def get_artist(self, name: str):
        return self.artist_info.get(name)

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

    def set_artist(self, name: str, location: int):
        if len(self.artists) >= location:
            self.artists[location] = name
