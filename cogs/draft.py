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
        """What week in the schedual it is on from 0-12"""

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

    def next_matchup(self):
        players_versus: list = []
        for index, player in enumerate(self.week_matchups[0]):
            players_versus.append([player, self.week_matchups[1][index]])
        for players in players_versus:
            player_1: Player = players[0]
            player_2: Player = players[1]
            if player_1.matchup_score > player_2.matchup_score:
                player_1.record_add_win()
                player_2.record_add_loss()
            elif player_1.matchup_score < player_2.matchup_score:
                player_2.record_add_win()
                player_1.record_add_loss()
            else:
                return
        self.matchup_count += 1
        self.week_matchups = self.matchups[self.matchup_count:self.matchup_count+1]

    def start_matchups(self):
        players: list = self.draft_players[:]
        random.shuffle(players)  # suffle
        sched = create_schedule(players)
        full_sched = []
        for week in range(0, 24):
            try:
                full_sched += sched[week]
            except:
                sched += sched
                full_sched += sched[week]
        self.matchups = full_sched[:]
        self.week_matchups = full_sched[0:1]

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
                weekly_total += listeners

            player.weekly_listeners = weekly_total
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
                info["songs_on_billboard"].clear()

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
            player.total_change_listeners = 0
            change_total_listeners = 0
            change_total_score = 0
            for artist in player.artists:
                info = player.artist_info.get(artist)
                weekly_listeners = info["weekly"][-1]
                start_listeners = info["starting_listeners"]
                change_listeners = weekly_listeners - start_listeners
                change_total_listeners += change_listeners
                info["week_listeners_change"] = change_listeners
                change_total_score += change_listeners * self.change_mult
                info["week_score_change"] = change_listeners * self.change_mult
                info["total_score_change"] += change_listeners * self.change_mult
            player.total_change_score += change_total_score
            player.matchup_change_score += change_total_score
            player.weeks_change_score = change_total_score

    def score_aoty(self):
        for player in self.get_all_players():
            weekly_score = 0
            for artist in player.artists:
                info = player.artist_info.get(artist)
                info["new_album_score"] = 0
                current_albums = get_all_artist_albums(
                    artist_id=info["id_aoty"])
                if current_albums != info["albums_on_record"]:
                    info["albums_on_record"] = current_albums
                    info["new_album_name"] = current_albums[0]
                    album_score = get_most_recent_album_user_score(
                        info["id_aoty"])
                    album_score = int(album_score)
                    info["week_album_score"] = album_score

                    for index, score_range in enumerate(self.aoty_scoring_guide):
                        # Case 1: "90+"
                        if score_range.endswith("+"):
                            min_val = int(score_range[:-1])
                            if album_score >= min_val:
                                info["new_album_score"] = self.aoty_scoring[index]
                                info["total_album_score"] += self.aoty_scoring[index]
                                weekly_score += self.aoty_scoring[index]
                                break

                        # Case 2: "64-"
                        elif score_range.endswith("-"):
                            max_val = int(score_range[:-1])
                            if album_score <= max_val:
                                info["new_album_score"] = self.aoty_scoring[index]
                                info["total_album_score"] += self.aoty_scoring[index]
                                weekly_score += self.aoty_scoring[index]
                                break

                        # Case 3: mid-range "89-85"
                        else:
                            start, end = map(int, score_range.split("-"))
                            if start >= album_score >= end:
                                info["new_album_score"] = self.aoty_scoring[index]
                                info["total_album_score"] += self.aoty_scoring[index]
                                weekly_score += self.aoty_scoring[index]
                                break
                else:
                    info["new_album_name"] = ""
            player.weeks_aoty_score = weekly_score
            player.matchup_aoty_score += weekly_score
            player.total_aoty_score += weekly_score

    def score_listeners(self):
        for player in self.get_all_players():
            monthly_total = 0
            weekly_total = 0
            for artist in player.artists:
                info = player.artist_info.get(artist)
                monthly_listeners = info["monthly"][-1]
                weekly_listeners = info["weekly"][-1]
                week_listeners_score = weekly_listeners * self.listener_mult
                info["weekly_listeners_score"] = week_listeners_score
                info["matchup_listeners_score"] += week_listeners_score
                info["yearly_listeners_total"] += week_listeners_score
                weekly_total += weekly_listeners * self.listener_mult
                info["monthly_listeners_score"] = monthly_listeners * \
                    self.listener_mult
                monthly_total += monthly_listeners * self.listener_mult
            player.weeks_listener_score = weekly_total
            player.monthly_listeners_score = monthly_total
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


def create_schedule(list: list):
    """ Create a schedule for the teams in the list and return it"""
    s = []

    if len(list) % 2 == 1:
        list = list + ["BYE"]

    for i in range(len(list)-1):

        mid = int(len(list) / 2)
        l1 = list[:mid]
        l2 = list[mid:]
        l2.reverse()

        # Switch sides after each round
        if (i % 2 == 1):
            s = s + [l1, l2]
        else:
            s = s + [l2, l1]

        list.insert(1, list.pop())

    print(s[:])

    return s
