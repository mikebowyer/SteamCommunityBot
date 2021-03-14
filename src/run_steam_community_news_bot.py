import argparse, asyncio, discord, sys, time
from steam_community_news_bot import SteamCommunityNewsBot

parser = argparse.ArgumentParser(description='Bot to check for latest patches for a steam community news')
parser.add_argument('--token', help='Token to use to connect bot to channels')
parser.add_argument('--jsonConfig', help='JSON config file which contains which guilds')

steamCommunityNewsBot = SteamCommunityNewsBot()


@steamCommunityNewsBot.bot.event
async def on_message(message):
    """
    This function defines what to do when any message is sent that the steam community bot can see.
    It will rely on handleIncomingMessage to generate any response messages (if necassary), then send them to the appropriate channel.
    :param message: The message sent by a user on discord which this bot has read access to.
    """
    returnMsgs = steamCommunityNewsBot.handleIncomingMessage(message)

    for msg in returnMsgs:
        if msg["embed"]:
            await message.channel.send(embed=msg['contents'])
        else:
            await message.channel.send(msg['contents'])


@steamCommunityNewsBot.bot.event
async def on_ready():
    """
    The method which is used when the bot succesfully connects to discord server and is ready to send/receive messages.
    """
    print('INFO: Steam Community News Bot succesfully logged in as')
    print(steamCommunityNewsBot.bot.user.name)
    print(steamCommunityNewsBot.bot.user.id)
    print('------')


async def send_new_announcements():
    """
    A function which is called every 5 minutes (300 seconds) to check to see if any steam community has a new announcement.
    If a new announcement is found, then it will be sent to the appropriate channel.
    """
    await steamCommunityNewsBot.bot.wait_until_ready()
    while True:
        print("INFO: Checking for new announcements")
        newAnnouncementChannelPairs = steamCommunityNewsBot.getNewAnnouncementChannelPairs()
        for announceChanPair in newAnnouncementChannelPairs:
            try:
                channel = steamCommunityNewsBot.bot.get_channel(announceChanPair['channelId'])
                print("INFO: Found new announcement for community associated with channel id {}".format(
                    announceChanPair['channelId']))
                await channel.send(embed=announceChanPair['embedMsg'])
            except (discord.DiscordException, discord.ClientException, discord.HTTPException, discord.NotFound):
                print("Could not connect to Discord when sending new announcement to channelID" + announceChanPair[
                    'channelId'])
        # Wait 5 minutes before checking again
        await asyncio.sleep(300)


if __name__ == '__main__':

    args = parser.parse_args()

    while True:
        try:
            print("INFO: Parsing json configuration file")
            if steamCommunityNewsBot.readConfig(args.jsonConfig):
                print("INFO: Parsing Successful")
                print("INFO: Starting async task for checking new announcements")
                send_new_announcements_task = asyncio.ensure_future(send_new_announcements())
                print("INFO: Starting Steam Community News Bot!")
                steamCommunityNewsBot.bot.loop.run_until_complete(steamCommunityNewsBot.bot.start(args.token))
            else:
                print("Error reading config file, exiting.")
                break
        except KeyboardInterrupt:
            print("Keyboard interrupt detected, exiting.")
            steamCommunityNewsBot.bot.loop.run_until_complete(steamCommunityNewsBot.bot.logout())
            send_new_announcements_task.cancel()
            sys.exit(1)
        except:
            print("Something went wrong, restarting discord bot in 10 seconds.")
            steamCommunityNewsBot.bot.loop.run_until_complete(steamCommunityNewsBot.bot.logout())
            send_new_announcements_task.cancel()
            time.sleep(10)
        finally:
            steamCommunityNewsBot.bot.loop.close()
