from randomisedString import RandomisedString

from OtherClasses.CustomMessages import CustomMessages
from OtherClasses.Player import Player


class Party:
    def __init__(self):
        self.partyID = RandomisedString().AlphaNumeric(30, 30)
        self.defaultPartyCode = "Generate"
        self.partyCode = self.defaultPartyCode
        self.players:list[Player] = []
        self.leaderIndex = None
        self.maxPlayers = 3
        self.onPartyClosed = None
        self.onPartyCodeCreated = None
        self.onKick = None
    def __notifyOtherPlayersIndexDecrement(self, hollowIndex:int):
        for player in self.players:
            if player.viewer is None: continue
            player.viewer.sendCustomMessage(CustomMessages.decrementPartyMemberIndex(hollowIndex, len(self.players)))
    def __notifyPlayerPromotion(self, oldLeaderIndex:int, newLeaderIndex:int):
        for player in self.players:
            if player.viewer is not None:
                player.viewer.sendCustomMessage(CustomMessages.newLeader(oldLeaderIndex, newLeaderIndex))
    def __notifyOtherPlayersJoined(self, newPlayerIndex:int, newPlayer:Player):
        for playerIndex in range(len(self.players)):
            player = self.players[playerIndex]
            if playerIndex != newPlayerIndex:
                if player.viewer is None: continue
                player.viewer.sendCustomMessage(CustomMessages.addedPartyMember(newPlayerIndex, newPlayer))
    def __notifyOtherPlayersLeft(self, oldPlayerIndex:int):
        for player in self.players:
            if player.viewer is not None:
                player.viewer.sendCustomMessage(CustomMessages.removedPartyMember(oldPlayerIndex))
    def __notifySelfJoined(self, newPlayerIndex:int):
        newPlayer = self.players[newPlayerIndex]
        if newPlayer.viewer is not None:
            for playerIndex in range(len(self.players)):
                player = self.players[playerIndex]
                newPlayer.viewer.sendCustomMessage(CustomMessages.addedPartyMember(playerIndex, player))
    def __notifySelfLeft(self, oldPlayer:Player):
        if oldPlayer.viewer is not None:
            for playerIndex in range(len(self.players)):
                oldPlayer.viewer.sendCustomMessage(CustomMessages.removedPartyMember(playerIndex))
            oldPlayer.viewer.privateData.party = None
            self.onKick(oldPlayer.viewer)
    def addPlayer(self, newPlayer:Player):
        if len(self.players) < self.maxPlayers:
            self.players.append(newPlayer)
            index = len(self.players) - 1
            if len(self.players) != 1:
                self.__notifySelfJoined(index)
                self.__notifyOtherPlayersJoined(index, newPlayer)
            return index
    def removePlayer(self, oldPlayer:Player):
        for index in range(len(self.players)):
            if self.players[index].userName == oldPlayer.userName:
                if index == self.leaderIndex or self.leaderIndex is None: self.__transferLeader()
                if len(self.players) != 1:
                    self.__notifySelfLeft(oldPlayer)
                    self.__notifyOtherPlayersLeft(index)
                    self.__notifyOtherPlayersIndexDecrement(index)
                self.players.pop(index)
                if len(self.players) == 0:
                    self.onPartyClosed(self)
                return index
    def sendPartyCode(self, player):
        if player.viewer is not None:
            player.viewer.sendCustomMessage(CustomMessages.partyCode(self.partyCode))
    def generatePartyCode(self):
        if self.partyCode == self.defaultPartyCode:
            self.partyCode = RandomisedString().AlphaNumeric(5, 5).lower()
            self.onPartyCodeCreated(self)
            for player in self.players:
                if player is not None:
                    self.sendPartyCode(player)
    def __transferLeader(self):
        if len(self.players):
            oldLeaderIndex = self.leaderIndex
            self.leaderIndex = 0
            self.__notifyPlayerPromotion(oldLeaderIndex, self.leaderIndex)
    def __isLeader(self, player:Player):
        return player.userName == self.players[self.leaderIndex].userName
    def kickPlayer(self, requestedBy:Player, playerIndex:int):
        if self.__isLeader(requestedBy):
            toKick = self.players[playerIndex]
            if toKick is not None:
                self.removePlayer(toKick)
    def sendMessage(self, category:str, sender, text):
        for player in self.players:
            player.viewer.sendCustomMessage(CustomMessages.chatMessage(category, sender, text))