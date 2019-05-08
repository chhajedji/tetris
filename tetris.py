#!/usr/bin/python3
import sys, random, pygame, collections, time

from collections import namedtuple
from pygame.locals import *

FPS = 25

movedown_event = pygame.USEREVENT+1
pygame.time.set_timer(movedown_event, 1000)

filled = [[0 for x in range(10)] for y in range(20)]
emptyrow = [0 for foo in range(10)]
toprow = 19

GREY     = (224, 224, 224) 
NAVYBLUE = ( 60,  60, 100)
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)

t =		[[0, 1, 0],
		 [1, 1, 1], 
		 [0, 0, 0]]
s =		[[0, 1, 1], 
		 [1, 1, 0],
		 [0, 0, 0,]]
z =		[[0, 0, 0],
		 [1, 1, 0],
		 [0, 1, 1]]
o =		[[1, 1, 0],
		 [1, 1, 0],
		 [0, 0, 0]]
i =		[[0, 0, 1, 0] for c in range(4)]
j =		[[0, 1, 0],
		 [0, 1, 0],
		 [1, 1, 0]]
l =		[[0, 1, 0],
		 [0, 1, 0],
		 [0, 1, 1]]

T, S, Z, O, I, J, L = 't', 's', 'z', 'o', 'i', 'j', 'l'
nameshapemap = {T:t, S:s, Z:z, O:o, I:i, J:j, L:l}
colors = (NAVYBLUE, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
shapes = (T, S, Z, O, I, J, L)
BGCOLOR = WHITE

GAMEWINDOWTOP = 10
GAMEWINDOWLEFT = 10
GAMEWINDOWWIDTH = 200
GAMEWINDOWHEIGHT = 400
BLOCKSIZE = 20
BLOCK = 1
# global pos,lmargin, rmargin,  nextblock, currentblock
global currentblock
DEFAULTPOS = (10+4*BLOCKSIZE, -10)				#starting posttion
pos = DEFAULTPOS
lmargin, rmargin = pos[0], pos[0]+3*BLOCKSIZE
nextblock = None

def main():
	global pos, surf, newblock, lmargin, rmargin, currentblock, nextblock
	pygame.init()
	fpsclock = pygame.time.Clock()
	surf = pygame.display.set_mode((400, 420))
	pygame.display.set_caption('Tetris')
	newblock = namedtuple('Block', 'name shape color angle')

	surf.fill(BGCOLOR)
	# rb = newblock(T, t, RED, 0)		#test case
	sendnew()
	while True:

		for event in pygame.event.get():
			if (event.type == QUIT):
				pygame.quit()
				sys.exit()
			
			elif (event.type == movedown_event):
				pos = movedown(pos)

			elif (event.type == KEYDOWN):

				if(event.key == K_ESCAPE):
					pygame.quit()
					sys.exit()

				elif(event.key == K_UP):
					currentblock = rotate(currentblock)
					lmargin = leftmargin(currentblock, pos[0])
					rmargin = rightmargin(currentblock, pos[0])
					if 10 > lmargin or 10+10*BLOCKSIZE < rmargin:
						currentblock = rotate(currentblock)
						currentblock = rotate(currentblock)
						currentblock = rotate(currentblock)

				elif(event.key == K_RIGHT):
					pos = moveright(currentblock, pos)
					# pos = moveright(rb, pos)			#test case

				elif(event.key == K_LEFT):
					pos = moveleft(currentblock, pos)
					# pos = moveleft(rb, pos)				#test case
		
		pressed = pygame.key.get_pressed()
		if pressed[K_DOWN]:
			pos = movedown(pos)

		surf.fill(BGCOLOR)
		pygame.draw.rect(surf, BLACK, (GAMEWINDOWTOP, GAMEWINDOWLEFT, GAMEWINDOWWIDTH, GAMEWINDOWHEIGHT), 1)
		pygame.draw.rect(surf, BLACK, (250, 50, 130, 130), 1) #side window for next block
		#displayfilled()
		writetext()

		draw(currentblock.name, currentblock.color, currentblock.angle, pos)
		draw(nextblock.name, nextblock.color, nextblock.angle, (280, 80))

		b = bottom(currentblock, pos, filled)
		print('bottom(current block) = ', b, "toprow: ", toprow)
		if b == pos:
			updatefilled(currentblock, pos, filled)
			displayfilled()
			pos = DEFAULTPOS
		fpsclock.tick(FPS)
		displayfilled()
		showgrid()
		pygame.display.update()

def dispblock(e, x, y):		#display color 'e' at x, y
	if e == 0:
		return
	pygame.draw.rect(surf, e, (10+y*BLOCKSIZE, 10+x*BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))

def bottom(block, pos, filled):			#returns bottommost position of current block
	global lmargin, rmargin, toprow
	down = [20, 20, 20, 20]			#row no. of bottommost position of current block
	lmargin, rmargin = leftmargin(block, pos[0]), rightmargin(block, pos[0])
	#print('filled = ',filled)
	#print("lmargin, rmargin: ", int((lmargin-10)/BLOCKSIZE), int((rmargin-10)/BLOCKSIZE))
	#print("col range:", int((lmargin-10)/BLOCKSIZE), int((rmargin-10)/BLOCKSIZE))
	for col in range(int((lmargin-10)/BLOCKSIZE), int((rmargin-10)/BLOCKSIZE)):
		for row in range(20):
			if filled[row][col] != 0:
				down[int(col-((lmargin-10)/BLOCKSIZE))] = row
				break
	winner = min(down)*BLOCKSIZE+10
	for foo in range((winner +5*BLOCKSIZE), (winner - 5*BLOCKSIZE), -BLOCKSIZE):		#trial for block's depth coordinate
	#for foo in range((10+(row-1)*BLOCKSIZE), (10+(row-5)*BLOCKSIZE), -BLOCKSIZE):		#trial for block's depth coordinate
		if bottommargin(block, foo) == winner:
			newpos = (pos[0], foo)
			break
	
	#print("current pos: ", int(pos[0]/BLOCKSIZE-0.5), int(pos[1]/BLOCKSIZE-0.5), " bottom pos: ", int(newpos[0]/BLOCKSIZE-0.5), int(newpos[1]/BLOCKSIZE-0.5))
	return newpos

def displayfilled():		#display the filled elements on screen
	global toprow, filled
	x = 0
	for row in filled:
		y = 0
		for e in row:
			dispblock(e, x, y)
			y += 1
		x += 1

def delcompletelines():
	global filled, toprow
	for row in filled[toprow:]:
		delflag = 1
		for e in row:
			if e == 0:
				delflag = 0
				break
		if delflag == 1:
			del filled[filled.index(row)]
			filled.insert(0, emptyrow)

def addnew(block, pos, filled):			#add a block to filled
	col, row = int((pos[0]-10)/BLOCKSIZE), int((pos[1]-10)/BLOCKSIZE)
	global toprow
	toprow = row
	rownum = 0
	for r in block.shape:
		colnum = 0
		for c in r:
			if c == 1:
				filled[row+rownum][col+colnum] = block.color
			colnum += 1
		rownum += 1

def updatefilled(block, pos, filled):			#add new block, delete complete lines, check game over, send new block
	global toprow, emptyrow
	addnew(block, pos, filled)
	delcompletelines()
	if toprow <= 0:
		filled = [emptyrow for i in range(20)]		#game over
		toprow = 19
		return
	print("toprow: ", toprow)
	sendnew()


def movedown(pos):
	newpos = (pos[0], pos[1]+BLOCKSIZE)
	return newpos

def writetext():
	nexttextobj = pygame.font.SysFont('NotoSansLao-Regular', 36)
	titleobj = pygame.font.SysFont('NotoSansLao-Regular', 40)
	nextsurfobj = titleobj.render('Next', False, BLACK)
	titlesurfobj = titleobj.render('T E T R I S', False, BLACK)
	surf.blit(nextsurfobj, (270, 20))
	surf.blit(titlesurfobj, (220, 300))

def sendnew():
	global nextblock, currentblock
	if nextblock == None:
		newshape = shapes[random.randrange(len(shapes))]
		newcolor = colors[random.randrange(len(colors))]
		currentblock = newblock(newshape, nameshapemap[newshape], newcolor, 0)
		newshape = shapes[random.randrange(len(shapes))]
		nextblock = newblock(newshape, nameshapemap[newshape], colors[random.randrange(len(colors))], 0)

	else:
		currentblock = nextblock
		newshape = shapes[random.randrange(len(shapes))]
		newcolor = colors[random.randrange(len(colors))]
		nextblock = newblock(newshape, nameshapemap[newshape], newcolor, 0)

def moveleft(block, pos):
	lmargin = leftmargin(block, pos[0])
	if (lmargin <= 10):
		return pos
	if (filled[int((pos[1]-10)/BLOCKSIZE)][int((lmargin-10)/BLOCKSIZE-1)] != 0):
		return pos
	newpos = (pos[0]-BLOCKSIZE, pos[1])
	return newpos

def moveright(block, pos):
	rmargin = rightmargin(block, pos[0])
	if rmargin >= 10+10*BLOCKSIZE:
		return pos
	if (filled[int((pos[1]-10)/BLOCKSIZE)][int((rmargin+10)/BLOCKSIZE-1)] != 0):
		return pos
	newpos = (pos[0]+BLOCKSIZE, pos[1])
	return newpos

def bottommargin(b, y):
	if b.name == T:
		if b.angle == 0:
			return y+2*BLOCKSIZE
		return y+3*BLOCKSIZE
	elif b.name == O:
		return y+2*BLOCKSIZE
	elif b.name == S:
		if b.angle == 0:
			return y+2*BLOCKSIZE
		return y+3*BLOCKSIZE
	elif b.name == L:
		if b.angle == 270:
			return y+2*BLOCKSIZE
		return y+3*BLOCKSIZE
	elif b.name == Z:
		if b.angle == 180:
			return y+2*BLOCKSIZE
		return y+3*BLOCKSIZE
	elif b.name == J:
		if b.angle == 90:
			return y+2*BLOCKSIZE
		return y+3*BLOCKSIZE
	if b.angle == 90:
		return y+BLOCKSIZE*3
	elif b.angle == 270:
		return y+2*BLOCKSIZE
	return y+4*BLOCKSIZE

def leftmargin(b, x):
	if b.name == T:
		if b.angle == 90:
			return x+BLOCKSIZE
		return x 
	elif b.name == O:
		return x
	elif b.name == S:
		if b.angle == 90:
			return x+BLOCKSIZE
		return x
	elif b.name == L:
		if b.angle == 0:
			return x+BLOCKSIZE
		return x
	elif b.name == Z:
		if b.angle == 270:
			return x+BLOCKSIZE
		return x
	elif b.name == J:
		if b.angle == 180:
			return x+BLOCKSIZE
		return x
	if b.angle == 0:
		return x+BLOCKSIZE*2
	elif b.angle == 180:
		return x+BLOCKSIZE
	return x

def rightmargin(b, x):
	if b.name == T:
		if b.angle == 270:
			return x+2*BLOCKSIZE
		return x+3*BLOCKSIZE
	elif b.name == O:
		return x+2*BLOCKSIZE
	elif b.name == S:
		if b.angle == 270:
			return x+2*BLOCKSIZE
		return x+3*BLOCKSIZE
	elif b.name == L:
		if b.angle == 180:
			return x+2*BLOCKSIZE
		return x+3*BLOCKSIZE
	elif b.name == Z:
		if b.angle == 90:
			return x+2*BLOCKSIZE
		return x+3*BLOCKSIZE
	elif b.name == J:
		if b.angle == 0:
			return x+2*BLOCKSIZE
		return x+3*BLOCKSIZE
	if b.angle == 0:
		return x+BLOCKSIZE*3
	elif b.angle == 180:
		return x+2*BLOCKSIZE
	return x+4*BLOCKSIZE

def blockmatrixrotate(mat):
	soln = [row[:] for row in mat]
	m = len(mat[0])
	for c1 in range(0,m):
		for c2 in range(0,m):
			soln[c2][m-1-c1] = mat[c1][c2]
	return soln

def rotate(block):			#clockwise rotation
	if (block.shape == O):
		return block
	if(block.angle == 270):
		newangle = 0
		newshape = blockmatrixrotate(block.shape)
	else:
		newangle = block.angle+90
		newshape = blockmatrixrotate(block.shape)
	return (newblock(block.name, newshape, block.color, newangle))

def draw(name, color, angle, cords):
	(x, y) = cords
	if name == T:
		if angle == 0:
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, 3*BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, BLOCKSIZE))
		if angle == 90:
			pygame.draw.rect(surf, color, (x+2*BLOCKSIZE, y+BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, 3*BLOCKSIZE))
		if angle == 180:
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, 3*BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y+2*BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))
		if angle == 270:
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, 3*BLOCKSIZE))
	elif name == S:
		if angle == 0:
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, 2*BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, 2*BLOCKSIZE, BLOCKSIZE))
		if angle == 90:
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, 2*BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+2*BLOCKSIZE, y+BLOCKSIZE, BLOCKSIZE, 2*BLOCKSIZE))
		if angle == 180:
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y+BLOCKSIZE, 2*BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x, y+2*BLOCKSIZE, 2*BLOCKSIZE, BLOCKSIZE))
		if angle == 270:
			pygame.draw.rect(surf, color, (x, y, BLOCKSIZE, 2*BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y+BLOCKSIZE, BLOCKSIZE, 2*BLOCKSIZE))
	elif name == O:
		pygame.draw.rect(surf, color, (x, y, 2*BLOCKSIZE, 2*BLOCKSIZE))
	elif name == Z:
		if angle == 0:
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, 2*BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y+2*BLOCKSIZE, 2*BLOCKSIZE, BLOCKSIZE))
		if angle == 90:
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, 2*BLOCKSIZE))
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, BLOCKSIZE, 2*BLOCKSIZE))
		if angle == 180:
			pygame.draw.rect(surf, color, (x, y, 2*BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y+BLOCKSIZE, 2*BLOCKSIZE, BLOCKSIZE))
		if angle == 270:
			pygame.draw.rect(surf, color, (x+2*BLOCKSIZE, y, BLOCKSIZE, 2*BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y+BLOCKSIZE, BLOCKSIZE, 2*BLOCKSIZE))
	elif name == O:
		if angle == 0:
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, 3*BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, BLOCKSIZE))
		if angle == 90:
			pygame.draw.rect(surf, color, (x+2*BLOCKSIZE, y+BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, 3*BLOCKSIZE))
		if angle == 180:
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, 3*BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y+2*BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))
		if angle == 270:
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, 3*BLOCKSIZE))
	elif name == I:
		if angle == 0:
			pygame.draw.rect(surf, color, (x+2*BLOCKSIZE, y, BLOCKSIZE, 4*BLOCKSIZE))
		if angle == 90:
			pygame.draw.rect(surf, color, (x, y+2*BLOCKSIZE,4* BLOCKSIZE, BLOCKSIZE))
		if angle == 180:
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, 4*BLOCKSIZE))
		if angle == 270:
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, 4*BLOCKSIZE, BLOCKSIZE))
	elif name == J:
		if angle == 0:
			pygame.draw.rect(surf, color, (x, y+2*BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, 3*BLOCKSIZE))
		if angle == 90:
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, 3*BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x, y, BLOCKSIZE, BLOCKSIZE))
		if angle == 180:
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, 3*BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+2*BLOCKSIZE, y, BLOCKSIZE, BLOCKSIZE))
		if angle == 270:
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, 3*BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+2*BLOCKSIZE, y+2*BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))
	elif name == L:
		if angle == 0:
			pygame.draw.rect(surf, color, (x+2*BLOCKSIZE, y+2*BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, 3*BLOCKSIZE))
		if angle == 90:                    
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, 3*BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x, y+2*BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))
		if angle == 180:
			pygame.draw.rect(surf, color, (x+BLOCKSIZE, y, BLOCKSIZE, 3*BLOCKSIZE))
			pygame.draw.rect(surf, color, (x, y, BLOCKSIZE, BLOCKSIZE))
		if angle == 270:
			pygame.draw.rect(surf, color, (x+2*BLOCKSIZE, y, BLOCKSIZE, BLOCKSIZE))
			pygame.draw.rect(surf, color, (x, y+BLOCKSIZE, 3*BLOCKSIZE, BLOCKSIZE))

def showgrid():
	for y in range (20):
		pygame.draw.rect(surf, GREY, (10, 10+y*BLOCKSIZE,10*BLOCKSIZE , BLOCKSIZE), 1)
	for x in range (10):
		pygame.draw.rect(surf, GREY, (10+x*BLOCKSIZE, 10, BLOCKSIZE, 20*BLOCKSIZE), 1)

if __name__ == '__main__':
	main()
