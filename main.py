from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import sys
import os
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
	stacks = []
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
	global card, playerpos, playernames, player, players, havepassed, passed
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
clearData()
doshuffle()
deal(stacks)
switch()
updateData()
@socketio.on('connect', namespace='/main')
def connect():
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
	global card, player, lastplayer, havepassed, playerpos, nextplayerpos, passed
	if card == 1:
		if data["player"] != player:
			return
		if data["mode"] == 0:
			domessage("Cannot pass.")
			return
		if data["mode"] > 1:
			domessage("Cards must be passed one at a time.")
			return
		if data["card"] not in stacks[player]:
			domessage("Insufficient cards.")
			return
		a = 1
		if passed == 2:
			a = 2
		stacks[playerpos[players-a]].append(data["card"])
		stacks[player].remove(data["card"])
		if passed == 2:
			player = playerpos[0]
			card = 0
			passed = 0
			stacks[playerpos[players-1]].sort()
			stacks[playerpos[players-2]].sort()
			updateData()
			return
		if passed == 1:
			player = playerpos[1]
			passed = 2
			updateData()
			return
		if passed == 0:
			passed = 1
			updateData()
			return
		updateData()
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
			
			if havepassed[player]:
				continue
			if player == lastplayer:
				lastplayer = -1
				card = 0
				havepassed = []
				for x in range(players):
					havepassed.append(0)
				domessage(playernames[player]+" won the round.")
				if len(stacks[player]) == 0:
					continue
			if len(stacks[player]) == 0:
				continue
			break
		updateData()
	else:
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
			a1 = max(stacks[playerpos[players-1]])
			b1 = max(stacks[playerpos[players-2]])
			stacks[playerpos[0]].append(a1)
			stacks[playerpos[players-1]].remove(a1)
			a2 = max(stacks[playerpos[players-1]])
			stacks[playerpos[0]].append(a2)
			stacks[playerpos[players-1]].remove(a2)
			stacks[playerpos[1]].append(b1)
			stacks[playerpos[players-2]].remove(b1)
			stacks[playerpos[0]].sort()
			stacks[playerpos[1]].sort()
			for x in range(len(stacks)):
				stacks[x].sort()
			card = 1
			player = playerpos[0]
			updateData()
		else:
			while True:
				if playerpos.index(player)+1 == players:
					player = playerpos[0]
				else:
					player = playerpos[playerpos.index(player)+1]
				
				if havepassed[player]:
					continue
				if player == lastplayer:
					lastplayer = -1
					card = 0
					havepassed = []
					for x in range(players):
						havepassed.append(0)
					domessage(playernames[player]+" won the round.")
					if len(stacks[player]) == 0:
						continue
				if len(stacks[player]) == 0:
					continue
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
    if 'PORT' in os.environ:
        socketio.run(app, "0.0.0.0",int(os.environ['PORT']))
    else:
        socketio.run(app, "0.0.0.0", 3000)
