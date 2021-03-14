import discord
from discord.ext import commands
import json
from lib import steam_community_news_parser as newsParser


class GuildChannelSteamNews:
    def __init__(self, guild, channel, steamNewsURL):
        self.guild = guild
        self.channel = channel
        self.steamsNewsURL = steamNewsURL


class SteamCommunityNewsBot:
    def __init__(self):
        self.jsonConfigPath = None
        self.jsonData = None
        self.bot = commands.Bot(command_prefix='!')

    def readConfig(self, jsonConfigPath):
        """
        Reads in the config file which stores information about which steam community is associated with which discord channel.
        :param jsonConfigPath: Path to json configuration file
        :return: The json data stored within the json configuration file
        """
        try:
            f = open(jsonConfigPath, )
            self.jsonConfigPath = jsonConfigPath
            self.jsonData = json.load(f)
            return True
        except:
            return False

    def handleIncomingMessage(self, message):
        """
        Called when a new message is recieved by the bot. It first determines if the bot has been tagged. If the bot is not tagged, then nothing happens.
        If the bot is tagged, then the subsequent text is parsed for the available commands that the bot offers (add, remove, list, latest).
        The function then generates a return message(s) to send back to the channel where the bot was called.
        :param message: The message sent in discord that the bot has recieved.
        :return: A list of messages which are to be sent back to the channel which tagged the bot. empty if the bot was not tagged.
        """
        returnMsgList = []

        for mention in message.mentions:
            if mention.id == self.bot.user.id:
                print("INFO: New message in channel {} tagged this bot, responding.".format(message.channel.name))
                if "add" in message.content:
                    print("INFO: User wants to add new URL to this channel.")
                    returnmsg, communityName = self.addNewCommunityNews(message)
                    addedSuccessFailMsg = {'embed': False, 'contents': returnmsg}
                    if communityName != None:
                        print("INFO: Sucessfully added community, now pushing latest update.")
                        embedmsg = self.getLatestAnnouncmentForCommunity(communityName)
                        latestAnnoucnmentMsg = {'embed': True, 'contents': embedmsg}
                    returnMsgList.append(addedSuccessFailMsg)
                    returnMsgList.append(latestAnnoucnmentMsg)
                elif "latest" in message.content:
                    # strip out community name from message: @SteamCommunityBot latest <community name>
                    communityName = " ".join(message.content.split()[2:])  # make a single string single spaced

                    if "all" in communityName:
                        print("INFO: User has requested an update for all communities associated with this channel.")
                        communitiesToUpdate = self.getCommunityNamesForChannel(message.channel)
                        for communityName in communitiesToUpdate:
                            latestAnnouncment = self.getLatestAnnouncmentForCommunity(communityName)
                            latestAnnoucnmentMsg = {'embed': True, 'contents': latestAnnouncment}
                            returnMsgList.append(latestAnnoucnmentMsg)
                    else:
                        print("INFO: User has requested an update for {}.".format(communityName))
                        embedmsg = self.getLatestAnnouncmentForCommunity(communityName)
                        if embedmsg == None:
                            noCommunityText = "No steam community of name {} is associated with this channel! Cannot get latest announcement.".format(
                                communityName)
                            noCommunityMsg = {'embed': False, 'contents': noCommunityText}
                            returnMsgList.append(noCommunityMsg)
                        else:
                            latestAnnouncmentMsg = {'embed': True, 'contents': embedmsg}
                            returnMsgList.append(latestAnnouncmentMsg)
                elif "list" in message.content:
                    print("INFO: User has requested a list of all communities associated with this channel.")
                    listMsg = {'embed': False, 'contents': self.getAllCommunityNameURLsMsg(message.channel)}
                    returnMsgList.append(listMsg)
                elif "remove" in message.content:

                    # strip out community name from message: @SteamCommunityBot Remove <community name>
                    communityName = " ".join(message.content.split()[2:])
                    removalSuccess = self.removeCommunity(communityName)
                    print("INFO: User has requested a the removal of the community named {}".format(communityName))
                    if removalSuccess:
                        successMsg = {'embed': False,
                                      'contents': "Successfully removed announcements for {} from this channel".format(
                                          communityName)}
                        returnMsgList.append(successMsg)
                    else:
                        failMsg = {'embed': False,
                                   'contents': "Failed to removed announcements for {}, that community is not associated with this channel".format(
                                       communityName)}
                        returnMsgList.append(failMsg)
                else:
                    helpMsg = {'embed': False,
                               'contents': self.getHelpMessage()}
                    returnMsgList.append(helpMsg)
                break

        return returnMsgList

    def getHelpMessage(self):
        """
        :return: The default response for helping users use the bot.
        """
        # helpMessage = "Thanks for tagging Steam Community Bot! \n" \
        #               + "There are a few simple commands to use this bot:\n" \
        #               + '\tadd <steam community news URL> - Causes any new news posted on the steam community news page to sent to this channel\n' \
        #               + '\tlist - Shows all steam communities associated with this channel.\n' \
        #               + '\tlatest <steam_community_name> - Causes latest news on the specified steam community to be sent to this channel.\n' \
        #               + '\tlatest all - Causes latest news on all steam communities associated with this channel to be sent to this channel.\n' \
        #               + '\tremove <steam community news URL> - Removes the specified steam community from this channel. \n'
        helpMessage = "Hello ECE 528/428!"
        return helpMessage

    def setLatestAccouncementTitle(self, communityName, accountmentTitle):
        """
        When a new announcement is found that hasn't been shared by the bot before, this function will take the title
        of that annoucnment and add it to the json configuration file so that it will not be shared again with the
        community.
        :param communityName: String of community name which has a new announcement to save
        :param accountmentTitle: String of the announcements title to save to the json configuration file
        """
        for community in self.jsonData["Communities"]:
            if communityName == community["communityName"]:
                community['lastAnnouncementTitle'] = accountmentTitle
                break
        self.writeJsonData()

    def addNewCommunityNews(self, message):
        """
        Adds a new steam community to the json config file if a valid URL is provided.
        The json configuration file is updated with the new community information.
        If a valid URL is provided the name of the community associated with the URL will be returned along with
        a success message to share with the user. If the URL is invalid then a error message will be returned.
        :param message: The message a user sent in the channel
        :return returnMessage: The message to share with the user as a result of adding a new community
        :return communityName: The name of the community that was added if sucessful, None otherwise.
        """
        returnMessage = 'Default error message'
        communityName = None
        if len(message.content.split()) >= 2:
            url = message.content.split()[2]
            retrievedCommunityName = newsParser.getCommunityName(url)
            if retrievedCommunityName != None:
                latestAnnoucnment = newsParser.getLatestAccouncement(url)
                newJsonEntry = {
                    "communityName": retrievedCommunityName,
                    "channelId": message.channel.id,
                    "channelName": message.channel.name,
                    "url": url,
                    "lastAnnouncementTitle": latestAnnoucnment['title']
                }
                self.jsonData['Communities'].append(newJsonEntry)
                self.writeJsonData()
                returnMessage = "Adding new community to this channel. Expect news from the steam community at {} to be posted to this channel!".format(
                    url)
                communityName = retrievedCommunityName
            else:
                returnMessage = 'Invalid URL Provided, please provide valid steam community news URL. EG: https://steamcommunity.com/app/892970/'
        else:
            returnMessage = 'Invalid URL Provided, please provide valid steam community news URL. EG: https://steamcommunity.com/app/892970/'

        return returnMessage, communityName

    def writeJsonData(self):
        """
        Writes the stored/modified json data to the configuration file any time a change is made.
        """
        with open(self.jsonConfigPath, 'w') as configFile:
            json.dump(self.jsonData, configFile)

    def createEmbedObjectForAnnouncment(self, announcment):
        """
        Given an announcment create an object which can be embedded in a discord message.
        :param announcment: An announcment dictionary which is used to create the embedded message
        :return: The embedded message
        """
        embedObj = discord.Embed(title=announcment['title'], description=announcment['info'], url=announcment['url'],
                                 color=0x00ff00)
        if announcment['img_url'] != None:
            embedObj.set_image(url=announcment['img_url'])
        # embedObj.add_field(name="Field1", value="hi", inline=False)
        # embedObj.add_field(name="Field2", value="hi2", inline=False)
        return embedObj

    def getNewAnnouncementChannelPairs(self):
        """
        Called to find if any new announcments in any steam communities were made. If there were, then creates
        a list of announcment channel pairs. This information is then used to send each announcment to the correct
        channel it should be sent to.
        :return: List of announcment channel pairs for any announcements which are new to any community
        """
        newAnnoucementChannelPairs = []
        for community in self.jsonData["Communities"]:
            latestAnnouncment = newsParser.getLatestAccouncement(community['url'])
            # If new announcment
            if latestAnnouncment['title'] != community['lastAnnouncementTitle']:
                embeddedMessageForAnnouncment = self.createEmbedObjectForAnnouncment(latestAnnouncment)
                self.setLatestAccouncementTitle(community["communityName"], latestAnnouncment['title'])
                announceChannelPair = {"embedMsg": embeddedMessageForAnnouncment, "channelId": community["channelId"]}
                newAnnoucementChannelPairs.append(announceChannelPair)
        return newAnnoucementChannelPairs

    def getLatestAnnouncmentForCommunity(self, communityName):
        """
        Given a community name get an embedded message using the latest announcment in the community.
        :param communityName: Name of community to get the latest announcment for.
        :return: An embedded message to send to the appropriate channel.
        """
        embeddedMessageForAnnouncment = None
        for community in self.jsonData['Communities']:
            if community['communityName'] == communityName:
                latestAnnouncment = newsParser.getLatestAccouncement(community['url'])
                embeddedMessageForAnnouncment = self.createEmbedObjectForAnnouncment(latestAnnouncment)
                self.setLatestAccouncementTitle(community['communityName'], latestAnnouncment['title'])

        return embeddedMessageForAnnouncment

    def getAllCommunityNameURLsMsg(self, channel):
        """
        Grabs all community names and their URLs from the json configuration file, then makes a nice
        human readable string to display them.
        :param channel: Channel information about which communities and URLs are needed for
        :return: String containing human readable list of community URL pairs for requested channel
        """
        community_found = False
        returnMsg = "List of steam communities associated with this channel:\n"
        for community in self.jsonData['Communities']:
            if community['channelId'] == channel.id:
                newStr = "\t{} - ```{}```\n".format(community['communityName'], community['url'])
                returnMsg = returnMsg + newStr
                community_found = True

        if not community_found:
            returnMsg = self.getNoAssociatedCommunitiesErrorMsg()

        return returnMsg

    def getNoAssociatedCommunitiesErrorMsg(self):
        """
        Provide error message to indicate that a community name provided isn't associated with a given channel.
        :return: Error message
        """
        returnMsg = "This channel is not associated with a Steam Community News! You can add a " \
                    + "community URL using the add option.\n" \
                    + '\tadd <steam community news URL> - Causes any new news posted on the steam community news ' \
                    + 'page to sent to this channel\n '
        return returnMsg

    def removeCommunity(self, communityName):
        """
        Removes a community from the json configuration and returns a flag indicating if it was sucessful
        :param communityName: Name of community to remove
        :return: Flag to indicate if community was removed sucessfully (true) or not (false)
        """
        removalSuccess = False
        for community in self.jsonData['Communities']:
            if communityName in community['communityName']:
                self.jsonData['Communities'].remove(community)
                self.writeJsonData()
                removalSuccess = True

        return removalSuccess

    def getCommunityNamesForChannel(self, channel):
        """
        Return a list of all community names associated with a channel.
        :param channel: The name of the channel to get communities for
        :return: List of all community names for the provided channel
        """
        communityNameList = []
        for community in self.jsonData['Communities']:
            if community['channelId'] == channel.id:
                communityNameList.append(community['communityName'])
        return communityNameList
