from shuffle import riffle
from random import SystemRandom
import Image
#Questions to ask:
#How do I shuffle? Do I shuffle physically accurately or do I use random.shuffle?
#Going along with that question, do I want everything to be physically accurate or do I want it to be fast?
#It would be fun to make it physically accurate.
#Should I have someone "shuffle" the deck?
#SystemRandom is the best source of true random numbers.
random = SystemRandom()
deck = []
stack1 = []
stack2 = []
for n in range(52):
	deck.append(n)
# def shuffle(n):
# 	global stack1, stack2, deck
# 	for i in range(n):
# 		stack1 = deck[:len(deck)/2]
# 		stack2 = deck[len(deck)/2:]
# 		deck = []
# 		while len(stack1)+len(stack2)>0:
# 			if random.getrandbits(1):
# 				if len(stack1)>0:
# 					deck.append(stack1.pop())
# 			else:
# 				if len(stack2)>0:
# 					deck.append(stack2.pop())
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
#random.shuffle(deck)
shuffle(7)
