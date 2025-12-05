from cogs.scraper import get_artist_id, get_all_artist_albums


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

        self.artist_info: dict = {}
        """self.artist_scores = {
            "artist_name": {
                "weekly": [...],      # raw weekly scores
                "monthly": [...],     # rolling monthly totals
                "yearly_total": 0       # accumulated total for the year
                "id_aoty": get_artist_id(name.lower()),
                "albums_on_record": get_all_artist_albums(),
                "picked": True
            }
        """

        self.total_listeners = 0
        self.weekly_listeners = 0

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

    def get_id(self):
        return self.user_id

    def draft_artist(self, name: str):
        self.artists.append(name)
        id = get_artist_id(name.lower())
        self.artist_info[name] = {
            "weekly": [],
            "monthly": [],
            "yearly_total": 0,
            "id_aoty": id,
            "albums_on_record": get_all_artist_albums(id),
            "picked": True
        }

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
