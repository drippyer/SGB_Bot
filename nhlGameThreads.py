import requests
import json
from datetime import date
from datetime import datetime
import time
from pytz import timezone
import ast
import os
import praw

# get dates and set date formats
today = date.today()
longDay = str(today)
simpleDay = str(today.strftime("%-m/%d"))
dateFormat = "%Y-%m-%d %H:%M:%S %Z%z"
timeFormat = "%-I:%M %p %Z"
cwd = os.getcwd()

# create today's URL for API call
baseURL = "https://statsapi.web.nhl.com/api/v1"
todaySchedURL = baseURL + "/schedule?date=" + longDay

# pull game info
response = requests.get(todaySchedURL)
response = response.json()
dates = response["dates"]
datesString = str(dates[0])
datesDict = ast.literal_eval(datesString)
games = datesDict["games"]

# connect to reddit
sub = "ShotGlassBets"
r = praw.Reddit('bot1')
subreddit = r.subreddit(sub)

# check each game to create a title and post to reddit
for game in games:
    rawGameDate = datetime.strptime(game["gameDate"], "%Y-%m-%dT%H:%M:%SZ")
    cleanGameDate = rawGameDate.replace(tzinfo=timezone('UTC'))
    easternGameDate = cleanGameDate.astimezone(timezone('US/Eastern'))
    cleanTime = easternGameDate.strftime(timeFormat)
    teamDict = game["teams"]
    awayTeam = teamDict["away"]["team"]["name"]
    homeTeam = teamDict["home"]["team"]["name"]
    title = "[" + simpleDay + "] " + homeTeam + " vs " + awayTeam + " (" + cleanTime + ")"
    # submit post to reddit
    subreddit.submit(title, selftext="", url=None, flair_id=None, flair_text=None, resubmit=True, send_replies=False, nsfw=False, spoiler=False, collection_id=None)
    print("Posted \"" + title + "\" to /r/" + sub)