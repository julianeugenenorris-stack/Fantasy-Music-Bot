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
        return [p for p in self.draftRoom if isinstance(p, Player)]

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

    def updateWeeklyListeners(self, weekListeners):
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

            # store weekly totals
            player.addWeeklyScore(weeklyTotal)
            player.addToTotalScore(weeklyTotal)

            # store per-artist weekly scores correctly
            player.setPrevWeekArtistScores(artistScores)

    def updateMonthlyScores(self):
        for player in self.getPlayers():

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
        for player in self.getPlayers():
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


class Player:
    def __init__(self, userID):
        self.userID = userID

        self.artists = []
        self.artistsTotalScore = []
        self.leagueStartListeners = []

        self.totalScore = 0
        self.totalArtistScores = []

        self.lastThreeWeeksTotals = []
        self.lastThreeWeeksArtists = []
        self.monthlyArtistScores = []
        self.monthlyTotalScore = 0

        self.prevWeekArtistScores = []
        self.prevWeekScores = []
        self.weeklyScore = 0

    def getArtists(self):
        return self.artists

    def getPrevWeekScores(self):
        return self.prevWeekScores

    def getTotalScore(self):
        return self.totalScore

    def getWeeklyScore(self):
        return self.weeklyScore

    def getID(self):
        return self.userID

    def getPrevWeekArtistScores(self):
        return self.prevWeekArtistScores

    def getLastThreeWeeksTotals(self):
        return self.lastThreeWeeksTotals

    def getLastThreeWeeksArtists(self):
        return self.lastThreeWeeksArtists

    def getMonthlyArtistScores(self):
        return self.monthlyArtistScores

    def addArtist(self, name):
        self.artists.append(name)

    def setArtist(self, name, location):
        if len(self.artists) >= location:
            self.artists[location] = name

    def addWeeklyScore(self, totalWeekScores):
        self.weeklyScore = totalWeekScores

    def setPrevWeekScores(self, prevWeekScores):
        self.prevWeekScores = prevWeekScores

    def setPrevWeekArtistScores(self, prevWeekArtistScores):
        self.prevWeekArtistScores = prevWeekArtistScores

    def setArtistsTotalScore(self, totalScore):
        self.artistsTotalScore = totalScore

    def setTotalArtistScores(self, totalArtistScores):
        self.totalArtistScores = totalArtistScores

    def setLastWeekScore(self, lastWeeksScore):
        self.lastWeeksScores = lastWeeksScore

    def addToTotalScore(self, totalScore):
        self.totalScore += totalScore

    def setLastThreeWeeksTotals(self, lastThreeWeeksTotals):
        self.lastThreeWeeksTotals = lastThreeWeeksTotals

    def setLastThreeWeeksArtists(self, lastThreeWeeksArtists):
        self.lastThreeWeeksArtists = lastThreeWeeksArtists

    def setMonthlyArtistScores(self, monthlyArtistScores):
        self.monthlyArtistScores = monthlyArtistScores

    def setMonthlyTotalScore(self, monthlyTotalScore):
        self.monthlyTotalScore = monthlyTotalScore
