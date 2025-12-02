class Player:
    def __init__(self, id: int, name: str,):
        """
        :param user_id: The player's discord id.
        :type user_id: int
        :param name: The player's discord name.
        :type name: str
        """
        self.user_id = id
        self.name = name

        self.artists: list = []

        self.artist_scores: dict = {}
        """self.artist_scores = {
            "artist_name": {
                "weekly": [...],      # raw weekly scores
                "monthly": [...],     # rolling monthly totals
                "yearly_total": 0       # accumulated total for the year
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

    def addArtist(self, name):
        self.artists.append(name)

    def set_artist(self, name: str, location: int):
        if len(self.artists) >= location:
            self.artists[location] = name

    def ensure_artist(self, name):
        if name not in self.artist_scores:
            self.artist_scores[name] = {
                "weekly": [],
                "monthly": [],
                "yearly_total": 0
            }
