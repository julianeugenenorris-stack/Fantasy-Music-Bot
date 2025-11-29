class Draft:
    def __init__(self, name, roundCount):
        self.draftRoom = []
        self.leagueArtists = []
        self.leagueListeners = []
        self.draftname = name
        self.turn = 0
        self.size = 0
        self.direction = 1
        self.rounds = roundCount
        self.draftStarted = False
        self.draftCompleted = False

    def getSize(self):
        return self.size

    def getName(self):
        return self.draftname

    def getArtists(self):
        return self.leagueArtists

    def getListeners(self):
        return self.leagueListeners

    def getTurn(self):
        return self.turn

    def getRound(self):
        return self.rounds

    def getPlayers(self):
        return self.draftRoom

    def isDone(self):
        return self.draftCompleted

    def isStarted(self):
        return self.draftStarted

    def isDraftCompleted(self):
        return self.draftCompleted

    def startDraft(self):
        self.draftStarted = True

    def endDraft(self):
        self.draftCompleted = True

    def nextTurn(self):
        if self.direction == 1:
            if self.turn is self.size - 1:
                self.direction = -1
                self.rounds -= 1
                if self.rounds < 0:
                    print(f"rounds: {self.rounds} draft is complete\n")
                    self.draftCompleted = True
                return
            self.turn += self.direction
        else:
            if self.turn == 0:
                self.direction = 1
                self.rounds -= 1
                if self.rounds < 0:
                    print(f"rounds: {self.rounds} draft is complete\n")
                    self.draftCompleted = True
                return
            self.turn += self.direction

    def addPlayer(self, userID):
        self.size += 1
        self.draftRoom.append(Player(userID))

    def setArtists(self, artists):
        self.leagueArtists = artists

    def setListeners(self, listeners):
        self.leagueListeners = listeners


class Player:
    def __init__(self, userID):
        self.artists = []
        self.artistsTotalScore = []
        self.lastWeeksScores = []
        self.userID = userID
        self.totalScore = 0
        self.weeklyScore = 0

    def getArtists(self):
        return self.artists

    def getArtistsTotalScore(self):
        return self.artistsTotalScore

    def getLastWeekScore(self):
        return self.lastWeeksScores

    def getTotalScore(self):
        return self.totalScore

    def getWeeklyScore(self):
        return self.weeklyScore

    def getID(self):
        return self.userID

    def setArtist(self, name):
        self.artists.append(name)

    def setArtistsTotalScore(self, totalScore):
        self.artistsTotalScore = totalScore

    def setLastWeekScore(self, lastWeeksScore):
        self.lastWeeksScores = lastWeeksScore

    def setTotalScore(self, totalScore):
        self.totalScore = totalScore

    def setWeeklyScore(self, weeklyScore):
        self.weeklyScore = weeklyScore
