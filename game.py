#!/usr/bin/python2

import pygame, math, random, sys
from pygame.locals import *

pygame.init()

#Initialize gamepads
pygame.joystick.init()
joys = []
for i in range(pygame.joystick.get_count()):
	joys.append(pygame.joystick.Joystick(0))
	joys[i].init()
clock = pygame.time.Clock()
# Font object to write text with it
font = pygame.font.Font(None, 25)
players = []
bots = []

curs = (
	"        ",
	"        ",
	"        ",
	"   XX   ",
	"   XX   ",
	"        ",
	"        ",
	"        ")
datatuple, masktuple = pygame.cursors.compile(curs, black='X', white=' ', xor='o')
pygame.mouse.set_cursor((8,8), (4,4), datatuple, masktuple)
player_count = 0
bot_ctr = 0
last_shot = 0
mouse_x = 0
mouse_y = 0
dt = clock.get_time()
win_width = 1680
win_height = 1050
#Fullscreen
screen = pygame.display.set_mode((win_width, win_height), pygame.FULLSCREEN)
#Windowed
#screen = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption('Biggest Idiotic Program')
#Black background
#background = pygame.Surface(screen.get_size()).convert()
#background.fill((0, 0, 0))
back_image = pygame.image.load("back.jpg")
background = pygame.Surface((win_width, win_height))
background.blit(pygame.transform.smoothscale(back_image, (win_width, win_height)), (0,0), pygame.Rect(0,0,win_width,win_height))

#===============================================================================
# def init_players():
#	"""Ask user how many bros will play the game"""
#	while not 1 <= player_count <= 4:
#		screen.blit(background, (0,0))
#		screen.blit(font.render("How many players ?",True,(255,255,255)), (0,0))
#		e = pygame.event.wait(pygame.KEYDOWN)
#		if e.key == pygame.K_1 or e == pygame.K_KP1:
#			player_count = 1
#		if e.key == pygame.K_2 or e == pygame.K_KP2:
#			player_count = 2
#		if e.key == pygame.K_3 or e == pygame.K_KP3:
#			player_count = 3
#		if e.key == pygame.K_4 or e == pygame.K_KP4:
#			player_count = 4
# 
#	pygame.event.clear(pygame.KEYDOWN)
#	for i in range(player_count):
#		if pygame.event.wait(pygame.KEYDOWN).key == pygame.K_k:
#			players.append(Player("key")) 
#		elif pygame.event.wait(pygame.KEYDOWN).key == pygame.K_j:
#			e = pygame.event.wait(pygame.KEYDOWN)
#			while (e.key not in (1,2,3,4)):
#				e = pygame.event.wait(pygame.KEYDOWN)
#				if e.key == pygame.K_1 or e == pygame.K_KP1:
#					players.append(Player(1))
#				if e.key == pygame.K_2 or e == pygame.K_KP2:
#					players.append(Player(2))
#				if e.key == pygame.K_3 or e == pygame.K_KP3:
#					players.append(Player(3))
#				if e.key == pygame.K_4 or e == pygame.K_KP4:
#					players.append(Player(4))
#===============================================================================


def rot_center(image, angle):
	"""Rotate an image while keeping its center and size"""
	orig_rect = image.get_rect()
	rot_image = pygame.transform.rotate(image, angle)
	rot_rect = orig_rect.copy()
	rot_rect.center = rot_image.get_rect().center
	rot_image = rot_image.subsurface(rot_rect).copy()
	return rot_image

def check_collision(a, b):
	"""Check collisions between 2 objects. Object must have x,y,width and height attributes"""
	if (a.x + a.width > b.x) and (a.x < b.x + b.width) and (a.y + a.height > b.y) and (a.y < b.y + b.height):
		return True
	else:
		return False

class Player:
	def __init__(self):
		self.x = win_width/2
		self.y = win_height/2
		self.vx = 0
		self.vy = 0
		self.width = 20
		self.height = 20
		self.firemode = 0
		self.ch_angle = 0
		self.ch_iradius = 40
		self.ch_oradius = 60
		self.speed = 4
		self.image = pygame.image.load("ship.png").convert_alpha()
		self.health = 100
		self.damage = 9000
		self.shots = []
		self.isshooting = False
		self.last_shot = 0
		self.score = 0
		
	def move(self):
		if 0 < self.x + self.vx < win_width:
			self.x += self.vx
		if 0 < self.y + self.vy < win_height:
			self.y += self.vy

	def shoot(self):
		if self.isshooting and self.last_shot > 300:
			self.shots.append(Shot(self.x, self.y, self.ch_angle))
			self.last_shot = 0
		self.last_shot += dt
	def input_(self):
		"""Input is managed in the global update loop"""
		self.ch_angle = -math.atan2((mouse_x-self.x),(mouse_y-self.y)) + math.pi/2
		self.vx, self.vy = 0, 0
		keys = pygame.key.get_pressed()
		if keys[pygame.K_RIGHT]:
			players[0].vx += 1
		if keys[pygame.K_LEFT]:
			players[0].vx -= 1
		if keys[pygame.K_DOWN]:
			players[0].vy += 1
		if keys[pygame.K_UP]:
			players[0].vy -= 1
		if abs(self.vx)+abs(self.vy) > 1:
			self.vx, self.vy = self.vx*self.speed/math.sqrt(2), self.vy*self.speed/math.sqrt(2)
		else:
			self.vx, self.vy = self.vx*self.speed, self.vy*self.speed
	def update(self):
		global dt
		self.ch_x1=math.cos(self.ch_angle)*self.ch_iradius+self.x
		self.ch_y1=math.sin(self.ch_angle)*self.ch_iradius+self.y
		self.ch_x2=math.cos(self.ch_angle)*self.ch_oradius+self.x
		self.ch_y2=math.sin(self.ch_angle)*self.ch_oradius+self.y
		self.shoot()
		#Move and check collision, add score according to dmg and reward
		for i in self.shots:
			i.update()
			for j in bots:
				if check_collision(i, j):
					j.hit(i)
					i.hit(j)
					# self.score += (i.damage / j.max_health) * j.reward
					print self.score
		#Check for out of zone or destroyed shots, and delete them
		for i in self.shots[:]:
			if i.health <= 0:
				self.shots.remove(i)
			else:
				if i.x < 0 or i.x > win_width or i.y < 0 or i.y > win_height:
					self.shots.remove(i)

	def hit(self, hitter):
		self.health -= hitter.damage
			
	def draw(self):
		screen.blit(pygame.transform.smoothscale(rot_center(self.image, -math.degrees(self.ch_angle)),(32,32)), (self.x-16, self.y-16))
		pygame.draw.aaline(screen, (255,255,255), (self.ch_x1, self.ch_y1), (self.ch_x2, self.ch_y2))
		for i in self.shots: #Draw every player shot to screen
			i.draw()

class PlayerJoy(Player):
	def __init__(self, joy):
		Player.__init__(self)
		self.joy = joy
		self.joy.init()
		if sys.platform == 'win32':
			self.hmaxis = 0
			self.vmaxis = 1
			self.hlaxis = 4
			self.vlaxis = 3
		elif sys.platform == 'linux2':
			self.hmaxis = 0
			self.vmaxis = 1
			self.hlaxis = 2
			self.vlaxis = 3
		self.xc = 0
		self.yc = 0
	def input_(self):
		"""Take relevant elements from the event queue to control the player, 
		update vectors and angles accordingly. Put back others events to the event queue"""
		x_s, y_s, xc, yc, x_c, y_c = 0,0,0,0,0,0
		for e in pygame.event.get((pygame.JOYAXISMOTION, pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN)):
			if e.joy == self.joy.get_id():
				if e.type == pygame.JOYAXISMOTION:
					if e.axis == self.hlaxis: # Look away
						self.xc = e.value
					elif e.axis == self.vlaxis: # Look away too
						self.yc = e.value
					if e.axis == self.hmaxis: # x movement
						x_c += 1.
						x_s += e.value
					elif e.axis == self.vmaxis: # y movement
						y_c += 1.
						y_s = e.value
				else:
					if e.type == pygame.JOYBUTTONDOWN:
						self.isshooting = True
					else:
						self.isshooting = False
			else: 
				pygame.event.post(e)
		if x_c:
			self.vx = x_s / x_c
		if y_c:
			self.vy = y_s / y_c
		self.ch_angle = math.atan2(self.yc, self.xc)
	def move(self):
		if 0 < self.x + self.vx * self.speed < win_width:
			self.x += self.vx * self.speed
		if 0 < self.y + self.vy * self.speed < win_height:
			self.y += self.vy * self.speed

#Add players
players.append(Player())
for i in range(len(joys)):
	players.append(PlayerJoy(joys[0]))

class Bot:
	"""Generic bot class"""
	def __init__(self, x=0, y=0, width=20, height=20, reward=100, damage=9000, speed=2., max_health=100,img = 0 ):
		self.x = x
		self.y = y
		self.max_health = max_health
		self.health = self.max_health
		self.reward = reward
		self.angle = 0
		self.vx = 0
		self.vy = 0
		self.speed = speed
		self.damage = damage
		
		if img == 0:
			self.image = pygame.Surface((20, 20))
			self.width, self.height = 20, 20
			pygame.draw.circle(self.image, (255,255,255), (self.width/2,self.height/2), 10)
		else:
			self.width, self.height = img.get_width(), img.get_height()
			self.image = pygame.Surface((self.width, self.height))
			self.image.blit(img, (0,0))

		
	def hit(self, hitter):
		self.health = self.health - hitter.damage
		
	def update(self, dt):
		self.angle = -math.atan2((players[0].x-self.x),(players[0].y)-self.y) + math.pi/2
		self.vx = math.cos(self.angle)
		self.vy = math.sin(self.angle)
		self.x = self.x + self.vx * self.speed
		self.y = self.y + self.vy * self.speed
		self.check_collision()
		
	def draw(self):
		"""Method for printing the bot to screen """
		screen.blit(self.image, (self.x, self.y))
		
	def check_collision(self):
		global players
		for j in players:
			if check_collision(self, j):
				j.hit(self)
				self.hit(j)

class StandardBot(Bot):
	"""Bot with random spawn between the most far angle of the screen and player position. Random speed"""
	def __init__(self, plx, ply):
		x1, y1, x2, y2 = 0, 0, int(plx), int(ply)
		if(plx > win_width/2): #bottom screen
			if (ply > win_height/2):
				#print "Quarter 3 == player in bottom right corner"
				x1,y1,x2,y2 = 0,0, x2-20,y2-20
			else:
				#print "Quarter 2 == player in bottom left corner"
				x1,y1,x2,y2 = 0, y2+20,x2-20, win_height
		else: #top screen
			if (ply > win_height/2):
				#print "Quarter 4 == player in top right corner"
				x1,y1,x2,y2 = x2+20, 0, win_width,y2-20
			else:
				#print "Quarter 1 == player in top left corner"
				x1,y1,x2,y2 = x2+20, y2+20, win_width, win_height	
		Bot.__init__(self, random.randint(x1, x2), random.randint(y1, y2), img=pygame.image.load("british-flag.gif").convert_alpha())

class Shot:
	"""Generic shot class"""
	def __init__(self, x=0, y=0, angle=0, damage=100, width=20, height=20, mode="cl", speed=2000.):
		self.x = x
		self.y = y
		self.angle = angle
		self.speed = speed
		self.damage = damage
		self.width = width
		self.height = height
		self.health = 100
		self.mode = mode
		self.image = pygame.image.load("bullet" + mode + ".png").convert()
		
		# vector of shot
		self.vx = math.cos(angle)
		self.vy = math.sin(angle)
		
	def update(self, dt = 1):
		self.x += self.vx*dt*(self.speed/100) # use speed of bot in calculation
		self.y += self.vy*dt*(self.speed/100)
		
	def hit(self, hitter):
		self.health -= hitter.damage
	
	def draw(self):
		pygame.draw.circle(screen, (255,0,0), (int(self.x), int(self.y)), 10)

class RocketShot(Shot): 
	"""Small rocket propelled bullet that goes faster with time. Higher damage - lower initial speed -- might as well change 'mode' """
	
	def __init__(self, x=0, y=0, angle=0, damage=150, width=5, height=3, mode="rk", speed=50.):
		Shot.__init__(self, x, y, angle, damage, width, height, mode, speed) # calls __init__ from parent
		self.health = 1 # low health so it can't go through

	def update(self):
		self.x += self.vx*dt*(self.speed/100) # use speed of bot in calculation
		self.y += self.vy*dt*(self.speed/100)
		self.speed = min(self.speed+2, 2500) # increase shot speed / get a maximum speed for the rocket
	# should the rocket folow a bot (check for everyshot which one to target) folow the mouse (can lead to weird behaviors) or just go straight
	# might as well add the explosion (hit multiple bots in an area)
def update():
	global bot_ctr, dt, last_shot, mouse_x, mouse_y

	#Spawn bots
	bot_ctr += dt
	if (bot_ctr >= 500):
		bot_ctr = 0
		bots.append(StandardBot(players[0].x, players[0].y))
		
	#Update every bot
	for i in bots[:]:
		i.update(dt)
		if i.health <= 0:
			players[0].score += i.reward # increase score when bot dies
			bots.remove(i)
			
	#Event handling
	for event in pygame.event.get((pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN, pygame.QUIT)):
		if event.type == pygame.MOUSEMOTION:
			mouse_x, mouse_y = event.pos
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				players[0].isshooting = True
		elif event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				players[0].isshooting = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				pygame.quit()
				sys.exit()
		elif event.type == QUIT:
			pygame.quit()
			sys.exit()
	#Must be after event handling to listen to mouse input (shooting)
	for i in players:
		i.input_()
		i.move()
		i.update()

def draw():
	text = font.render("Score :" + str(players[0].score),True,(255,255,255))
	screen.blit(background, (0, 0)) #Blit background to real screen
	screen.blit(text, (0,0)) #Blit Text to real screen
	for i in bots: #Draw every bot to screen
		i.draw()
	for i in players:	
		i.draw()
	pygame.display.flip()

# Main loop
while True:
	dt = clock.get_time() #Time since last frame
	update() #Update coords
	draw()
	pygame.display.update() #Send the frame to GPU
	clock.tick(60) #Advance the time precisely
