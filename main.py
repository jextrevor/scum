from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import eventlet
from gevent import monkey
app = Flask(__name__)
socketio = SocketIO(app)
#from shuffle import riffle
from random import SystemRandom
#import Image
#Questions to ask:
#How do I shuffle? Do I shuffle physically accurately or do I use random.shuffle?
#Going along with that question, do I want everything to be physically accurate or do I want it to be fast?
#It would be fun to make it physically accurate.
#Should I have someone "shuffle" the deck?
#SystemRandom is the best source of true random numbers.
random = SystemRandom()
players = 0
deck = []
stack1 = []
stack2 = []
stacks = []
havepassed = []
card = 0 #Current card, or 1 for passing cards or 0 for blank.
passed = 0
playerpos = []
nextplayerpos = []
playernames = []
player = 0 #Current player
lastplayer = -1
def clear():
	global deck, stack1, stack2
	deck = []
	stack1 = []
	stack2 = []
	for x in range(4):
		for n in range(2,15):
			deck.append(n)
def position():
	t = 0
	for i in range(52):
		t += random.getrandbits(1);
	return t
def split(position):
	global deck, stack1, stack2
	stack1 = deck[:position]
	stack2 = deck[position:]
	deck = []
def fall():
	global deck, stack1, stack2
	if len(stack1) > 0 and random.random()<float(len(stack1))/(len(stack1)+len(stack2)):
		deck.append(stack1.pop(0))
	else:
		deck.append(stack2.pop(0))
def riffle():
	global deck, stack1, stack2
	while len(stack1)+len(stack2) > 0:
		fall()
def shuffle(n):
	for x in range(n):
		split(position())
		riffle()
def deal(stacks):
	while len(deck) > 0:
		for x in range(len(stacks)):
			if len(deck) > 0:
				stacks[x].append(deck.pop())
	for x in range(len(stacks)):
		stacks[x].sort()
def switch():
	global stacks
	stackstemp = stacks
	for x in range(players):
		stacks.append([])
	for x in range(players):
		stacks[playerpos[x]] = stackstemp[x]
def setup(p):
	global players, stacks, playerpos, havepassed
	players = p
	stacks = []
	for x in range(p):
		stacks.append([])
	playerpos = range(players)
	havepassed = []
	for x in range(players):
		havepassed.append(0)
	#playerpos = [2,0,1]
def clearData():
	global card, playerpos, playernames, player, players, havepassed
	card = 0
	playerpos = range(players)
	#playerpos = [2,0,1]
	playernames = []
	nextplayerpos = []
	for x in range(players):
		playernames.append("Player "+str(x+1))
	player = 0
	lastplayer = -1
	passed = 0
	havepassed = []
	for x in range(players):
		havepassed.append(0)
def updateHands():
	global stacks
	socketio.emit("hands",{"stacks":stacks},namespace="/main")
def updateData():
	global card, playerpos, playernames, player, players
	socketio.emit('players',{"players":players},namespace='/main')
	socketio.emit('playernames',{"playernames":playernames},namespace='/main')
	socketio.emit('playerpos',{"playerpos":playerpos},namespace='/main')
	socketio.emit('player',{"player":player},namespace='/main')
	socketio.emit('card',{"card":card},namespace='/main')
	updateHands()
def doshuffle():
	clear()
	shuffle(7)
def domessage(message):
	with open("log.txt","a") as myfile:
		myfile.write(message+"\n")
	socketio.send(message,namespace="/main")
setup(4)
doshuffle()
deal(stacks)
switch()
clearData()
updateData()
@socketio.on('connect', namespace='/main')
def connect():
	print "hi"
	updateData()
	domessage("One player connected.")
@socketio.on('disconnect', namespace='/main')
def disconnect():
	domessage("One player disconnected.")
@socketio.on('message', namespace='/main')
def message(msg):
	domessage(msg)
@socketio.on('play', namespace='/main')
def playcard(data):
	global card, player, lastplayer, havepassed, playerpos
	if card == 1:
		#If passing cards, determine how many cards have been passed and how many are remaining.
		#Also determine player.
		#Return.
		pass
	if data["player"] != player:
		return
	if data["mode"] == 0:
		if lastplayer == -1:
			domessage("Cannot pass.")
			return
		havepassed[player] = True
		while True:
			if playerpos.index(player)+1 == players:
				player = playerpos[0]
			else:
				player = playerpos[playerpos.index(player)+1]
			if len(stacks[player]) == 0:
				continue
			if havepassed[player]:
				continue
			if player == lastplayer:
				lastplayer = -1
				card = 0
				havepassed = []
				for x in range(players):
					havepassed.append(0)
				domessage(playernames[player]+" won the round.")
			break
		updateData()
	else:
		print "hi"
		if stacks[player].count(data["card"]) < data["mode"]:
			domessage("Insufficient cards.")
			return;
		if card != 0:
			if not data["card"] > card[0]:
				domessage("Card not high enough.")
				return;
			if not data["mode"] == card[1]:
				domessage("Number of cards not matching.")
				return;
		card = [data["card"],data["mode"]]
		domessage(playernames[player]+" played "+str(data["mode"])+" "+str(data["card"])+"'s.")
		for n in range(data["mode"]):
			stacks[player].remove(data["card"])
		if len(stacks[player]) == 0:
			nextplayerpos.append(player)
		lastplayer = player
		if all(len(stack) == 0 for stack in stacks):
			playerpos = nextplayerpos
			nextplayerpos = []
			doshuffle()
			deal(stacks)
			switch()
			#Give two top cards of last player to first player.
			#Give top card of second to last player to second player.
			card = 1
		else:
			while True:
				if playerpos.index(player)+1 == players:
					player = playerpos[0]
				else:
					player = playerpos[playerpos.index(player)+1]
				if len(stacks[player]) == 0:
					continue
				print havepassed
				if havepassed[player]:
					continue
				if player == lastplayer:
					lastplayer = -1
					card = 0
					havepassed = []
					for x in range(players):
						havepassed.append(0)
					domessage(playernames[player]+" won the round.")
				break
			updateData()
@socketio.on('players', namespace='/main')
def updateplayers(data):
	domessage("Reformatting for "+str(data["players"])+" players...")
	setup(int(data["players"]))
	doshuffle()
	deal(stacks)
	switch()
	clearData()
	updateData()
	domessage("Ready.")
@socketio.on('name', namespace="/main")
def updatename(data):
	global playernames
	domessage("Changing name of player "+str(data["number"]+1)+" to "+data["name"]+"...")
	playernames[data["number"]] = data["name"]
	updateData()
	domessage("Ready.")
@app.route("/")
def vote():
	templateData = {}
	return render_template("main.html",**templateData)
@app.after_request
def no_cache(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-cache, no-store'
    response.headers['Pragma'] = 'no-cache'
    return response
if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", 3000)