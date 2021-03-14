import unittest

import src.lib.steam_community_news_parser as parser

class MyTestCase(unittest.TestCase):

 def test_getLatestAccouncement(self):

     print("\nTest1:")
     print("Testing: getLatestAccouncement Function...")

     result = parser.getLatestAccouncement("https://steamcommunity.com/app/413150/")
     print("Result: ", result)


     Check_latestAccouncement = {"title": None, "info": None, "date": None, "url": None, "img_url": None}
     self.assertNotEqual(result,Check_latestAccouncement)
  #   print("Testing Finished")

 def test_getCommunityName(self):
    print("\nTest2:")
    print("Testing: getCommunityName Function...")

    result = parser.getCommunityName("https://steamcommunity.com/app/413150/")
    print("Result: ", result)

    check_communityname = "Steam Community :: Stardew Valley"
    self.assertEqual(result,check_communityname)
 #   print("Testing Finished")
