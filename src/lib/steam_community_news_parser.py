import urllib
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup


def getLatestAccouncement(url):
    """
    Given a steam community URL find the details about the latest announcement.
    :param url: URL to a steam community which the latest announcement is desired
    :return: The latest announcement information for the provided URL
    """
    latestAccouncement = {"title": None, "info": None, "date": None, "url": None, "img_url": None}

    # Make request to grab community news from steam
    try:
        request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        source = urlopen(request).read()
        bsoup = soup(source, "html.parser")
        announcmentCards = bsoup.findAll('div', {'class': lambda x: x and 'Announcement_Card' in x.split()})
    except:
        raise Exception("Couldn't connect connect to URL.")

    # get latest anncouncment card information
    try:
        latestAccouncement["title"] = \
            announcmentCards[0].findAll("div", class_="apphub_CardContentNewsTitle")[0].contents[0]
        latestAccouncement["date"] = announcmentCards[0].findAll("div", class_="apphub_CardContentNewsDate")[0].text
        latestAccouncement["img_url"] = announcmentCards[0].findAll("img")[0].attrs["src"]
        latestAccouncement["url"] = announcmentCards[0].attrs["data-modal-content-url"]
        latestAccouncement["info"] = announcmentCards[0].findAll("div", class_="apphub_CardTextContent")[0].get_text(
            separator="\n")
        # trim message to only limited characters because discord limits them
        if len(latestAccouncement["info"]) > 2047:
            trimmedStr = latestAccouncement["info"][:2044] + "..."
            latestAccouncement["info"] = trimmedStr
    except:
        raise Exception("Error retrieving announcement information title.")

    return latestAccouncement


def getCommunityName(url):
    """
    Given a steam community URL, find the name of the community which is associated with it.
    :param url: URL to a steam community which the name of the community is desired
    :return: the name of the steam community for the provided URL
    """
    communityname = None
    try:
        request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        source = urlopen(request).read()
        bsoup = soup(source, "html.parser")
        communityname = bsoup.findAll('title')[0].text
    except:
        raise Exception("Error retrieving community name!")

    return communityname
