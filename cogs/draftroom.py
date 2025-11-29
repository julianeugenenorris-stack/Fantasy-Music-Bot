class Draft:
    def __init__(self, name, roundCount):
        self.draftRoom = []
        self.leagueArtists = []
        self.draftname = name

        self.turn = 0
        self.size = 0
        self.direction = 1
        self.rounds = roundCount

        self.draftStarted = False
        self.draftCompleted = False
        self.seasonStarted = False

        # weekday - hour - minute
        self.draftUpdateTime = []

    def getSize(self):
        return self.size

    def getName(self):
        return self.draftname

    def getArtists(self):
        return self.leagueArtists

    def getTurn(self):
        return self.turn

    def getRound(self):
        return self.rounds

    def getPlayers(self):
        return self.draftRoom

    def getUpdateTime(self):
        return self.draftUpdateTime

    def isDone(self):
        return self.draftCompleted

    def isDraftStarted(self):
        return self.draftStarted

    def isSeasonStarted(self):
        return self.seasonStarted

    def isDraftCompleted(self):
        return self.draftCompleted

    def startDraft(self):
        self.draftStarted = True

    def endDraft(self):
        self.draftCompleted = True

    def startSeason(self):
        self.seasonStarted = True

    def nextTurn(self):
        if self.direction == 1:
            if self.turn is self.size - 1:
                self.direction = -1
                self.rounds -= 1
                if self.rounds <= 0:
                    self.draftCompleted = True
                return
            self.turn += self.direction
        else:
            if self.turn == 0:
                self.direction = 1
                self.rounds -= 1
                if self.rounds <= 0:
                    self.draftCompleted = True
                return
            self.turn += self.direction

    def addPlayer(self, userID):
        self.size += 1
        self.draftRoom.append(Player(userID))

    def setArtists(self, artists):
        self.leagueArtists = artists

    def setStartListeners(self, listeners):
        self.leagueStartListeners = listeners

    def setUpdateTimer(self, weekday, hour, minute):
        self.draftUpdateTime.append(weekday)
        self.draftUpdateTime.append(hour)
        self.draftUpdateTime.append(minute)

    def weeklyListenerUpdate(self, weekListeners):
        artistIndex = {name: i for i, name in enumerate(self.getArtists())}

        for player in self.getPlayers():
            artistScores = []
            weeklyTotal = 0

            for artistName in player.getArtists():

                if artistName not in artistIndex:
                    print(
                        f"Warning: artist {artistName} not found in artist pool.")
                    artistScores.append(0)
                    continue

                idx = artistIndex[artistName]
                score = weekListeners[idx]

                artistScores.append(score)
                weeklyTotal += score

            player.addWeeklyScore(weeklyTotal)
            player.setPrevWeekScores(artistScores)
            player.addToTotalScore(weeklyTotal)

    def updateMonthlyScores(self, weeklyTotals, weeklyArtistScores):
        players = self.getPlayers()

        for i, player in enumerate(players):
            # --- Weekly scoreboard ---
            week_total = weeklyTotals[i]
            week_artists = weeklyArtistScores[i]  # list of per-artist scores

            # total his
            total_history = player.getLastThreeWeeksTotals()
            total_history.append(week_total)

            if len(total_history) > 3:
                total_history = total_history[-3:]

            player.setLastThreeWeeksTotals(total_history)

            # artists his
            artist_history = player.getLastThreeWeeksArtists()
            artist_history.append(week_artists)

            if len(artist_history) > 3:
                artist_history = artist_history[-3:]

            player.setLastThreeWeeksArtists(artist_history)

            # monthly total
            monthly_total = sum(total_history)
            player.setMonthlyTotalScore(monthly_total)

            # monthly artists scores, each artist score for last 3 weeks
            num_artists = len(week_artists)
            monthly_artist_scores = [0] * num_artists

            for week in artist_history:
                for a in range(num_artists):
                    monthly_artist_scores[a] += week[a]

            player.setMonthlyArtistScores(monthly_artist_scores)


class Player:
    def __init__(self, userID):
        self.userID = userID
        self.totalScore = 0

        self.artists = []
        self.artistsTotalScore = []
        self.leagueStartListeners = []

        self.lastThreeWeeksTotals = []
        self.lastThreeWeeksArtists = []
        self.monthlyArtistScores = []
        self.monthlyTotalScore = 0

        self.prevWeekArtistScores = []
        self.prevWeekScores = []
        self.totalScores = []
        self.weeklyScore = 0

    def getArtists(self):
        return self.artists

    def getprevWeekScores(self):
        return self.prevWeekScores

    def getTotalScore(self):
        return self.totalScore

    def getWeeklyScore(self):
        return self.weeklyScore

    def getID(self):
        return self.userID

    def addArtist(self, name):
        self.artists.append(name)

    def setArtist(self, name, location):
        if len(self.artists) >= location:
            self.artists[location] = name

    def setWeeklyScore(self, totalWeekScores):
        self.weeklyScore = totalWeekScores

    def setPrevWeekScores(self, prevWeekScores):
        self.prevWeekScores.copy(prevWeekScores)

    def setArtistsTotalScore(self, totalScore):
        self.artistsTotalScore = totalScore

    def setLastWeekScore(self, lastWeeksScore):
        self.lastWeeksScores = lastWeeksScore

    def addToTotalScore(self, totalScore):
        self.totalScore += totalScore

    def setWeeklyScore(self, weeklyScore):
        self.weeklyScore = weeklyScore

    def getLastThreeWeeksTotals(self):
        return self.lastThreeWeeksTotals

    def setLastThreeWeeksTotals(self, arr):
        self.lastThreeWeeksTotals = arr

    def getLastThreeWeeksArtists(self):
        return self.lastThreeWeeksArtists

    def setLastThreeWeeksArtists(self, arr):
        self.lastThreeWeeksArtists = arr

    def setMonthlyArtistScores(self, arr):
        self.monthlyArtistScores = arr

    def setMonthlyTotalScore(self, score):
        self.monthlyTotalScore = score
