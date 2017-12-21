import time, datetime, json, re, os, random, sys
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

#print ("-----------------START-----------------")
#print (str(datetime.datetime.now()))
#print ("Now: "+now.strftime('%m/%d/%Y %H%M%S')+" and Then: "+then.strftime('%m/%d/%Y %H%M%S'))

# ----Useful Variables----

runCount = 1
watchedTS = {} # Dictionary object for tracking the most recently reviewed message in each group using the Group ID as index

#########################################################################
##################  SETUP THESE VARIABLES FOR EACH BOT ##################

# Set your User Token for the appropriate Slack team (each team has it's own)
userToken = "xoxp-8686754065-8707667493-151099928103-378724e0be610791c775d7c0c3f54256" 

# Create variables for each of your gropus/channels you might want the bot to watch
socialRockstarsID = "G09E3SGEQ"
brianPlaygroundID = "G1Y1HRYEP"
eucGurusID = "G1HTXUX3L"
vdiBitchingID = "G0KLMHJUS"
politicsID = "G3UUUTFV2"

# Add the group/channel variables to watchedGroupArray to enable the bot to watch
watchedGroupArray = [brianPlaygroundID, politicsID] # Array of all the groups for this bot to watch

# Create the personality of the bot (avatar and name)
botAvatar = "https://68.media.tumblr.com/avatar_2ffaeb9f55ec_128.png"
botName = "Donald Drumpf"

# Create list of words the bot should react to
reactionWords = ["donald","trump","drumpf"]

# Create a list of context aware words to narrow down the responses
subReactionWords = ["ivanka","dutch","iq","women","hilary","twitter","rocket"]

# Create list of pseudo-quotes the bot should react with (use 'username' if you want the bot to react to the author of the post)
botQuotesFile = file('TrumpQuotes.txt','r')
botQuotes = botQuotesFile.readlines()
#botQuotes = ["So, I hear the Dutch have _the best_ wishes. They're great.  It is true.", 
#				"An extremely credible source has called my office and told me that username's birth certificate is a fraud",
#				"Nobody builds walls better than me, believe me.",
#				"The beauty of me is that I am very rich.",
#				"One of they key problems today is that politics is such a disgrace. Good people don't go into government.",
#				"My fingers are long and beautiful, as, it has been well documented, are various other parts of my body.",
#				"I've said if Ivanka weren't my daughter, perhaps I'd be dating her.",
#				"I think the only difference between me and the other candidates is that I'm more honest and my women are more beautiful.",
#				"My Twitter has become so powerful that I can actually make my enemies tell the truth.",
#				"My IQ is one of the highest - and you all know it! Please don't feel so stupid or insecure; it's not your fault.",
#				"Thanks sweetie. That's nice.",
#				"Number one, I have great respect for women. I was the one that really broke the glass ceiling on behalf of women, more than anybody in the construction industry.",
#				"You know, it really doesn't matter what the media write as long as you've got a young, and beautiful, piece of ass."]

#################################### END VARIABLE SETUP ####################################
############################################################################################

# Open tracking file
#messageTracker = file('trumpBotMessageTracker.txt','w')



recentTS = time.mktime(then.timetuple())
#print ("Starting at timestamp: "+str(recentTS))

# Set the starting timestamp for each group in the watched group timestamp dictionary
for watchedGroup in watchedGroupArray:
	watchedTS[watchedGroup] = recentTS

# Open up Slack
sc = SlackClient(userToken)
#print (sc.api_call("api.test"))

# Get me the list of (public) channels
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

	# 			# Check to see if any of the reaction words are used in the message
	# 			if ("dheeraj" in messageText.lower()) or ("pandey" in messageText.lower()):
				if (any(substring.lower() in messageText.lower() for substring in reactionWords)):
					print (userName+" used "+str(reactionWords)+" in: '"+messageText+"'")

	# 				# Create message
	# 				#print ("Full list: " + str(len(abeQuotes)))

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




						#filteredQuotes = [quote for quote in botQuotes if (any(substring in quote for substring in matchedSubReactionWords))]


						#print (str(filteredQuotes))


					# Use if construct to provide context aware responses for special words
					# if "fpga" in messageText.lower():
					# 	filteredQuotes = [quote for quote in botQuotes if ("fpga" in quote.lower())]
						
	# 				elif "baloney" in messageText.lower():
	# 					filteredQuotes = [quote for quote in abeQuotes if ("baloney" in quote.lower())]
						
	# 				elif "invisible" in messageText.lower():
	# 					filteredQuotes = [quote for quote in abeQuotes if ("invisible" in quote.lower())]
						
	# 				elif "webscale" in messageText.lower():
	# 					filteredQuotes = [quote for quote in abeQuotes if ("webscale" in quote.lower())]
								
	# 				elif "women" in messageText.lower():
	# 					filteredQuotes = [quote for quote in abeQuotes if ("women" in quote.lower())]

	# 				elif "spof" in messageText.lower():
	# 					filteredQuotes = [quote for quote in abeQuotes if ("spof" in quote.lower())]
						
	# 				elif "vmware" in messageText.lower():
	# 					filteredQuotes = [quote for quote in abeQuotes if ("vmware" in quote.lower())]

	# 				elif "people" in messageText.lower():
	# 					filteredQuotes = [quote for quote in abeQuotes if ("spof" in quote.lower())]

	# 				elif "middle" in messageText.lower():
	# 					filteredQuotes = [quote for quote in abeQuotes if ("middle" in quote.lower())]

	# 				elif "fud" in messageText.lower():
	# 					filteredQuotes = [quote for quote in abeQuotes if ("fud" in quote.lower())]

	# 				elif "compet" in messageText.lower():
	# 					filteredQuotes = [quote for quote in abeQuotes if ("compet" in quote.lower())]
						
					else:
						filteredQuotes = botQuotes

					# Let's review the list we created
					print ("Filtered list: " + str(len(filteredQuotes)))

					# Create random index number based on the size of the quotes list to randomly select response
					randomIndex = random.randint(0,len(filteredQuotes)-1)
					
	# 				print (randomIndex)
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

	# Maintain run count
	runCount += 1

	# Take a break and wait for some more messages
	#time.sleep(30)

#print ("-----------------END-----------------")
print ("")


#messageTracker.close()
sys.stdout = orig_stdout
sys.stderr = orig_stderr
f.close()
