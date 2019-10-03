from datetime import date, datetime
from pytz import timezone
import requests
import json
import time
import praw
import ast
import os

def redditConnect():
    print("Connecting to reddit...")

    # set praw variables and connect to subreddit
    global sub
    global r
    global subreddit
    sub = "ShotGlassBets"
    r = praw.Reddit("bot1")
    subreddit = r.subreddit(sub)
    print("Connected!\n")

def removePosts():
    print("Removing posts > 1.5 days old and with 0 comments")

    # set counters to 0
    i = 0
    zeroComCount = 0

    # pull new submissions
    for submission in subreddit.new(limit = 37): ##### change to 30 after 1st run
        # get post info
        numCom = submission.num_comments
        postTitle = submission.title
        postAuthor = submission.author
        username = "ShotGlassBets_Bot"

        # set recency check
        unixTime = time.time()
        unixDay = 86400
        checkTime = unixTime - (unixDay * 1.5)
        createdTime = submission.created_utc

        # check to see if post > 1.5 days old, if it's not stickied, and if the bot posted it
        if (checkTime > createdTime) and (submission.stickied == False) and (postAuthor == username):
            i += 1

            # now check to see which of those posts had 0 comments and remove them
            if (numCom == 0):
                zeroComCount += 1
                submission.mod.remove()
                print("Removed:", postTitle,)
    print(zeroComCount, "of", i, "posts had 0 comments\n")

def postNHLThreads():
    print("Creating posts for /r/", sub)

    # get dates and set date formats
    today = date.today()
    longDay = str(today)
    simpleDay = str(today.strftime("%-m/%-d"))
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
    gameCount = 0

    # check each game to create a title and post to reddit
    for game in games:
        gameCount += 1
        rawGameDate = datetime.strptime(game["gameDate"], "%Y-%m-%dT%H:%M:%SZ")
        cleanGameDate = rawGameDate.replace(tzinfo = timezone("UTC"))
        easternGameDate = cleanGameDate.astimezone(timezone("US/Eastern"))
        cleanTime = easternGameDate.strftime(timeFormat)
        teamDict = game["teams"]
        awayTeam = teamDict["away"]["team"]["name"]
        homeTeam = teamDict["home"]["team"]["name"]
        title = "[" + simpleDay + "] " + homeTeam + " vs " + awayTeam + " (" + cleanTime + ")"

        # submit post to reddit
        subreddit.submit(title, selftext = "", url=None, resubmit=True, send_replies=False).mod.flair(text = "NHL")
        print("Posted:", title)
    print(gameCount, "posts submitted\n")

# run code
redditConnect()
removePosts()
postNHLThreads()
