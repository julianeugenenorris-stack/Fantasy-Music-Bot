from cogs.player import Player


class Draft:
    def __init__(
            self,
            name: str,
            rounds: int,
            monthly: float = 0.00000003333,
            change: float | None = None,
            aoty: float | None = None,
            aoty_cutoff: float | None = None,
            billboard: float | None = None,
            billboard_multiplier: int | None = None,
            billboard_top: int | None = None
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
        :type aoty: float | None
        :param aoty: How many points will be added for album of the year user scores.
        :type aoty: float | None
        :param billboard: How many points will be the base for the billboard scoring.
        :type billboard: float | None
        :param billboard_multiplier: The multiplier for each billboard spot up the list.
        :type billboard_multiplier: int | None
        :param billboard_top: To what postition to give points. (5 = top 5 artists get points)
        :type billboard_top: int | None
        """

        self.draft_players: list[str] = []
        """List of player names."""
        self.draft_name: str = name

        # for the draft sequencing
        self.turn: int = 0
        self.direction: int = 1
        self.rounds: int = rounds

        self.starting_listeners: list = None
        self.current_listeners: list = None

        self.monthly: float = monthly
        self.change: float | None = change
        self.aoty: float | None = aoty
        self.aoty_cutoff: float | None = aoty_cutoff
        self.billboard: float | None = billboard
        self.billboard_multiplier: int | None = billboard_multiplier
        self.billboard_top: int | None = billboard_top

        self.all_artists: list[str] = []

        self.stage: int = 0
        """0 = draft is unstarted, 1 is draft is started, 2 is draft is completed, 3 is season is started"""

        self.draftUpdateTime: list[int] = []
        """weekday - hour - minute"""

    def new_settings(self,
                     rounds: int | None = None,
                     monthly: float | None = None,
                     change: float | None = None,
                     aoty: float | None = None,
                     aoty_cutoff: float | None = None,
                     billboard: float | None = None,
                     billboard_multiplier: int | None = None,
                     billboard_top: int | None = None) -> bool:
        """
        :param rounds: Number of rounds in the draft.
        :type rounds: int
        :param monthly: How many points monthly listeners will count for per week.
        :type monthly: float
        :param change: How many points will be added as an artists monthly listeners goes up and down.
        :type change: float | None
        :param aoty: How many points will be added for album of the year user scores.
        :type aoty: float | None
        :param aoty: How many points will be added for album of the year user scores.
        :type aoty: float | None
        :param billboard: How many points will be the base for the billboard scoring.
        :type billboard: float | None
        :param billboard_multiplier: The multiplier for each billboard spot up the list.
        :type billboard_multiplier: int | None
        :param billboard_top: To what postition to give points. (5 = top 5 artists get points)
        :type billboard_top: int | None
        """
        if rounds is not None:
            self.rounds = rounds
        if monthly is not None:
            self.monthly = monthly
        if change is not None:
            self.change = change
        if aoty is not None:
            self.aoty = aoty
        if aoty_cutoff is not None:
            self.aoty_cutoff = aoty_cutoff
        if billboard is not None:
            self.billboard = billboard
        if billboard_multiplier is not None:
            self.billboard_multiplier = billboard_multiplier
        if billboard_top is not None:
            self.monthly = billboard_top

    def get_settings(self) -> list:
        return {
            "rounds": self.rounds,
            "change": self.change,
            "monthly": self.monthly,
            "aoty": self.aoty,
            "aoty_cutoff": self.aoty_cutoff,
            "billboard": self.billboard,
            "billboard_multiplier": self.billboard_multiplier,
            "billboard_top": self.billboard_top
        }

    def is_stage(self, stage: int | list) -> bool:
        """0 = draft is unstarted, 1 = draft is started, 2 = draft is completed, 3 = season is started, 4 = season is over
        :param stage: takes in a stage and checks if the draft is in the matching stage.
        :type stage: int | list
        :returns: if it is the current draft stage or not.
        :rtype: boolean
        """
        if stage is list:
            if self.stage in stage:
                return True
        elif stage is int:
            if self.stage is stage:
                return True
        else:
            return False

    def next_stage(self) -> None:
        """Goes to next stage of draft. 0 = draft is unstarted, 1 = draft is started, 2 = draft is completed, 3 = season is started, 4 = season is overd"""
        if self.stage is 3:
            print("Warning: Season is over.")

        if self.stage > 4:
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
        return self.draftUpdateTime

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
        self.draft_players.append(Player(id=id, name=name))

    def set_all_artists(self, artists: list):
        self.all_artists = artists

    def set_starting_listeners(self, listeners: list):
        self.starting_listeners = listeners

    def set_current_listeners(self, listeners: list):
        self.current_listeners = listeners

    def setUpdateTimer(self, weekday, hour, minute):
        self.draftUpdateTime.append(weekday)
        self.draftUpdateTime.append(hour)
        self.draftUpdateTime.append(minute)

    def updateWeeklyListeners(self, weekListeners):
        artistIndex = {name: i for i,
                       name in enumerate(self.get_all_artists())}

        for player in self.get_all_players():
            artistScores = []
            weeklyTotal = 0

            for artistName in player.All():

                if artistName not in artistIndex:
                    print(
                        f"Warning: artist {artistName} not found in artist pool.")
                    artistScores.append(0)
                    continue

                idx = artistIndex[artistName]
                score = weekListeners[idx]

                artistScores.append(score)
                weeklyTotal += score

            # store weekly totals
            player.addWeeklyScore(weeklyTotal)
            player.addToTotalScore(weeklyTotal)

            # store per-artist weekly scores correctly
            player.setPrevWeekArtistScores(artistScores)

    def updateMonthlyScores(self):
        for player in self.get_all_players():

            week_total = player.getWeeklyScore()
            week_artists = player.getPrevWeekArtistScores()

            # update total 3-week history
            totals = player.getLastThreeWeeksTotals()
            totals.append(week_total)
            if len(totals) > 3:
                totals = totals[-3:]
            player.setLastThreeWeeksTotals(totals)

            # update artist scores for 3-week history
            artists_history = player.getLastThreeWeeksArtists()
            artists_history.append(week_artists)
            if len(artists_history) > 3:
                artists_history = artists_history[-3:]
            player.setLastThreeWeeksArtists(artists_history)

            # compute monthly totals
            monthly_total = sum(totals)
            player.setMonthlyTotalScore(monthly_total)

            # compute monthly per-artist totals
            num_artists = len(week_artists)
            monthly_artist_scores = [0] * num_artists

            for week in artists_history:
                for i in range(num_artists):
                    monthly_artist_scores[i] += week[i]

            player.setMonthlyArtistScores(monthly_artist_scores)

    def updateTotalScores(self):
        for player in self.get_all_players():
            artist_scores_history = player.getLastThreeWeeksArtists()

            if not artist_scores_history:
                player.setTotalArtistScores([])
                continue

            num_artists = len(artist_scores_history[0])
            totals = [0] * num_artists

            for week_scores in artist_scores_history:
                for i in range(num_artists):
                    totals[i] += week_scores[i]

            player.setTotalArtistScores(totals)
