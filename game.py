#!/usr/bin/python2

import pygame, math, random, sys, os
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
score = 0
last_shot = 0
mouse_x = 0
mouse_y = 0
time_since_last_frame = 0
dt = clock.get_time()
win_width = 1024
win_height = 600
#Fullscreen
#screen = pygame.display.set_mode((win_width, win_height), pygame.FULLSCREEN)
#Windowed
screen = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption('Biggest Idiotic Program')
#Black background
#background = pygame.Surface(screen.get_size()).convert()
#background.fill((0, 0, 0))
back_image = pygame.image.load("back.jpg")
background = pygame.Surface((win_width, win_height))
particles = pygame.Surface((win_width, win_height)).convert_alpha()
particles.fill((0,0,0,0))
background.blit(pygame.transform.smoothscale(back_image, (win_width, win_height)), (0,0), pygame.Rect(0,0,win_width,win_height))

def wait_key():
	while True:
		e = pygame.event.wait()
		if e.type == pygame.KEYDOWN:
			if e.key == pygame.K_ESCAPE:
				pygame.quit()
				sys.exit()
			return e
		elif e.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

def init_players():
	"""Ask user how many bros will play the game"""
	player_count = 0
	assigned_joys = {}
	assigned_keys = False
	screen.blit(background, (0,0))
	while not (1 <= player_count <= 4):
		screen.blit(background, (0,0))
		screen.blit(font.render("How many players ?",True,(255,255,255)), (0,0))
		pygame.display.update()
		e = wait_key()
		if e.key == pygame.K_1 or e.key == pygame.K_KP1:
			player_count = 1
		if e.key == pygame.K_2 or e.key == pygame.K_KP2:
			player_count = 2
		if e.key == pygame.K_3 or e.key == pygame.K_KP3:
			player_count = 3
		if e.key == pygame.K_4 or e.key == pygame.K_KP4:
			player_count = 4

	for i in range(player_count):
		screen.blit(background, (0,0))
		screen.blit(font.render("What kind of controller for player {0}?".format(i+1), True, (255,255,255)),(0,0))
		pygame.display.update()
		while True:
			e = wait_key()
			if e.key == pygame.K_k:
				if (not assigned_keys):
					players.append(Player())
					break
			elif e.key == pygame.K_j and len(joys)>= 1:
				screen.blit(background, (0,0))
				screen.blit(font.render("Which joystick ?", True, (255,255,255)),(0,30))
				pygame.display.update()
				while True:
					k = wait_key()
					if k.key == pygame.K_1 or k.key == pygame.K_KP1:
						players.append(PlayerJoy(joys[0]))
						break
					if (k.key == pygame.K_2 or k.key == pygame.K_KP2) and player_count >= 2 and len(joys)>=2:
						players.append(PlayerJoy(joys[1]))
						break
					if (k.key == pygame.K_3 or k.key == pygame.K_KP3) and player_count >= 3 and len(joys)>=3:
						players.append(PlayerJoy(joys[2]))
						break
					if (k.key == pygame.K_4 or k.key == pygame.K_KP4) and player_count == 4 and len(joys)>=4:
						players.append(PlayerJoy(joys[3]))
						break
				break
		screen.blit(background, (0,0))
		screen.blit(font.render("Choose a ship for player {0}".format(i), True, (255,255,255)), (0,0))
		while True:
			pygame.display.update()
			e = wait_key()
			img_path = os.path.join('playerimg', str(pygame.key.name(e.key)) + '.png')
			if (not os.path.isfile(img_path)):
				screen.blit(background, (0,0))
				screen.blit(font.render("Image not valid",True,(255,255,255)), (0,30))
				pygame.display.update()
				continue
			img = pygame.image.load(img_path)
			screen.blit(background, (0,0))
			screen.blit(img, (0, 0))
			screen.blit(font.render("Press the same key to confirm choice",True,(255,255,255)), (0,30))
			pygame.display.update()
			k = wait_key()
			if k.key == e.key:
				players[i].image = img
				break
			else:
				screen.blit(background, (0,0))
				screen.blit(font.render("Choose a ship for player {0}".format(i), True, (255,255,255)), (0,0))
				continue

	pygame.event.clear(pygame.KEYDOWN)

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
	return False

def pick_best_target_in_list(x, y, l): 
	""" Choose the closest 'l' object from pos(x, y) """
	mindist = 100000
	target = 0
	for i in l:
		angle = -math.atan2((i.x-x),(i.y)-y) + math.pi/2
		vx = math.cos(angle)
		vy = math.sin(angle)
		curdist = math.sqrt(vx**2 + vy**2)
		if mindist > curdist:
			mindist = curdist
			target = i
	return target

class Player:
	def __init__(self, x=win_width/2, y=win_height/2):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.width = 32
		self.height = 32
		self.firemode = 0
		self.ch_angle = 0
		self.ch_iradius = 40
		self.ch_oradius = 60
		self.speed = 4
		self.image = pygame.image.load(os.path.join("playerimg", "s.png")).convert_alpha()
		self.health = 100
		self.damage = 9000
		self.shots = []
		self.isshooting = False
		self.isshooting_s = False
		self.last_shot = 0
		self.score = 0
		self.primary = Bullet
		self.secondary = Bomb
		
	def move(self):
		if 0 < (self.x + self.vx * self.speed * (dt/100.)) < win_width:
			self.x += self.vx * self.speed * (dt/100.)
		if 0 < (self.y + self.vy * self.speed * (dt/100.)) < win_height:
			self.y += self.vy * self.speed * (dt/100.)

	def shoot(self):
		if self.isshooting and self.last_shot > 300:
			self.shots.append(self.primary(self.x + self.width/2, self.y + self.height/2, self.ch_angle))
			self.last_shot = 0
		self.last_shot += dt
		if self.isshooting_s and self.last_shot > 300:
			self.shots.append(self.secondary(self.x - 5, self.y - 5, self.ch_angle))
			self.last_shot = 0
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
	def update_crosshair(self):
		self.ch_x1=math.cos(self.ch_angle)*self.ch_iradius+self.x + 16
		self.ch_y1=math.sin(self.ch_angle)*self.ch_iradius+self.y + 16
		self.ch_x2=math.cos(self.ch_angle)*self.ch_oradius+self.x + 16
		self.ch_y2=math.sin(self.ch_angle)*self.ch_oradius+self.y + 16

	def update(self):
		global dt
		self.update_crosshair()
		self.shoot()
		#Move and check collision, add score according to dmg and reward
		for s in self.shots:
			s.update()
			for i in s.check_collisions():
				self.score += i.hit(s)
				s.hit(i)
			
		#Check for out of zone or destroyed shots, and delete them
		for i in self.shots[:]:
			if i.health <= 0:
				self.shots.remove(i)
			else:
				if i.x < 0 or i.x > win_width or i.y < 0 or i.y > win_height:
					self.shots.remove(i)

	def hit(self, hitter):
		self.health -= hitter.damage
		self.score -= 10*hitter.reward
	def draw(self):
		screen.blit(pygame.transform.smoothscale(rot_center(self.image, -math.degrees(self.ch_angle)),(self.width,self.height)), (self.x, self.y))
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
			if self.joy.get_name() == 'Xbox Gamepad (userspace driver)'
				self.hmaxis = 0
				self.vmaxis = 1
				self.hlaxis = 2
				self.vlaxis = 3
			elif self.joy.get_name() == 'USB Gamepad ':
				self.hmaxis = 0
				self.vmaxis = 1
				self.hlaxis = 3
				self.vlaxis = 4
		self.xc = 0
		self.yc = 0
	def input_(self):
		"""Take relevant elements from the event queue to control the player, update vectors and angles accordingly. Put back others events to the event queue"""
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

class Bot:
	"""Generic bot class"""
	last_spawn = 0 #Class variable to keep track of bot spawn, in order to script bot spawn
	def __init__(self, x=0, y=0, angle=0, width=20, height=20, reward=100, damage=100, speed=10., max_health=100,img = None ):
		self.x = x
		self.y = y
		self.max_health = max_health
		self.health = self.max_health
		self.reward = reward
		self.angle = angle
		self.vx = 0
		self.vy = 0
		self.speed = speed
		self.damage = damage
		self.target = pick_best_target_in_list(self.x, self.y, players) # pick best player target
		
		if img == None:
			self.image = pygame.Surface((20, 20))
			self.width, self.height = 20, 20
			pygame.draw.circle(self.image, (255,255,255), (self.width/2,self.height/2), 10)
		else:
			self.width, self.height = img.get_width(), img.get_height()
			self.image = pygame.Surface((self.width, self.height))
			self.image.blit(img, (0,0))
			self.image.convert_alpha()
		
	def hit(self, hitter):
		self.health = self.health - hitter.damage
		return self.reward

	def update(self, dt):
		self.angle = -math.atan2((self.target.x-self.x),(self.target.y)-self.y) + math.pi/2
		self.vx = math.cos(self.angle)
		self.vy = math.sin(self.angle)
		self.x = self.x + self.vx * self.speed * (dt/100.)
		self.y = self.y + self.vy * self.speed * (dt/100.)
		self.check_collision()
		
	def draw(self):
		"""Method for printing the bot to screen """
		screen.blit(self.image,(self.x, self.y))
		
	def check_collision(self):
		global players
		for j in players:
			if check_collision(self, j):
				j.hit(self)
				self.hit(j)

class ImprovedBot(Bot):
	"""smarter StandardBot, will change target if another player is closer, faster"""
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
		Bot.__init__(self, random.randint(x1, x2), random.randint(y1, y2), speed=10., img=pygame.image.load("british-flag.gif").convert_alpha())
		
		def update(self, dt):
			self.target = pick_best_target_in_list(self.x, self.y, players)
			self.angle = -math.atan2((self.target.x-self.x),(self.target.y)-self.y) + math.pi/2
			self.vx = math.cos(self.angle)
			self.vy = math.sin(self.angle)
			self.x = self.x + self.vx * self.speed
			self.y = self.y + self.vy * self.speed
			self.check_collision()

class Shot:
	"""Generic shot class"""
	def __init__(self, x, y, angle, damage, w, h, image = "bulletsh.png", speed=400., health = 100):
		self.angle = angle
		self.speed = speed
		self.damage = damage
		self.width = w
		self.height = h
		self.x = x - self.width/2
		self.y = y - self.height/2
		self.health = 100
		self.image = pygame.image.load(os.path.join("shotimg", image)).convert_alpha()
		
		# vector of shot
		self.vx = math.cos(angle)
		self.vy = math.sin(angle)
		
	def update(self, dt = 1):
		self.x += self.vx*(dt/100.)*(self.speed) # use speed of bot in calculation
		self.y += self.vy*(dt/100.)*(self.speed)
		
	def hit(self, hitter):
		self.health -= hitter.damage
	def check_collisions(self):
		collided = []
		for b in bots:
			if check_collision(self, b):
				collided.append(b)
		return collided
	def draw(self):
		#screen.blit(rot_center(self.image, math.degrees(-self.angle)), (self.x, self.y))
		screen.blit(pygame.transform.smoothscale(rot_center(self.image, -math.degrees(self.angle)),(self.width, self.height)), (self.x, self.y))

class Bullet(Shot):
	def __init__(self, x, y, angle):
		Shot.__init__(self, x, y, angle, 100, 16, 16, "bulletsh.png", 400., 100)

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
	
class Bomb(Shot):
	def __init__(self, x=0, y=0, angle=0):
		Shot.__init__(self, x, y, angle, 150, 5, 3, "bomb.png", 65)
		self.age = 1
		self.maxradius = 100
		self.health = 9000
	def update(self):
		global dt
		self.age += dt*(self.speed/100)
		if self.age >= 100:
			self.health = 0
	def draw(self):
		pygame.gfxdraw.aacircle(screen, (int(self.x), int(self.y)), int(self.age), (255,0,0))
	def check_collisions(self):
		collided = []
		for b in bots:
			if math.hypot(b.x-self.x, b.y-self.y) < self.age:
				collided.append(b)
		return collided
	
def update():
	global bot_ctr, dt, last_shot, mouse_x, mouse_y, score
	score = 0
	#Spawn bots
	bot_ctr += dt
	if (bot_ctr >= 500):
		bot_ctr = 0
		bots.append(ImprovedBot(players[0].x, players[0].y))
		
	#Update every bot
	for i in bots[:]:
		i.update(dt)
		if i.health <= 0:
			bots.remove(i)
			
	#Event handling
	for event in pygame.event.get((pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN, pygame.QUIT)):
		if event.type == pygame.MOUSEMOTION:
			mouse_x, mouse_y = event.pos
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				players[0].isshooting = True
			elif event.button == 3:
				players[0].isshooting_s = True
		elif event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				players[0].isshooting = False
			elif event.button == 3:
				players[0].isshooting_s = False	
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
		score += i.score

def draw():
	text = font.render("Score :" + str(score),True,(255,255,255))
	screen.blit(background, (0, 0)) #Blit background to real screen
	screen.blit(particles, (0,0))
	particles.fill((0,0,0,0))
	screen.blit(text, (0,0)) #Blit Text to real screen
	for i in bots: #Draw every bot to screen
		i.draw()
	for i in players:	
		i.draw()
	pygame.display.flip()
init_players()

# Main loop
while True:
	dt = clock.get_time() #Time since last frame
	time_since_last_frame += dt
	update()
	if time_since_last_frame >= 16:
		time_since_last_frame = 0
		draw()
		pygame.display.update() #Send the frame to GPU
	clock.tick_busy_loop(600) # Advance time and limit to 60 FPS
