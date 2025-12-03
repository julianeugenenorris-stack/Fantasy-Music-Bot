from cogs.scraper import get_artist_id


class Player:
    def __init__(self, user_id: int, name: str,):
        """
        :param user_id: The player's discord id.
        :type user_id: int
        :param name: The player's discord name.
        :type name: str
        """
        self.user_id = user_id
        self.name = name

        self.artists: list = []

        self.artist_scores: dict = {}
        """self.artist_scores = {
            "artist_name": {
                "weekly": [...],      # raw weekly scores
                "monthly": [...],     # rolling monthly totals
                "yearly_total": 0       # accumulated total for the year
                "id": get_artist_id(name)
            }
        """

        self.total_score = 0
        self.weekly_score = 0

    def get_artists_scores(self):
        return self.artist_scores

    def get_all_artists(self):
        return self.artists

    def get_total_score(self):
        return self.total_score

    def get_weekly_score(self):
        return self.weekly_score

    def get_id(self):
        return self.user_id

    def draft_artist(self, name: str):
        self.artists.append(name)
        self.artist_scores[name] = {
            "weekly": [],
            "monthly": [],
            "yearly_total": 0,
            "id_aoty": get_artist_id(name.lower())
        }
        print(self.artist_scores)

    def set_artist(self, name: str, location: int):
        if len(self.artists) >= location:
            self.artists[location] = name

    def ensure_artist(self, name):
        if name not in self.artist_scores:
            self.artist_scores[name] = {
                "weekly": [],
                "monthly": [],
                "yearly_total": 0,
                "id_aoty": get_artist_id(name.lower())
            }
