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

    def get_all_artists(self):
        return self.artists

    def getPrevWeekScores(self):
        return self.prevWeekScores

    def getTotalScore(self):
        return self.totalScore

    def getWeeklyScore(self):
        return self.weeklyScore

    def get_id(self):
        return self.user_id

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
