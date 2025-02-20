from gevent import monkey

monkey.patch_all()

from datetime import datetime
from time import time, sleep
from sys import argv
from typing import Any
from flask import request, redirect, make_response
from jinja2 import Template
from argon2 import PasswordHasher

from OtherClasses.PartyInvite import PartyInvite
from OtherClasses.PlayerStatus import PlayerStatus
from OtherClasses.Question import Question
from OtherClasses.ChatMessageNodes import ChatMessageNodes
from OtherClasses.Quiz import Quiz
from OtherClasses.PrivateData import PrivateData
from OtherClasses.Matchmaker import Matchmaker, Match
from OtherClasses.FileNames import FileNames
from OtherClasses.Database import Database
from OtherClasses.CachedElements import CachedElements
from OtherClasses.CoreValues import CoreValues
from OtherClasses.DivIDs import DivID
from OtherClasses.Pages import Pages
from OtherClasses.Player import Player
from OtherClasses.Party import Party
from OtherClasses.Routes import Routes
from OtherClasses.CustomMessages import CustomMessages
from OtherClasses.WSGIElements import WSGIRunner
from OtherClasses.DBHolder import DBHolder


from customisedLogs import CustomisedLogs
from internal.dynamicWebsite import DynamicWebsite



##############################################################################################################################
# NAVBAR


def renderBaseNavbar(viewerObj: DynamicWebsite.Viewer):
    if not viewerObj.privateData.isElementRendered(FileNames.HTML.BaseNavbar):
        viewerObj.privateData.renderElement(FileNames.HTML.BaseNavbar)
        viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.BaseNavbar)).render(baseURI=viewerObj.privateData.baseURI), DivID.navbar1, UpdateMethods.update)


def removeBaseNavbar(viewerObj: DynamicWebsite.Viewer):
    if viewerObj.privateData.isElementRendered(FileNames.HTML.BaseNavbar):
        viewerObj.privateData.removeElement(FileNames.HTML.BaseNavbar)
        viewerObj.updateHTML("", DivID.navbar1, UpdateMethods.update)


def renderLobbyNavbar(viewerObj: DynamicWebsite.Viewer):
    if not viewerObj.privateData.isElementRendered(FileNames.HTML.LobbyNavbar):
        viewerObj.privateData.renderElement(FileNames.HTML.LobbyNavbar)
        viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.LobbyNavbar)).render(baseURI=viewerObj.privateData.baseURI), DivID.navbar2, UpdateMethods.update)


def removeLobbyNavbar(viewerObj: DynamicWebsite.Viewer):
    if viewerObj.privateData.isElementRendered(FileNames.HTML.LobbyNavbar):
        viewerObj.privateData.removeElement(FileNames.HTML.LobbyNavbar)
        viewerObj.updateHTML("", DivID.navbar2, UpdateMethods.update)



def renderQuizNavbar(viewerObj: DynamicWebsite.Viewer):
    if not viewerObj.privateData.isElementRendered(FileNames.HTML.QuizNavbar):
        viewerObj.privateData.renderElement(FileNames.HTML.QuizNavbar)
        viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.QuizNavbar)).render(baseURI=viewerObj.privateData.baseURI), DivID.navbar2, UpdateMethods.update)


def removeQuizNavbar(viewerObj: DynamicWebsite.Viewer):
    if viewerObj.privateData.isElementRendered(FileNames.HTML.QuizNavbar):
        viewerObj.privateData.removeElement(FileNames.HTML.QuizNavbar)
        viewerObj.updateHTML("", DivID.navbar2, UpdateMethods.update)


##############################################################################################################################
# AUTH PAGES


def __renderAuthStructure(viewerObj: DynamicWebsite.Viewer):
    if viewerObj.privateData.currentPage() not in [Pages.AUTH, Pages.PRE_AUTH, Pages.POST_AUTH]:
        viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.AuthStructure)).render(baseURI=viewerObj.privateData.baseURI), DivID.changingPage, UpdateMethods.update)
        viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.Ghost3d)).render(baseURI=viewerObj.privateData.baseURI), DivID.ghost3d, UpdateMethods.update)


def renderAuthPre(viewerObj: DynamicWebsite.Viewer):
    __renderAuthStructure(viewerObj)
    removeBaseNavbar(viewerObj)
    removeLobbyNavbar(viewerObj)
    removeQuizNavbar(viewerObj)
    #hideSocials(viewerObj)
    if viewerObj.privateData.currentPage() != Pages.PRE_AUTH:
        viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.AuthPre)).render(baseURI=viewerObj.privateData.baseURI), DivID.auth, UpdateMethods.update)
        viewerObj.privateData.newPage(Pages.PRE_AUTH)
        viewerObj.sendCustomMessage(CustomMessages.pageChanged(Pages.PRE_AUTH))


def renderAuthForms(viewerObj: DynamicWebsite.Viewer):
    __renderAuthStructure(viewerObj)
    removeBaseNavbar(viewerObj)
    removeLobbyNavbar(viewerObj)
    removeQuizNavbar(viewerObj)
    hideSocials(viewerObj)
    if viewerObj.privateData.currentPage() != Pages.AUTH:
        viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.AuthForms)).render(baseURI=viewerObj.privateData.baseURI), DivID.auth, UpdateMethods.update)
        viewerObj.privateData.newPage(Pages.AUTH)
        viewerObj.sendCustomMessage(CustomMessages.pageChanged(Pages.AUTH))
        sendLoginForm(viewerObj)
        sendRegisterForm(viewerObj)


def renderAuthPost(viewerObj: DynamicWebsite.Viewer):
    return renderLobby(viewerObj)
    __renderAuthStructure(viewerObj)
    removeLobbyNavbar(viewerObj)
    removeQuizNavbar(viewerObj)
    renderBaseNavbar(viewerObj)
    showSocials(viewerObj)
    if viewerObj.privateData.currentPage() != Pages.POST_AUTH:
        viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.AuthPost)).render(baseURI=viewerObj.privateData.baseURI, player=viewerObj.privateData.player), DivID.auth, UpdateMethods.update)
        viewerObj.privateData.newPage(Pages.POST_AUTH)
        viewerObj.sendCustomMessage(CustomMessages.pageChanged(Pages.POST_AUTH))
        sleep(3)
        if viewerObj.privateData.currentPage() == Pages.POST_AUTH:
            renderLobby(viewerObj)


##############################################################################################################################
# CHAT ELEMENTS


def renderChatStructure(viewerObj: DynamicWebsite.Viewer):
    if not viewerObj.privateData.isElementRendered(FileNames.HTML.ChatFull):
        viewerObj.privateData.renderElement(FileNames.HTML.ChatFull)
        viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.ChatFull)).render(baseURI=viewerObj.privateData.baseURI), DivID.chatBox, UpdateMethods.update)
        sendPendingChats(viewerObj)


def sendPendingChats(viewerObj: DynamicWebsite.Viewer):
    pendingChats = DBHolder.useDB().execute(f"SELECT * FROM {Database.PENDING_CHATS.TABLE_NAME} WHERE {Database.PENDING_CHATS.RECEIVER}=? ORDER BY {Database.PENDING_CHATS.SENT_AT}", [viewerObj.privateData.userName])
    for chat in pendingChats: viewerObj.sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, chat[Database.PENDING_CHATS.SENDER], chat[Database.PENDING_CHATS.TEXT]))


##############################################################################################################################
# MUSIC TRAY


def renderMusicTray(viewerObj: DynamicWebsite.Viewer):
    viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.MusicTray)).render(baseURI=viewerObj.privateData.baseURI), DivID.musicTrayHolder, UpdateMethods.update)


##############################################################################################################################
# FRIEND ELEMENTS


def showSocials(viewerObj: DynamicWebsite.Viewer):
    if not viewerObj.privateData.isElementRendered(FileNames.HTML.SocialsStructure):
        viewerObj.privateData.renderElement(FileNames.HTML.SocialsStructure)
        viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.SocialsStructure)).render(baseURI=viewerObj.privateData.baseURI), DivID.friendsStructure, UpdateMethods.update)
        others = []
        for _ in range(15):
            other = Player(None)
            others.append(other)
            viewerObj.sendCustomMessage(CustomMessages.friendAdded(other))
        #TODO: send pending friend requests

        # friendList = SQLconn.execute(f"""SELECT
        # CASE
        #     WHEN {Database.FRIEND.P1} = ? THEN {Database.FRIEND.P2}
        #     WHEN {Database.FRIEND.P1} = ? THEN {Database.FRIEND.P2}
        # END AS result
        # FROM {Database.FRIEND.TABLE_NAME};""", [viewerObj.privateData.userID, viewerObj.privateData.userID])

    viewerObj.sendCustomMessage(CustomMessages.toggleSocials(True))


def hideSocials(viewerObj: DynamicWebsite.Viewer):
    viewerObj.sendCustomMessage(CustomMessages.toggleSocials(False))


##############################################################################################################################
# LOBBY PAGES


def __renderLobbyStructure(viewerObj: DynamicWebsite.Viewer):
    if viewerObj.privateData.currentPage() != Pages.LOBBY:
        viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.LobbyStructure)).render(baseURI=viewerObj.privateData.baseURI), DivID.changingPage, UpdateMethods.update)
        viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.LobbyFeatures)).render(baseURI=viewerObj.privateData.baseURI), DivID.lobbyFeatures, UpdateMethods.update)
        viewerObj.privateData.newPage(Pages.LOBBY)


def renderLobby(viewerObj: DynamicWebsite.Viewer):
    __renderLobbyStructure(viewerObj)
    renderBaseNavbar(viewerObj)
    renderLobbyNavbar(viewerObj)
    removeQuizNavbar(viewerObj)
    showSocials(viewerObj)
    if viewerObj.privateData.player.party is None:
        createParty(viewerObj.privateData.player)


##############################################################################################################################
# QUIZ PAGES


def __renderQuizStructure(viewerObj: DynamicWebsite.Viewer):
    if viewerObj.privateData.currentPage() != Pages.QUIZ:
        viewerObj.privateData.newPage(Pages.QUIZ)
        viewerObj.privateData.player.viewer.sendCustomMessage(CustomMessages.pageChanged(Pages.QUIZ))


def renderQuiz(viewerObj: DynamicWebsite.Viewer):
    viewerObj.privateData.player.setStatus(PlayerStatus.IN_QUIZ)
    viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.QuizFull)).render(baseURI=viewerObj.privateData.baseURI), DivID.changingPage, UpdateMethods.update)
    renderQuizNavbar(viewerObj)


def renderMatchFound(viewerObj: DynamicWebsite.Viewer):
    __renderQuizStructure(viewerObj)
    hideSocials(viewerObj)
    removeBaseNavbar(viewerObj)
    removeLobbyNavbar(viewerObj)
    removeQuizNavbar(viewerObj)
    viewerObj.updateHTML(cachedElements.fetchStaticHTML(FileNames.HTML.MatchFound), DivID.changingPage, UpdateMethods.update)


##############################################################################################################################
# NOTES PAGES


def renderNotesFullPage(viewerObj: DynamicWebsite.Viewer):
    viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.NotesFullPage)).render(baseURI=viewerObj.privateData.baseURI), DivID.changingPage, UpdateMethods.update)


def renderNotes(viewerObj: DynamicWebsite.Viewer):
    viewerObj.sendCustomMessage(CustomMessages.pageChanged(Pages.POST_AUTH))


##############################################################################################################################
# CONTEXTUAL


def renderPreAuthUniversal(viewerObj: DynamicWebsite.Viewer):
    if not viewerObj.privateData.isScriptRendered(FileNames.JS.PreAuthUniversal):
        viewerObj.privateData.renderScript(FileNames.JS.PreAuthUniversal)
        viewerObj.updateHTML(f"<script id='{FileNames.JS.PreAuthUniversal}'>" + cachedElements.fetchStaticJS(FileNames.JS.PreAuthUniversal) + "</script>", DivID.scripts, UpdateMethods.append)
    if not viewerObj.privateData.isScriptRendered(FileNames.JS.Trail):
        viewerObj.privateData.renderScript(FileNames.JS.Trail)
        viewerObj.updateHTML(f"<script id='{FileNames.JS.Trail}'>" + cachedElements.fetchStaticJS(FileNames.JS.Trail) + "</script>", DivID.scripts, UpdateMethods.append)
    viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.UniversalContainer)).render(baseURI=viewerObj.privateData.baseURI), DivID.root, UpdateMethods.update)


##############################################################################################################################
# DECIDE FIRST PAGE


def renderFirstPage(viewerObj: DynamicWebsite.Viewer, isAuthenticated: bool):
    renderPreAuthUniversal(viewerObj)
    renderMusicTray(viewerObj)
    if isAuthenticated:
        if viewerObj.privateData.player is None:
            viewerObj.privateData.player = Player(viewerObj)
            viewerObj.privateData.player.setStatus(PlayerStatus.ONLINE)
        if viewerObj.privateData.expectedPostAuthPage == Pages.LOBBY: renderLobby(viewerObj)
        elif viewerObj.privateData.expectedPostAuthPage == Pages.QUIZ: renderQuiz(viewerObj)
        #elif viewerObj.privateData.expectedPostAuthPage == Pages.marketPlace: renderMarketPlace(viewerObj)
        else: renderAuthPost(viewerObj)
        renderChatStructure(viewerObj)
    else:
        renderAuthPre(viewerObj)


##############################################################################################################################
# USER ACTIONS


def performActionPostSecurity(viewerObj: DynamicWebsite.Viewer, form: dict, isSecure:bool):
    if "PURPOSE" not in form: return
    purpose = form.pop("PURPOSE")
    print(purpose, viewerObj.privateData.currentPage())

    if viewerObj.privateData.currentPage() == Pages.AUTH:
        if purpose == "LOGIN" and isSecure:
            resetFormErrors(viewerObj)
            identifier = form.get("identifier").strip()
            password = form.get("password").strip()
            if not identifier:
                sendLoginCSRF(viewerObj)
                return rejectForm(viewerObj, DivID.loginIdentifierError, "Invalid Username/Email")
            if not password:
                sendLoginCSRF(viewerObj)
                return rejectForm(viewerObj, DivID.loginIdentifierError, "Invalid Password")

            accepted, reason = manualLogin(viewerObj, identifier, password)
            if accepted:
                return renderFirstPage(viewerObj, accepted)
            else:
                sendLoginCSRF(viewerObj)
                return rejectForm(viewerObj, DivID.loginIdentifierError, reason)
        elif purpose == "REGISTER" and isSecure:
            resetFormErrors(viewerObj)
            username = form.get("user-name").strip()
            password = form.get("password").strip()
            confirmPassword = form.get("confirm-password").strip()
            email = form.get("email").strip()
            name = form.get("person-name").strip()
            if not username:
                sendRegisterCSRF(viewerObj)
                return rejectForm(viewerObj, DivID.registerUsernameError, "Invalid Username")
            if not password:
                sendRegisterCSRF(viewerObj)
                return rejectForm(viewerObj, DivID.registerPasswordError, "Invalid Password")
            if password != confirmPassword:
                sendRegisterCSRF(viewerObj)
                return rejectForm(viewerObj, DivID.registerPasswordError, "Passwords Do Not Match")
            if not email:
                sendRegisterCSRF(viewerObj)
                return rejectForm(viewerObj, DivID.registerEmailError, "Invalid Email")
            if not name:
                sendRegisterCSRF(viewerObj)
                return rejectForm(viewerObj, DivID.registerNameError, "Invalid Name")

            accepted, reason = createUser(viewerObj, username, password, name, email)
            if accepted:
                return renderFirstPage(viewerObj, accepted)
            else:
                sendRegisterCSRF(viewerObj)
                return rejectForm(viewerObj, DivID.registerGeneralError, reason)
    if viewerObj.privateData.currentPage() == Pages.PRE_AUTH:
        if purpose == "RENDER_AUTH_FORMS":
            return renderAuthForms(viewerObj)
    if viewerObj.privateData.currentPage() == Pages.LOBBY:
        if purpose == "PARTY_CODE":
            return viewerObj.privateData.player.party.generatePartyCode()
        if purpose == "PARTY_CODE_INPUT":
            newParty = partyCodes.get(form.get("CODE"))
            if newParty is not None:
                oldParty = viewerObj.privateData.player.party
                if oldParty.partyID != newParty.partyID:
                    viewerObj.privateData.player.party = newParty
                    if oldParty: oldParty.removePlayer(viewerObj.privateData.player, True)
                    return newParty.addPlayer(viewerObj.privateData.player)
        if purpose == "READY":
            return viewerObj.privateData.player.party.playerReady(viewerObj.privateData.player)
        if purpose == "UN_READY":
            return viewerObj.privateData.player.party.playerUnready(viewerObj.privateData.player)
    if viewerObj.privateData.currentPage() == Pages.QUIZ:
        if purpose == "OPTION_SELECTED":
            if form.get("QUESTION") in viewerObj.privateData.player.quizQuestions and viewerObj.privateData.player.party.team.match.quiz.currentQuestionID == form.get("QUESTION"):
                question:Question = viewerObj.privateData.player.quizQuestions[form.get("QUESTION")]
                question.selectedOption = question.fetchOption(form.get("OPTION"))
                question.timeTaken = time() - question.startTime
                return
    if viewerObj.privateData.currentPage() not in [Pages.AUTH, Pages.PRE_AUTH, Pages.POST_AUTH]:
        if purpose == "RENDER_HOMEPAGE":
            return renderAuthPost(viewerObj)
    if viewerObj.privateData.currentPage() == Pages.POST_AUTH:
        if purpose == "RENDER_LOBBY":
            return renderLobby(viewerObj)
    if viewerObj.privateData.currentPage() not in [Pages.PRE_AUTH, Pages.AUTH]:
        if purpose == "CHAT":
            form["TEXT"] = Template(form["TEXT"][:50]).render()
            if form["TO"] == ChatMessageNodes.PARTY:
                if viewerObj.privateData.player.party is not None:
                    return viewerObj.privateData.player.party.receiveMessage(viewerObj.privateData.userName, form["TEXT"])
                else:
                    viewerObj.sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, ChatMessageNodes.SYSTEM, "You need to be in a party to send this message."))
            elif form["TO"] == ChatMessageNodes.TEAM:
                if viewerObj.privateData.player.party is not None:
                    if viewerObj.privateData.player.party.team is not None:
                        return viewerObj.privateData.player.party.team.receiveMessage(viewerObj.privateData.userName, form["TEXT"])
                    else:
                        viewerObj.sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, ChatMessageNodes.SYSTEM, "You need to be in a team to send this message."))
            elif form["TO"] in viewerObj.privateData.friends:
                if form["TO"] in activeUsernames: return activeUsernames[form["TO"]].sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, form["FROM"], form["TEXT"]))
                else: return DBHolder.useDB().execute(f"INSERT INTO {Database.PENDING_CHATS.TABLE_NAME} VALUES (?, ?, ?, ?)", [form['TO'], form['FROM'], form['TEXT'], datetime.now()])
            else:
                return viewerObj.sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, ChatMessageNodes.SYSTEM, "Unable to send. Recipient unknown"))
        if purpose == "PARTY_INVITE":
            friendUsername = Template(form["USERNAME"]).render()
            if friendUsername in viewerObj.privateData.player.friends and friendUsername in activeUsernames: # person valid
                if friendUsername in viewerObj.privateData.player.outgoingPartyInvites:
                    return viewerObj.sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, ChatMessageNodes.SYSTEM, f"{friendUsername} already has a pending invite"))
                if viewerObj.privateData.userName in activeUsernames[friendUsername].privateData.player.outgoingPartyJoinRequests:
                    if viewerObj.privateData.player.party.addPlayer(activeUsernames[friendUsername].privateData.player) is not None:
                        pass #TODO: idk
                else:
                    if not viewerObj.privateData.player.party: return viewerObj.sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, ChatMessageNodes.SYSTEM, f"You are not in a party"))
                    else:
                        invite = PartyInvite(viewerObj.privateData.player.party.partyID, viewerObj.privateData.player, viewerObj.privateData.player, activeUsernames[friendUsername].privateData.player)
                        viewerObj.privateData.player.outgoingPartyInvites[friendUsername] = invite
                        activeUsernames[friendUsername].privateData.player.incomingPartyInvites[viewerObj.privateData.userName] = invite
                        invite.sendToReceiver()
                """
                if sender.userName not in self.receivedJoinRequests.values():
                    for player in self.players:
                        if player.viewer is not None:
                            interactionID = RandomisedString().AlphaNumeric(10,10)
                            self.receivedJoinRequests[interactionID] = PartyInvite(interactionID, self, sender, receiver)
                            player.viewer.sendCustomMessage(CustomMessages.receivePartyJoinRequest(interactionID, sender))
                else:
                    return sender.viewer.sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, ChatMessageNodes.SYSTEM, "Already requested to join the party"))
            """
            else:
                return viewerObj.sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, ChatMessageNodes.SYSTEM, "Unable to send. Recipient unknown"))

        if purpose == "PARTY_JOIN_REQUEST":
            friendUsername = Template(form["USERNAME"]).render()
            if friendUsername in viewerObj.privateData.friends and friendUsername in activeUsernames:
                pass
            else:
                return viewerObj.sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, ChatMessageNodes.SYSTEM, "Unable to send. Recipient unknown"))

        if purpose == "FRIEND_REQUEST":
            friendUsername = Template(form["USERNAME"]).render()
            if friendUsername in viewerObj.privateData.friends:
                return viewerObj.sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, ChatMessageNodes.SYSTEM, f"Already friends with {friendUsername} person"))
            if not DBHolder.useDB().execute(f"SELECT {Database.USER_INFO.USERNAME} FROM {Database.USER_INFO.TABLE_NAME} WHERE {Database.USER_INFO.USERNAME} = ?", [friendUsername]):
                return viewerObj.sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, ChatMessageNodes.SYSTEM, f"ID {friendUsername} doesn't exist"))
            if friendUsername in viewerObj.privateData.outgoingFriendRequests:
                return viewerObj.sendCustomMessage(CustomMessages.chatMessage(ChatMessageNodes.YOU, ChatMessageNodes.SYSTEM, f"{friendUsername} already has a pending friend request"))
            if friendUsername in viewerObj.privateData.player.incomingFriendRequests:
                viewerObj.privateData.player.incomingFriendRequests.remove(friendUsername)
                DBHolder.useDB().execute(f"DELETE FROM {Database.PENDING_FRIEND_REQUESTS.TABLE_NAME} WHERE {Database.PENDING_FRIEND_REQUESTS.SENDER}=? AND {Database.PENDING_FRIEND_REQUESTS.RECEIVER}=?", [friendUsername, viewerObj.privateData.userName])
                DBHolder.useDB().execute(f"INSERT INTO {Database.FRIEND.TABLE_NAME} VALUES (?, ?)", [friendUsername, viewerObj.privateData.userName])
                viewerObj.privateData.friends.append(friendUsername)
                if friendUsername in activeUsernames:
                    activeUsernames[friendUsername].privateData.friends.append(viewerObj.privateData.userName)
                    viewerObj.sendCustomMessage(CustomMessages.friendAdded(activeUsernames[friendUsername].privateData.player))
                    return
                else:
                    offlineFriend = Player(None)
                    offlineFriend.userName = friendUsername
                    return viewerObj.sendCustomMessage(CustomMessages.friendAdded(offlineFriend))
    if viewerObj.privateData.currentPage() in [Pages.LOBBY, Pages.POST_AUTH, Pages.NOTES, Pages.MARKETPLACE]:
        if purpose == "LOGOUT":
            freeActiveUsername(viewerObj.privateData.userName)
            logoutDevice(viewerObj)
            return viewerObj.sendCustomMessage(CustomMessages.refreshBrowser())

    return rejectForm(viewerObj, form, "Unknown Purpose")


def rejectForm(viewerObj: DynamicWebsite.Viewer, divToTarget, reason):
    viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.FormErrorElement)).render(errorText=reason), divToTarget, UpdateMethods.update)
    print("FORM REJECTED")


def formSubmitCallback(viewerObj: DynamicWebsite.Viewer, form: dict):
    print("Form received: ", viewerObj.viewerID, form, type(form))
    performActionPostSecurity(viewerObj, form, True)


def customWSMessageCallback(viewerObj: DynamicWebsite.Viewer, message: Any):
    print("WS received: ", viewerObj.viewerID, message, type(message))
    performActionPostSecurity(viewerObj, message, False)


def visitorLeftCallback(viewerObj: DynamicWebsite.Viewer):
    print("Visitor Left: ", viewerObj.viewerID)
    if viewerObj.privateData.player is not None and viewerObj.privateData.player.party is not None:
        viewerObj.privateData.player.party.removePlayer(viewerObj.privateData.player, False)
    freeActiveUsername(viewerObj.privateData.userName)


def newVisitorCallback(viewerObj: DynamicWebsite.Viewer):
    print("Visitor Joined: ", viewerObj.viewerID)
    setPrivateDetails(viewerObj)
    accepted, reason = autoLogin(viewerObj)
    renderFirstPage(viewerObj, accepted)


def firstPageCreator():
    return make_response(Template(cachedElements.fetchStaticHTML(FileNames.HTML.FirstPage)).render(title="GAMBIT", baseURI=request.path))


def freeActiveUsername(userName):
    if userName in activeUsernames:
        del activeUsernames[userName]
        print("Freed username:", userName)


##############################################################################################################################
# AUTHENTICATION


def resetFormErrors(viewerObj: DynamicWebsite.Viewer):
    viewerObj.updateHTML("", DivID.loginIdentifierError, UpdateMethods.update)
    viewerObj.updateHTML("", DivID.registerGeneralError, UpdateMethods.update)
    viewerObj.updateHTML("", DivID.registerNameError, UpdateMethods.update)
    viewerObj.updateHTML("", DivID.registerEmailError, UpdateMethods.update)
    viewerObj.updateHTML("", DivID.registerUsernameError, UpdateMethods.update)
    viewerObj.updateHTML("", DivID.registerPasswordError, UpdateMethods.update)


def sendLoginCSRF(viewerObj: DynamicWebsite.Viewer):
    viewerObj.updateHTML(viewerObj.purposeManager.createCSRF("LOGIN"), DivID.loginCSRF, UpdateMethods.update)


def sendRegisterCSRF(viewerObj: DynamicWebsite.Viewer):
    viewerObj.updateHTML(viewerObj.purposeManager.createCSRF("REGISTER"), DivID.registerCSRF, UpdateMethods.update)


def sendLoginForm(viewerObj: DynamicWebsite.Viewer):
    viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.Login)).render(baseURI=viewerObj.privateData.baseURI), DivID.loginForm, UpdateMethods.update)
    sendLoginCSRF(viewerObj)


def sendRegisterForm(viewerObj: DynamicWebsite.Viewer):
    viewerObj.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.Register)).render(baseURI=viewerObj.privateData.baseURI), DivID.registerForm, UpdateMethods.update)
    sendRegisterCSRF(viewerObj)


def checkPasswordStrength(password:str):
    return len(password) >= 8 and password.isalnum()


def logoutDevice(viewerObj: DynamicWebsite.Viewer):
    DBHolder.useDB().execute(f"DELETE FROM {Database.USER_DEVICES.TABLE_NAME} WHERE {Database.USER_DEVICES.VIEWER_ID}=? LIMIT 1", [viewerObj.viewerID])


def createDevice(viewerObj: DynamicWebsite.Viewer):
    logoutDevice(viewerObj)
    DBHolder.useDB().execute(f"INSERT INTO {Database.USER_DEVICES.TABLE_NAME} VALUES (?, ?, ?)", [viewerObj.viewerID, viewerObj.privateData.userName, viewerObj.privateData.activeSince])


def setPrivateDetails(viewerObj: DynamicWebsite.Viewer):
    viewerObj.privateData = PrivateData()
    viewerObj.privateData.baseURI = request.path.split("?")[0]


def createUser(viewerObj: DynamicWebsite.Viewer, username:str, password:str, personName:str, email:str):
    username = Template(username).render()
    if len(username) > 9:
        return False, "Username too long (max 9)"
    elif not username.isalnum():
        return False, "Username only allows [A-Z, a-z, 0-9]"
    elif len(password)<6:
        return False, "Password should be minimum 6 letters"
    elif DBHolder.useDB().execute(f"SELECT {Database.USER_AUTH.USERNAME} from {Database.USER_AUTH.TABLE_NAME} where {Database.USER_AUTH.USERNAME}=? LIMIT 1", [username]):
        return False, "Username already registered"
    elif DBHolder.useDB().execute(f"SELECT {Database.USER_AUTH.EMAIL} from {Database.USER_AUTH.TABLE_NAME} where {Database.USER_AUTH.EMAIL}=? LIMIT 1", [email]):
        return False, "Email already registered"
    else:
        DBHolder.useDB().execute(f"INSERT INTO {Database.USER_INFO.TABLE_NAME} VALUES (?, ?, ?)", [username, personName, viewerObj.privateData.activeSince])
        DBHolder.useDB().execute(f"INSERT INTO {Database.USER_AUTH.TABLE_NAME} VALUES (?, ?, ?)", [username, email, passwordHasher.hash(password)])
        allowed, reason = freezeViewerTillUsernameRelease(viewerObj, username)
        if allowed:
            createDevice(viewerObj)
            return True, "User registered"
        else:
            return False, reason


def manualLogin(viewerObj: DynamicWebsite.Viewer, identifier:str, password:str):
    savedCredentials = DBHolder.useDB().execute(f"SELECT {Database.USER_AUTH.USERNAME}, {Database.USER_AUTH.PW_HASH} FROM {Database.USER_AUTH.TABLE_NAME} where {Database.USER_AUTH.USERNAME}=? OR {Database.USER_AUTH.EMAIL}=? LIMIT 1", [identifier, identifier])
    if savedCredentials:
        savedCredentials = savedCredentials[0]
        username = savedCredentials[Database.USER_AUTH.USERNAME].decode()
        pwHash = savedCredentials[Database.USER_AUTH.PW_HASH]
        try:
            if passwordHasher.verify(pwHash.decode(), password):
                allowed, reason = freezeViewerTillUsernameRelease(viewerObj, username)
                if allowed:
                    createDevice(viewerObj)
                    return True, "Manual Logged In"
                else:
                    return False, reason
        except:
            pass
    return False, "Invalid Credentials"


def autoLogin(viewerObj: DynamicWebsite.Viewer):
    savedDevice = DBHolder.useDB().execute(f"SELECT {Database.USER_DEVICES.USERNAME} FROM {Database.USER_DEVICES.TABLE_NAME} WHERE {Database.USER_DEVICES.VIEWER_ID}=? LIMIT 1", [viewerObj.viewerID])
    if savedDevice:
        savedDevice = savedDevice[0]
        username = savedDevice[Database.USER_DEVICES.USERNAME].decode()
        allowed, reason = freezeViewerTillUsernameRelease(viewerObj, username)
        if allowed: return True, "Auto Logged In"
        else: return False, reason
    return False, "Unknown Device"


def freezeViewerTillUsernameRelease(viewerObj:DynamicWebsite.Viewer, username):
    print(viewerObj.cookie.instanceID)
    if username in activeUsernames:
        viewerObj.updateHTML("Please close any other instances/tabs to use GAMBIT on this tab.", DivID.root, DynamicWebsite.UpdateMethods.update)
        while username in activeUsernames and viewerObj.currentState != DynamicWebsite.VIEWER_STATES.DEAD:
            print(username, "FROZEN LOGIN", )
            sleep(2)
        if viewerObj.currentState == DynamicWebsite.VIEWER_STATES.DEAD: return False, "Disconnected"
    print("Activated username:", username)
    activeUsernames[username] = viewerObj
    viewerObj.privateData.userName = username
    print(username, "ALLOWED LOGIN")
    return True, "Username free"


##############################################################################################################################
# PARTY


def closeParty(party: Party):
    if party.partyID in partyIDs: del partyIDs[party.partyID]
    if party.partyCode in partyCodes: del partyCodes[party.partyCode]
    matchmaker.removeFromQueue(party)


def onPartyCodeGenerated(party: Party):
    partyCodes[party.partyCode] = party


def createParty(player):
    party = Party(onPartyCodeGenerated, closeParty, renderLobby, cachedElements, matchmaker)
    partyIDs[party.partyID] = party
    if player: party.addPlayer(player)
    return party


##############################################################################################################################
# QUIZ


def onQuizEnd(quiz:Quiz):
    sortedPlayers = sorted(quiz.match.teamA.allPlayers()+quiz.match.teamB.allPlayers(), reverse=True)
    for toSend in sortedPlayers:
        if toSend.viewer:
            renderBaseNavbar(toSend.viewer)
            removeQuizNavbar(toSend.viewer)
            toSend.viewer.updateHTML(Template(cachedElements.fetchStaticHTML(FileNames.HTML.QuizScoreBoard)).render(resultWord="VICTORY" if toSend.party.team.winner else "DEFEAT"), DivID.changingPage, DynamicWebsite.UpdateMethods.update)
            for player in sortedPlayers:
                player.healthImpact = int(player.healthImpact)
                player.score = int(player.score)
                if player.party.team.winner:
                    toSend.viewer.updateHTML(Template(quiz.cachedElements.fetchStaticHTML(FileNames.HTML.QuizScoreBoardWinnerElement)).render(player=player), DivID.quizScoreBoard, DynamicWebsite.UpdateMethods.append)
                else:
                    toSend.viewer.updateHTML(Template(quiz.cachedElements.fetchStaticHTML(FileNames.HTML.QuizScoreBoardLoserElement)).render(player=player), DivID.quizScoreBoard, DynamicWebsite.UpdateMethods.append)
    for player in sortedPlayers:
        player.party.team = None


def onMatchFound(match: Match):
    quiz = Quiz(match, onQuizEnd, cachedElements, DBHolder.useDB())
    for party in match.teamB.parties+match.teamA.parties:
        for player in party.players:
            if player.viewer is not None:
                player.score = 0
                player.correct = 0
                player.incorrect = 0
                player.healthImpact = 0
                player.quizQuestions = {}
                renderMatchFound(player.viewer)
    sleep(3)
    for party in match.teamB.parties+match.teamA.parties:
        for player in party.players:
            if player.viewer is not None:
                renderQuiz(player.viewer)
    quiz.start()


##############################################################################################################################
# TEST


def testMatchmaking():
    sleep(2)
    for _ in range(1):
        party = createParty(Player(None))
        matchmaker.addToQueue(party)
        #sleep(0.5)


##############################################################################################################################
# VARIABLES


serverStartTime = time()
fernetKey = argv[1]
webPort = int(argv[2])
cdPort = int(argv[3])
partyIDs:dict[str, Party] = {}
partyCodes:dict[str, Party] = {}

logger = CustomisedLogs()
DBHolder = DBHolder(logger)
passwordHasher = PasswordHasher()
UpdateMethods = DynamicWebsite.UpdateMethods
cachedElements = CachedElements()
matchmaker = Matchmaker(onMatchFound, cachedElements)
activeUsernames:dict[str, DynamicWebsite.Viewer] = {}
dynamicWebsiteApp = DynamicWebsite(firstPageCreator, newVisitorCallback, visitorLeftCallback, formSubmitCallback, customWSMessageCallback, fernetKey, CoreValues.appName, Routes.webHomePage)


@dynamicWebsiteApp.baseApp.get("/debug")
def _debug():
    final = ""
    final += "<br><br>Parties<br>"
    for partyID in partyIDs:
        final += "<br>&emsp;"+partyID
        final+="<br>&emsp;&emsp;Players"
        for player in partyIDs[partyID].players:
            final += "<br>&emsp;&emsp;"+player.userName
    final += "<br><br>Party Codes<br>"
    for partyCode in partyCodes:
        final += "<br>&emsp;"+partyCode+"&emsp;&emsp;"+partyCodes[partyCode].partyID
    return final


@dynamicWebsiteApp.baseApp.before_request
def _modHeadersBeforeRequest():
    """
    Before any request goes to any route, it passes through this function.
    Applies user remote address correctly (received from proxy)
    :return:
    """
    if request.remote_addr == "127.0.0.1":
        if request.environ.get("HTTP_X_FORWARDED_FOR") is not None:
            address = request.environ.get("HTTP_X_FORWARDED_FOR")
        else: address = "LOCALHOST"
        request.remote_addr = address
    if request.environ.get("HTTP_X_FORWARDED_PATH") is not None:
        request.path = request.environ.get("HTTP_X_FORWARDED_PATH")
    else:
        request.path = ""
    if request.environ.get("HTTP_X_FORWARDED_PROTO") is not None:
        request.scheme = request.environ.get("HTTP_X_FORWARDED_PROTO")


@dynamicWebsiteApp.baseApp.errorhandler(Exception)
def handle_404(error):
    return redirect("http://"+request.environ["HTTP_HOST"].replace(str(webPort), str(cdPort))+request.environ["PATH_INFO"]+"?"+request.environ["QUERY_STRING"])


#Thread(target=testMatchmaking).start()


WSGIRunner(dynamicWebsiteApp.baseApp, webPort, Routes.webHomePage, logger)