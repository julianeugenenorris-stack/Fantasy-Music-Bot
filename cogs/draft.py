from cogs.player import Player
from cogs.scraper import *

import random


class Draft:
    def __init__(
            self,
            name: str,
            rounds: int,
            listener_mult: float = 0.00000003333,
            change_mult: float | None = 0.000003333,
            aoty: list | None = [50, 25, 15, 10, 5, 1, -5, -25],
            billboard_scoring: list | None = [
                10, 5, 5, 5, 5, 3, 3, 3, 3, 3, 1.5],
    ) -> None:
        """
        :param name: The name of the league used in graphics.
        :type name: str
        :param rounds: Number of rounds in the draft.
        :type rounds: int
        :param listener_mult: How many points listener_mult listeners will count for per week.
        :type listener_mult: float
        :param change_mult: How many points will be added as an artists listener_mult listeners goes up and down.
        :type change_mult: float | None
        :param aoty: How many points will be added for album of the year user scores.
        :type aoty: list | None
        :param billboard_scoring: How many points will be scored for the billboard_scoring rankings.
        :type billboard_scoring: list | None
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

        self.listener_mult: float = listener_mult
        self.change_mult: float | None = change_mult

        self.aoty_scoring_guide = ["90+", "89-85",
                                   "84-82", "81-79", "78-75", "74-70", "69-65", "64-"]
        self.aoty_scoring: list[float] = aoty
        """Shows how much an album scores if it is in the a range of aoty user scores. 7 spots in list. 
        [if an album gets a 90+ it will be a this, 89 - 85, 84 - 82, 81 - 79, 78 - 75, 74 - 65, and 64 to the min score]"""

        self.billboard_scoring: list[float] = billboard_scoring
        """How many points having a song in the top billboard_scoring will get you. 
        [#1 -> #100] based on index. Last spot will be used for every spot down the list."""

        self.billboard_current_songs: list = []
        self.stage: int = 0
        """0 = draft is unstarted, 1 is draft is started, 2 is draft is completed, 3 is season is started"""

        self.matchups: list = []
        """Moves clockwise and the groups are paired"""

        self.week_matchups: list = []
        """This weeks matchups"""
        self.matchup_count: int = 0
        """What week on schedual it is """

        self.total_matchups: int = 0
        """What week on schedual it is """
        self.week_in_matchup: int = 0
        """What week in the matchup it is from 0-4"""
        self.week_in_season: int = 0
        self.draft_update_time: list = []
        """weekday - hour - minute"""

    def new_settings(self,
                     rounds: int | None = None,
                     listener_mult: float | None = None,
                     change_mult: float | None = None,
                     aoty_range: str | None = None,
                     aoty_score: float | None = None,
                     billboard_score: float | None = None,
                     billboard_spot: int | None = None) -> bool:
        """
        :param rounds: Number of rounds in the draft.
        :type rounds: int
        :param listener_mult: How many points listener_mult listeners will count for per week.
        :type listener_mult: float
        :param change_mult: How many points will be added as an artists listener_mult listeners goes up and down.
        :type change_mult: float | None
        :param aoty_range: The range the user is changing.
        :type aoty_range: str | None
        :param aoty_score: What the new score will be in the range.
        :type aoty_score: float | None
        :param billboard_score: How many points will be the base for the billboard_scoring scoring.
        :type billboard_score: float | None
        :param billboard_spot: What spot is it in the list.
        :type billboard_spot: int | None
        """
        if rounds is not None:
            self.rounds = rounds
        if listener_mult is not None:
            self.listener_mult = listener_mult
        if change_mult is not None:
            self.change_mult = change_mult
        if aoty_range is not None:
            if aoty_score is not None:
                index = self.aoty_scoring_guide.index(aoty_range)
                self.aoty_scoring[index] = aoty_score
        if billboard_score is not None:
            if billboard_spot is not None:
                self.billboard_scoring[billboard_spot] = billboard_score

    def get_settings(self) -> list:
        return {
            "rounds": self.rounds,
            "change_mult": self.change_mult,
            "listener_mult": self.listener_mult,
            "aoty": self.aoty_scoring,
            "aoty_scoring_guide": self.aoty_scoring_guide,
            "billboard_scoring": self.billboard_scoring
        }

    def next_week(self):
        self.week_in_season += 1
        self.week_in_matchup += 1
        if self.week_in_matchup > 3:
            self.week_in_matchup = 0
            print(
                f"New matchup for week {self.week_in_season + 1}/ Matchup {self.matchup_count}")
            self.next_matchup()
            print(f"New matchup: {self.week_matchups}")
            for player in self.get_all_players():
                player.reset_matchup()

    def generate_matchups(self) -> list:
        """
        Generates a full season of randomized matchups using the Circle Method.
        Returns: A list of lists where each inner list is a list of (p1, p2) pairs for that week.
        """
        players = self.draft_players[:]
        random.shuffle(players)

        # If odd number of players, add an explicit "BYE" placeholder
        if len(players) % 2 == 1:
            players.append("BYE")

        num_players = len(players)
        num_weeks = num_players - 1
        schedule = []

        for _ in range(num_weeks):
            week_pairs = []
            half = num_players // 2
            left = players[:half]
            right = players[half:][::-1]  # Reverse second half

            for p1, p2 in zip(left, right):
                # keep pairs even if BYE is present so structure is consistent
                week_pairs.append((p1, p2))

            schedule.append(week_pairs)

            # rotate (circle method) keeping players[0] fixed
            players = [players[0]] + [players[-1]] + players[1:-1]

        return schedule

    def start_matchups(self):
        base_matchups = self.generate_matchups()
        # Keep previous behavior (if you want double round-robin)
        self.matchups = base_matchups + base_matchups

        # Initialize counters so matchup_count matches the index of week_matchups
        self.matchup_count = 0
        if self.matchups:
            self.week_matchups = self.matchups[0]
            self.total_matchups = 1

    def next_matchup(self):
        """Evaluate the just-finished matchup-week then advance to next week (wraps)."""
        # Evaluate results for the current active week if present
        for p1, p2 in list(self.week_matchups):
            # skip BYE placeholders
            if p1 == "BYE" and isinstance(p2, Player):
                p2.record_add_win()
                continue
            if p2 == "BYE" and isinstance(p1, Player):
                p1.record_add_win()
                continue

            # If any side is not a Player instance, skip evaluation
            if not (isinstance(p1, Player) and isinstance(p2, Player)):
                continue

            # compare matchup_score and apply results
            if p1.matchup_score > p2.matchup_score:
                p1.record_add_win()
                p2.record_add_loss()
            elif p1.matchup_score < p2.matchup_score:
                p2.record_add_win()
                p1.record_add_loss()
            else:
                for player in self.draft_players:
                    if player == p1:
                        p2.record_add_win()
                        p1.record_add_loss()
                        continue
                    if player == p2:
                        p1.record_add_win()
                        p2.record_add_loss()
                        continue
                pass

        # Advance index to next week and wrap
        if not self.matchups:
            self.week_matchups = []
            return

        self.matchup_count = (self.matchup_count + 1) % len(self.matchups)
        self.week_matchups = self.matchups[self.matchup_count]
        self.total_matchups += 1

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

    def next_stage(self) -> None:
        """Goes to next stage of draft. 0 = draft is unstarted, 1 = draft is started, 2 = draft is completed, 3 = season is started, 4 = season is overd"""
        if self.stage == 3:
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

    def get_all_players(self):
        return [p for p in self.draft_players if isinstance(p, Player)]

    def get_update_time(self):
        return self.draft_update_time

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

    def add_new_player(self, user, id: str, name: str, team):
        """Adds new player to the draft.
        :param user_id: The player's discord id.
        :type user_id: int
        :param name: The player's discord name.
        :type name: str
        """
        self.draft_players.append(
            Player(user_id=id, user_name=name, team_name=team, user=user))

    def update_starting_player_listeners(self):
        """Only used at start of season"""
        self.starting_listeners = self.current_listeners
        for player in self.get_all_players():
            for artist in player.artists:
                info = player.artist_info.get(artist)
                index = self.all_artists.index(artist)
                info["starting_listeners"] = self.starting_listeners[index]

    def update_weekly_listeners(self, weekly_listener_data):
        self.current_listeners = weekly_listener_data
        artist_index = {name: i for i,
                        name in enumerate(self.all_artists)}

        for player in self.get_all_players():
            weekly_total = 0

            for artist in player.artists:

                idx = artist_index.get(artist, None)
                listeners = weekly_listener_data[idx] if idx is not None else 0

                # log weekly listeners
                player.artist_info[artist]["weekly"].append(listeners)
                player.artist_info[artist]["matchup_listeners"] += listeners
                weekly_total += listeners

            player.weekly_listeners = weekly_total
            player.matchup_listeners += weekly_total
            player.total_listeners += weekly_total

    def update_total_listeners(self):
        for player in self.get_all_players():
            for artist in player.artists:
                listeners = player.artist_info[artist]["weekly"]
                yearly_total = sum(listeners)
                player.artist_info[artist]["yearly_total"] = yearly_total

    def score_billboard(self):
        self.billboard_current_songs = get_billboard_100(self)

        artist_to_players = {}

        for player in self.get_all_players():
            for artist in player.artists:
                artist_to_players.setdefault(artist, []).append(player)
                info = player.artist_info.get(artist)
                info["week_billboard_score"] = 0
                info["songs_on_billboard"] = []

        for rank, artists in enumerate(self.billboard_current_songs[1]):

            score = self.billboard_scoring[min(
                rank, len(self.billboard_scoring) - 1)]

            for artist in artists:
                if artist in artist_to_players:
                    for player in artist_to_players[artist]:

                        info = player.artist_info.get(artist)
                        if info is None:
                            continue

                        info["week_billboard_score"] = score
                        info["matchup_billboard_score"] += score
                        info["total_billboard_score"] += score
                        info["songs_on_billboard"].append(
                            self.billboard_current_songs[0][rank])

        for player in self.get_all_players():
            weekly_billboard_score = 0
            for artist in player.artists:
                info = player.artist_info.get(artist)
                weekly_billboard_score += info["week_billboard_score"]
            player.total_billboard_score += weekly_billboard_score
            player.matchup_billboard_score += weekly_billboard_score
            player.weeks_billboard_score = weekly_billboard_score

    def score_change(self):  # total_score_change
        for player in self.get_all_players():
            player.weekly_change_listeners = 0
            change_total_score = 0
            for artist in player.artists:
                info = player.artist_info.get(artist)
                weekly_listeners = info["weekly"][-1]
                start_listeners = info["starting_listeners"]
                change_listeners = weekly_listeners - start_listeners
                info["week_listeners_change"] = change_listeners
                change_total_score += change_listeners * self.change_mult
                change_score = change_listeners * self.change_mult
                info["week_score_change"] = change_score
                info["matchup_change_score"] += change_score
                info["total_score_change"] += change_score
            player.total_change_score += change_total_score
            player.matchup_change_score += change_total_score
            player.weeks_change_score = change_total_score

    def score_aoty(self):
        for player in self.get_all_players():
            weekly_score = 0
            for artist in player.artists:
                info = player.artist_info.get(artist)
                info["new_album_score"] = 0
                info["new_album_name"] = ""
                current_albums = get_all_artist_albums(
                    artist_id=info["id_aoty"])
                if current_albums != info["albums_on_record"]:
                    info["albums_on_record"] = current_albums
                    info["new_album_name"] = current_albums[0]
                    album_score = get_most_recent_album_user_score(
                        info["id_aoty"])
                    album_score = int(album_score)
                    info["new_album_score"] = album_score

                    for index, score_range in enumerate(self.aoty_scoring_guide):
                        # Case 1: "90+"
                        if score_range.endswith("+"):
                            min_val = int(score_range[:-1])
                            if album_score >= min_val:
                                info["week_album_score"] = self.aoty_scoring[index]
                                info["matchup_album_score"] += self.aoty_scoring[index]
                                info["total_album_score"] += self.aoty_scoring[index]
                                weekly_score += self.aoty_scoring[index]
                                break

                        # Case 2: "64-"
                        elif score_range.endswith("-"):
                            max_val = int(score_range[:-1])
                            if album_score <= max_val:
                                info["week_album_score"] = self.aoty_scoring[index]
                                info["matchup_album_score"] += self.aoty_scoring[index]
                                info["total_album_score"] += self.aoty_scoring[index]
                                weekly_score += self.aoty_scoring[index]
                                break

                        # Case 3: mid-range "89-85"
                        else:
                            start, end = map(int, score_range.split("-"))
                            if start >= album_score >= end:
                                info["week_album_score"] = self.aoty_scoring[index]
                                info["matchup_album_score"] += self.aoty_scoring[index]
                                info["total_album_score"] += self.aoty_scoring[index]
                                weekly_score += self.aoty_scoring[index]
                                break
            player.weeks_aoty_score = weekly_score
            player.matchup_aoty_score += weekly_score
            player.total_aoty_score += weekly_score

    def score_listeners(self):
        for player in self.get_all_players():
            weekly_total = 0
            for artist in player.artists:
                info = player.artist_info.get(artist)
                weekly_listeners = info["weekly"][-1]
                player.matchup_listeners += weekly_listeners
                week_listeners_score = weekly_listeners * self.listener_mult
                info["weekly_listeners_score"] = week_listeners_score
                info["matchup_listeners_score"] += week_listeners_score
                info["yearly_listeners_total"] += week_listeners_score
                weekly_total += weekly_listeners * self.listener_mult
            player.weeks_listener_score = weekly_total
            player.total_listeners_score += weekly_total
            player.matchup_listeners_score += weekly_total

    def score_total(self):
        for player in self.get_all_players():
            player.total_score = player.total_listeners_score + \
                player.total_aoty_score + player.total_billboard_score + player.total_change_score
            player.weeks_score = player.weeks_listener_score + \
                player.weeks_aoty_score + player.weeks_billboard_score + player.weeks_change_score
            player.matchup_score = player.matchup_listeners_score + \
                player.matchup_aoty_score + player.matchup_billboard_score + \
                player.matchup_change_score
            for artist in player.artists:
                info = player.artist_info.get(artist)
                week_listeners_score = info["weekly_listeners_score"]
                billboard_score = info["week_billboard_score"]
                album_score = info["week_album_score"]
                change_score = info["week_score_change"]
                weeks_total_score = week_listeners_score + \
                    billboard_score + album_score + change_score
                info["week_total_score"] = weeks_total_score
                info["matchup_total_score"] += weeks_total_score
                info["year_total_score"] += weeks_total_score

    def end_season():
        print("End season")
        return

    def get_opponent(self, player, week):
        for p1, p2 in self.matchups[week]:
            if p1 == player:
                return p2
            if p2 == player:
                return p1
        return None
