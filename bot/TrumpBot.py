import time, datetime, json, re, os, random, sys, ConfigParser
from slackclient import SlackClient

# Time Management
now = datetime.datetime.now()
then = now - datetime.timedelta(minutes=1)

# Redirect stdout
orig_stdout = sys.stdout
f = file('trumpBotOutput.txt','a')
sys.stdout = f

# Redirect stderr
orig_stderr = sys.stderr
sys.stderr = f

print ("-----------------START-----------------")
#print (str(datetime.datetime.now()))
#print ("Now: "+now.strftime('%m/%d/%Y %H%M%S')+" and Then: "+then.strftime('%m/%d/%Y %H%M%S'))

# ----Useful Variables----
runCount = 1   # Used to control the looping of this script. See the end to determine if script runs continuously or once per execution (when using a scheduled task).
watchedTS = {} # Dictionary object for tracking the most recently reviewed message in each group using the Group ID as index.

#########################################################################
##################   RETRIEVE AND SETUP THE VARIABLES  ##################

# Retrieve ini file configurations
config = ConfigParser.ConfigParser()
config.read('TrumpBot.ini')
#print (config.get("TrumpBot","userToken"))
	
# Set your User Token for the appropriate Slack team (each team has it's own)
userToken = config.get("TrumpBot","userToken")

# Add the group/channel IDs to watchedGroupArray to enable the bot to watch
watchedGroupArray = config.get("TrumpBot","watchedGroupList").split(",")

# Create the personality of the bot (avatar and name)
botAvatar = config.get("TrumpBot","botAvatar")
botName = config.get("TrumpBot","botName")

# Create list of words the bot should react to
reactionWords = config.get("TrumpBot","reactionWords").split(",")

# Create a list of context aware words to narrow down the responses
subReactionWords = config.get("TrumpBot","subReactionWords").split(",")

# Retrieve list of quotes the bot should react with (use 'username' if you want the bot to react to the author of the post)
botQuotesFile = file(config.get("TrumpBot","botQuotesFile"),'r')
botQuotes = botQuotesFile.readlines()

#################################### END VARIABLE SETUP ####################################
############################################################################################


recentTS = time.mktime(then.timetuple())
#print ("Starting at timestamp: "+str(recentTS))

# Set the starting timestamp for each group in the watched group timestamp dictionary
for watchedGroup in watchedGroupArray:
	watchedTS[watchedGroup] = recentTS

# Open up Slack
sc = SlackClient(userToken)
#print (sc.api_call("api.test"))

# Get the list of (public) channels
channelObj = sc.api_call("channels.list")
channels = channelObj["channels"]
#for channel in channels:
#	print (channel["name"]+" - "+channel["id"])

# Get me the list of (private) groups
groupObj = sc.api_call("groups.list")
groups = groupObj["groups"]
#for group in groups:
#	print (group["name"]+" - "+group["id"])

#print ("Watching these group IDs: "+str(watchedGroupArray))

# Let's do the timewarp again (and again, and again...)
while runCount == 1:
	#print ("")
	#print ("---------------Run #"+str(runCount)+" at "+str(datetime.datetime.now()))
	print ("---------------Run at "+str(datetime.datetime.now()))

	for watchedGroup in watchedGroupArray:
		print ("----------Group: "+watchedGroup)

		# Get the most recent group of messages since the most recently processed timestamp
		try:
			messagesObj = sc.api_call("groups.history",channel=watchedGroup,oldest=watchedTS[watchedGroup],unreads=1)
		except:
			# Reospen up Slack
			sc = SlackClient(userToken)
			messagesObj = sc.api_call("groups.history",channel=watchedGroup,oldest=watchedTS[watchedGroup],unreads=1)

		#print ("Messages Obj: "+str(messagesObj))

		if (messagesObj["ok"] == False):
			#print ("all good")
			messagesObj = sc.api_call("channels.history",channel=watchedGroup,oldest=watchedTS[watchedGroup],unreads=1)

		# Extract only the messages array
		messages = messagesObj["messages"]

		#print (len(messages)-1)

		# Loop through all the messages
		for message in messages:
			# Check to make sure it's actually a message type message
			if message["type"]=="message":
				# Extract the text of the message
				messageText = re.sub(u"(\u2018|\u2019|\u201c|\u2026|\u201d|\xaf|\u30cf|\u30c4|\u2022|\u2014)","", message["text"])

				# Reset the potential quotes that could be used
				filteredQuotes = []

				# Extract the user ID (defaults to Anonymous if it doesn't exist)
				userName = message.get("user","Anonymous")

				if userName!="Anonymous":
					# Get the user info based on the user ID and pull out the actual username
					userInfo = sc.api_call("users.info",user=userName)
					userName = userInfo["user"]["name"]
				
				#print ("-----Message:")	
				#print (userName+": "+messageText)

	 			# Check to see if any of the reaction words are used in the message
				if (any(substring.lower() in messageText.lower() for substring in reactionWords)):
					print (userName+" used "+str(reactionWords)+" in: '"+messageText+"'")

	 				# Select a reply message
	 				#print ("Full list: " + str(len(botQuotes)))

					if (any(substring.lower() in messageText.lower() for substring in subReactionWords)):
						matchedSubReactionWords = [triggerWord for triggerWord in subReactionWords if (triggerWord.lower() in messageText.lower())]

						print ("Matched subReactionWords: "+str(matchedSubReactionWords))

						for reactionWord in matchedSubReactionWords:
							#print ("--"+reactionWord)
							for quote in botQuotes:
								#print ("-"+quote)
								if (reactionWord.lower() in quote.lower()):
									#print ("************Match!")
									filteredQuotes.append(quote)
					else:
						filteredQuotes = botQuotes
						
					if (len(filteredQuotes) <= 0):
						filteredQuotes = botQuotes

					# Let's review the list we created
					print ("Filtered list: " + str(len(filteredQuotes)))

					# Create random index number based on the size of the quotes list to randomly select response
					randomIndex = random.randint(0,len(filteredQuotes)-1)
					
	 				#print ("Random number selected: " + RandomIndex)
					replyMessage = re.sub("username",userName,filteredQuotes[randomIndex])

					# Post a reply in the room
					sc.api_call("chat.postMessage",
						channel=watchedGroup,
						text=replyMessage,
						username=botName,
						as_user="false",
						icon_url=botAvatar)

			# Track the timestamp as the most recent, but only if this message is more recent than the previous message(s)
			if float(watchedTS[watchedGroup]) < float(message["ts"]):
				watchedTS[watchedGroup] = message["ts"]
				#print ("Stored message TS"+message["ts"])
				#messageTracker.write(message["ts"])

	# Maintain run count - Comment out this line if you want the script to run continuously. I have found that this will cause the script to fail due to too many connection attempts to Slack API.
	runCount += 1

	# Take a break and wait for some more messages - Useful when you comment out the line above to run the script continuously.
	#time.sleep(30)

#print ("-----------------END-----------------")
print ("")


#messageTracker.close()
sys.stdout = orig_stdout
sys.stderr = orig_stderr
f.close()
