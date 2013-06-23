import twitter
api = twitter.Api()
user = "Zipwhip"
statuses = api.GetUserTimeline(user)
txt = statuses[0].text
print txt
print len(txt)
#print [s.text for s in statuses]