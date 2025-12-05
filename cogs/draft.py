from cogs.player import Player


class Draft:
    def __init__(
            self,
            name: str,
            rounds: int,
            monthly: float = 0.00000003333,
            change: float | None = None,
            aoty: list | None = [50, 25, 15, 10, 5, -5, -25],
            billboard: list | None = [10, 5, 5, 5, 5, 3],
    ) -> None:
        """
        :param name: The name of the league used in graphics.
        :type name: str
        :param rounds: Number of rounds in the draft.
        :type rounds: int
        :param monthly: How many points monthly listeners will count for per week.
        :type monthly: float
        :param change: How many points will be added as an artists monthly listeners goes up and down.
        :type change: float | None
        :param aoty: How many points will be added for album of the year user scores.
        :type aoty: list | None
        :param billboard: How many points will be scored for the billboard rankings.
        :type billboard: list | None
        """

        self.draft_players: list[str] = []
        """List of player names."""
        self.draft_name: str = name

        # for the draft sequencing
        self.turn: int = 0
        self.direction: int = 1
        self.rounds: int = rounds

        self.all_artists: list[str] = []
        self.drafted_artists: set = set()
        self.starting_listeners: list = None
        self.current_listeners: list = None

        self.monthly: float = monthly
        self.change: float | None = change

        self.aoty_scoring_guide = ["90+", "89-85",
                                   "84-82", "81-79", "78-75", "74-65", "64-"]
        self.aoty_scoring: list[float] = aoty
        """Shows how much an album scores if it is in the a range of aoty user scores. 7 spots in list. 
        [if an album gets a 90+ it will be a this, 89 - 85, 84 - 82, 81 - 79, 78 - 75, 74 - 65, and 64 to the min score]"""

        self.billboard: list[float] = billboard
        """How many points having a song in the top billboard will get you. 
        [#1 -> #100] based on index. Last spot will be used for every spot down the list."""

        self.stage: int = 0
        """0 = draft is unstarted, 1 is draft is started, 2 is draft is completed, 3 is season is started"""

        self.week_in_season: int = 0
        self.draft_update_time: list = []
        """weekday - hour - minute"""

    def new_settings(self,
                     rounds: int | None = None,
                     monthly: float | None = None,
                     change: float | None = None,
                     aoty_range: str | None = None,
                     aoty_score: float | None = None,
                     billboard_score: float | None = None,
                     billboard_spot: int | None = None) -> bool:
        """
        :param rounds: Number of rounds in the draft.
        :type rounds: int
        :param monthly: How many points monthly listeners will count for per week.
        :type monthly: float
        :param change: How many points will be added as an artists monthly listeners goes up and down.
        :type change: float | None
        :param aoty_range: The range the user is changing.
        :type aoty_range: str | None
        :param aoty_score: What the new score will be in the range.
        :type aoty_score: float | None
        :param billboard_score: How many points will be the base for the billboard scoring.
        :type billboard_score: float | None
        :param billboard_spot: What spot is it in the list.
        :type billboard_spot: int | None
        """
        if rounds is not None:
            self.rounds = rounds
        if monthly is not None:
            self.monthly = monthly
        if change is not None:
            self.change = change
        if aoty_range is not None:
            if aoty_score is not None:
                index = self.aoty_scoring_guide.index(aoty_range)
                self.aoty_scoring[index] = aoty_score
        if billboard_score is not None:
            if billboard_spot is not None:
                self.billboard[billboard_spot] = billboard_score

    def get_settings(self) -> list:
        return {
            "rounds": self.rounds,
            "change": self.change,
            "monthly": self.monthly,
            "aoty": self.aoty_scoring,
            "aoty_scoring_guide": self.aoty_scoring_guide,
            "billboard": self.billboard
        }

    def is_stage(self, stage: int | list) -> bool:
        """0 = draft is unstarted, 1 = draft is started, 2 = draft is completed, 3 = season is started, 4 = season is over
        :param stage: takes in a stage and checks if the draft is in the matching stage.
        :type stage: int | list
        :returns: if it is the current draft stage or not.
        :rtype: boolean
        """
        if isinstance(stage, int):
            return self.stage == stage

        try:
            return self.stage in stage
        except TypeError:
            return False

    def get_stage(self,) -> int:
        return self.stage

    def next_stage(self) -> None:
        """Goes to next stage of draft. 0 = draft is unstarted, 1 = draft is started, 2 = draft is completed, 3 = season is started, 4 = season is overd"""
        if self.stage is 3:
            print("Warning: Season is over.")

        if self.stage > 3:
            print("Error: Max stage limit reached.")
            return
        self.stage += 1

    def get_size(self) -> int:
        """
        :returns: The number of players in the draft currently.
        :rtype: int
        """
        return len(self.draft_players)

    def get_name(self):
        return self.draft_name

    def get_all_artists(self):
        return self.all_artists

    def get_turn(self):
        return self.turn

    def get_round(self):
        return self.rounds

    def get_all_players(self):
        return [p for p in self.draft_players if isinstance(p, Player)]

    def get_update_time(self):
        return self.draft_update_time

    def get_week_in_season(self):
        return self.week_in_season

    def set_draft_update_time(self, update_list: list):
        self.draft_update_time = update_list

    def next_turn(self) -> None:
        """Goes to the next player in the draft order"""
        if self.direction == 1:
            if self.turn is len(self.draft_players) - 1:
                self.direction = -1
                self.rounds -= 1
                if self.rounds <= 0:
                    self.next_stage()
                return
            self.turn += self.direction
        else:
            if self.turn == 0:
                self.direction = 1
                self.rounds -= 1
                if self.rounds <= 0:
                    self.next_stage()
                return
            self.turn += self.direction

    def add_new_player(self, id: str, name: str):
        """Adds new player to the draft.
        :param user_id: The player's discord id.
        :type user_id: int
        :param name: The player's discord name.
        :type name: str
        """
        self.draft_players.append(Player(user_id=id, name=name))

    def add_drafted_artists(self, artist_name):
        self.drafted_artists.add(artist_name)

    def set_all_artists(self, artists: list):
        self.all_artists = artists

    def set_starting_listeners(self, listeners: list):
        self.starting_listeners = listeners

    def set_current_listeners(self, listeners: list):
        self.current_listeners = listeners

    def update_weekly_listeners(self, weekly_listener_data):
        artistIndex = {name: i for i,
                       name in enumerate(self.get_all_artists())}

        for player in self.get_all_players():
            weekly_total = 0

            for artist in player.artists:
                player.ensure_artist(artist)

                idx = artistIndex.get(artist, None)
                listeners = weekly_listener_data[idx] if idx is not None else 0

                # log weekly listeners
                player.artist_info[artist]["weekly"].append(listeners)
                weekly_total += listeners

            player.weekly_listeners = weekly_total
            player.total_listeners += weekly_total

    def update_monthly_listeners(self):
        for player in self.get_all_players():

            for artist in player.artists:
                listeners = player.artist_info[artist]["weekly"]
                player.ensure_artist(artist)

                # last 4 weeks = "month"
                recent = listeners[-4:]

                monthly_total = sum(recent)
                player.artist_info[artist]["monthly"].append(monthly_total)

    def update_total_listeners(self):
        for player in self.get_all_players():
            for artist in player.artists:
                listeners = player.artist_info[artist]["weekly"]
                yearly_total = sum(listeners)
                player.artist_info[artist]["yearly_total"] = yearly_total

    def score_all_players(self):
        for player in self.get_all_players():
            return
        return

    def end_season():
        print("End season")
        return
