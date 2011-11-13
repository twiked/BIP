#!/usr/bin/python2

import pygame, math, random, sys, os, time
from pygame.locals import *
import pygame.gfxdraw
pygame.mixer.pre_init(buffer=1024)
pygame.init()

#Initialize gamepads
pygame.joystick.init()
joys = []
for i in range(pygame.joystick.get_count()):
	joys.append(pygame.joystick.Joystick(i))
	joys[i].init()

#Initialise Clock
clock = pygame.time.Clock()

# Font object to write text with it
font = pygame.font.Font(None, 25)
players = []
bots = []

#Mouse cursor initalisation
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
game = True
lives = 5
time_since_last_frame = 0
played_time = 0
difficulty_modifier = 1
dt = clock.get_time()
win_width = 1024
win_height = 600
should_update_infos = True

#Score file reading
scorefile = open('score', 'r+')
hiscore = int(scorefile.read())

#Fullscreen
#screen = pygame.display.set_mode((win_width, win_height), pygame.FULLSCREEN)
#Windowed
screen = pygame.display.set_mode((win_width, win_height))
infos = pygame.surface.Surface((win_width, win_height)).convert_alpha()
pygame.display.set_caption('Biggest Idiotic Program')

#Black background
#background = pygame.Surface(screen.get_size()).convert()
#background.fill((0, 0, 0))

#Textured background
back_image = pygame.image.load("back.jpg")
background = pygame.Surface((win_width, win_height)).convert()
semi_background = pygame.Surface((win_width, win_height)).convert()
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
					if (k.key == pygame.K_2 or k.key == pygame.K_KP2) and len(joys)>=2:
						players.append(PlayerJoy(joys[1]))
						break
					if (k.key == pygame.K_3 or k.key == pygame.K_KP3) and len(joys)>=3:
						players.append(PlayerJoy(joys[2]))
						break
					if (k.key == pygame.K_4 or k.key == pygame.K_KP4) and len(joys)>=4:
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

def pick_closest_in_list(x, y, l): 
	""" Choose the closest 'l' 's object from pos(x, y) """
	mindist = 100000
	target = None
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
		self.speed = 16
		self.image = pygame.image.load(os.path.join("playerimg", "s.png")).convert_alpha()
		self.health = 100
		self.damage = 9000
		self.shots = []
		self.is_hitting = []
		self.isshooting = False
		self.isshooting_s = False
		self.last_shot = 0
		self.score = 0
		self.primary = Bullet
		self.secondary = Rocket
		self.pe = ParticleEmitter(YellowParticle, 90, 8)
		
	def move(self):
		if 0 < (self.x + self.vx * self.speed * (dt/100.)) < win_width - self.width:
			self.x += self.vx * self.speed * (dt/100.)
		if 0 < (self.y + self.vy * self.speed * (dt/100.)) < win_height - self.height:
			self.y += self.vy * self.speed * (dt/100.)

	def shoot(self):
		if self.isshooting and self.last_shot > 300:
			self.shots.append(self.primary(self.x + self.width/2, self.y + self.height/2, self.ch_angle))
			self.last_shot = 0
			self.pe.create_part(self.x + 16, self.y + 16, self.ch_angle, math.pi/4)
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
			self.vx, self.vy = self.vx/math.sqrt(2), self.vy/math.sqrt(2)
	def update_crosshair(self):
		self.ch_x1=math.cos(self.ch_angle)*self.ch_iradius+self.x + 16
		self.ch_y1=math.sin(self.ch_angle)*self.ch_iradius+self.y + 16
		self.ch_x2=math.cos(self.ch_angle)*self.ch_oradius+self.x + 16
		self.ch_y2=math.sin(self.ch_angle)*self.ch_oradius+self.y + 16

	def update(self):
		global dt
		self.update_crosshair()
		self.shoot()
		#Check for out of zone or destroyed shots, and delete them
		for i in self.shots[:]:
			if i.health <= 0:
				self.shots.remove(i)
			else:
				if i.x < 0 or i.x > win_width or i.y < 0 or i.y > win_height:
					self.shots.remove(i)
		#Move and check collision, add score according to dmg and reward
		for s in self.shots:
			s.update()
			for i in s.check_collisions():
				self.score += i.hit(s)
				s.hit(i)
			

		self.pe.update()
	def hit(self, hitter):
		global should_update_infos
		should_update_infos = True
		global lives, game
		try:
			if self.is_hitting.index(hitter):
				pass
		except(ValueError):
			self.is_hitting.append(hitter)
			lives -= 1
			if lives <= 0:
				game = False

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
			if self.joy.get_name() == 'Controller (XBOX 360 For Windows)':
				self.hmaxis = 0
				self.vmaxis = 1
				self.hlaxis = 4
				self.vlaxis = 3
			else:
				self.hmaxis = 0
				self.vmaxis = 1
				self.hlaxis = 4
				self.vlaxis = 3
		elif sys.platform == 'linux2':
			if self.joy.get_name() == 'Xbox Gamepad (userspace driver)':
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
		for e in pygame.event.get((pygame.JOYAXISMOTION, pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN)):
			if e.joy == self.joy.get_id():
				if e.type == pygame.JOYAXISMOTION:
					if e.axis == self.hlaxis: # Look away
						self.xc = e.value
					elif e.axis == self.vlaxis: # Look away too
						self.yc = e.value
					elif e.axis == self.hmaxis: # x movement
						self.vx = e.value
					elif e.axis == self.vmaxis: # y movement
						self.vy = e.value
				else:
					if e.type == pygame.JOYBUTTONDOWN:
						self.isshooting = True
					else:
						self.isshooting = False
			else: 
				pygame.event.post(e)
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
		self.is_hitting = []
		self.speed = speed
		self.damage = damage
		self.target = pick_closest_in_list(self.x, self.y, players) # pick best player target
		
		if img == None:
			self.image = pygame.Surface((20, 20))
			self.width, self.height = 20, 20
			pygame.draw.circle(self.image, (255,255,255), (self.width/2,self.height/2), 10)
		else:
			self.width, self.height = img.get_width(), img.get_height()
			self.image = img.convert_alpha()
		
	def hit(self, hitter):
		try:
			if self.is_hitting.index(hitter):
				pass
		except(ValueError):
			self.is_hitting.append(hitter)
			self.health = self.health - hitter.damage
			if self.health <= 0:
				return self.reward
		return 0

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
		if(plx > win_width/2):
			if (ply > win_height/2):
				x1,y1,x2,y2 = 0,0, x2-20,y2-20
			else:
				x1,y1,x2,y2 = 0, y2+20,x2-20, win_height
		else:
			if (ply > win_height/2):
				x1,y1,x2,y2 = x2+20, 0, win_width,y2-20
			else:
				x1,y1,x2,y2 = x2+20, y2+20, win_width, win_height	
		Bot.__init__(self, random.randint(x1, x2), random.randint(y1, y2), speed=10., img=pygame.image.load("british-flag.gif").convert_alpha())
		
		def update(self, dt):
			self.target = pick_closest_in_list(self.x, self.y, players)
			self.angle = -math.atan2((self.target.x-self.x),(self.target.y)-self.y) + math.pi/2
			self.vx = math.cos(self.angle)
			self.vy = math.sin(self.angle)
			self.x = self.x + self.vx * self.speed
			self.y = self.y + self.vy * self.speed
			self.check_collision()
			
class TankBot(Bot):
	"""TankBot is resistant to damage, and return shot to the player"""
	def __init__(self, plx, ply):
		x1, y1, x2, y2 = 0, 0, int(plx), int(ply)
		if(plx > win_width/2):
			if (ply > win_height/2):
				x1,y1,x2,y2 = 0,0, x2-20,y2-20
			else:
				x1,y1,x2,y2 = 0, y2+20,x2-20, win_height
		else:
			if (ply > win_height/2):
				x1,y1,x2,y2 = x2+20, 0, win_width,y2-20
			else:
				x1,y1,x2,y2 = x2+20, y2+20, win_width, win_height	
		Bot.__init__(self, random.randint(x1, x2), random.randint(y1, y2), speed=10.,max_health=500, img=pygame.image.load("itm_circle_grey.png").convert_alpha())

class Shot:
	"""Generic shot class"""
	#Number of shots spawned (to identify them)
	num = 0
	def __init__(self, x, y, angle, damage, w, h, image = "bulletsh", sound = "shoot", speed=400., health = 100):
		self.num = Shot.num
		Shot.num += 1
		self.angle = angle
		self.speed = speed
		self.damage = damage
		self.width = w
		self.height = h
		self.x = x - self.width/2
		self.y = y - self.height/2
		self.health = health
		self.is_hitting = []
		self.image = pygame.image.load(os.path.join("shotimg", image + ".png")).convert_alpha()
		self.sound = pygame.mixer.Sound(os.path.join("sounds", sound + ".wav"))
		if not pygame.mixer.get_busy():
			self.sound.play()
		# vector of shot
		self.vx = math.cos(angle)
		self.vy = math.sin(angle)
		
	def update(self, dt = 1):
		self.x += self.vx*(dt/100.)*(self.speed) # use speed of bot in calculation
		self.y += self.vy*(dt/100.)*(self.speed)
		
	def hit(self, hitter):
		global should_update_infos
		should_update_infos = True
		try:
			if self.is_hitting.index(hitter):
				pass
		except(ValueError):
			self.is_hitting.append(hitter)
			if isinstance (hitter, TankBot): # "is a"
				self.angle += random.uniform(math.pi/2, 3*math.pi/2) # return shots to the player
				self.vx = math.cos(self.angle)
				self.vy = math.sin(self.angle)
			else:
				self.health = self.health - hitter.damage
	
	def set_angle(angle):
		self.angle = angle
		self.vx = math.cos(angle)
		self.vy = math.sin(angle)
		
	def check_collisions(self):
		collided = []
		for b in bots:
			if check_collision(self, b):
				collided.append(b)
		return collided
	def draw(self):
		screen.blit(pygame.transform.smoothscale(rot_center(self.image, -math.degrees(self.angle)),(self.width, self.height)), (self.x, self.y))

class Bullet(Shot):
	def __init__(self, x, y, angle):
		Shot.__init__(self, x, y, angle, 100, 16, 16, "bulletsh", "shoot", 400., 50)

class Rocket(Shot): 
	"""Small rocket propelled bullet that goes faster with time. Higher damage - lower initial speed -- might as well change 'mode' """
	def __init__(self, x=0, y=0, angle=0, damage=150, w=5, h=3, image="rk", speed=5., health=1):
		self.following = pick_closest_in_list(x, y, bots) #Which bot it follows
		if self.following != None:
			Shot.__init__(self, x, y, angle, damage, w, h, image, "rocket", speed) # calls __init__ from parent
			self.radius = 50
		else:
			self.health=0
	def update(self):
		self.angle = (math.atan2(self.following.y - self.y, self.following.x - self.x))
		self.vx = math.cos(self.angle)
		self.vy = math.sin(self.angle)
		self.x += self.vx*dt*(self.speed/100) # use speed of bot in calculation
		self.y += self.vy*dt*(self.speed/100)
		self.speed = min(self.speed+2, 2500) # increase shot speed / get a maximum speed for the rocket
	def hit(self, hitter):
		self.health = 0
		for i in bots:
			if math.hypot(i.x-self.x, i.y-self.y) < self.radius:
				i.health = 0
class Bomb(Shot):
	def __init__(self, x=0, y=0, angle=0):
		Shot.__init__(self, x=x+16, y=y+16, angle=angle, damage=200, w=5, h=3, speed=1, sound="explosion")
		self.age = 1
		self.maxradius = 100
		self.health = 9000
	def update(self):
		global dt
		self.age += dt*self.speed
		if self.age >= 100:
			self.health = 0
	def draw(self):
		pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), int(self.age), (255,0,0))
	def check_collisions(self):
		collided = []
		for b in bots:
			if math.hypot(b.x-self.x, b.y-self.y) < self.age:
				collided.append(b)
		return collided
	
class Particle:
	def __init__(self, x, y, ttl=1000, angle=0, velocity=1, angular_velocity=0, start_color=(255,255,255), end_color=(255,255,255)):
		self.x, self.y  = x, y
		self.angle = angle
		self.ttl = ttl
		self.velocity = velocity
		self.angular_velocity = angular_velocity
		self.start_color, self.end_color = start_color, end_color
		self.color = []
		for i in start_color:
			self.color.append(i)
		self.color_increment = ((self.end_color[0]-self.start_color[0])/ttl, (self.end_color[1]-self.start_color[1])/ttl, (self.end_color[2]-self.start_color[2])/ttl)
	def update(self, dt):
		self.ttl -= dt
		self.x += math.cos(self.angle)*self.velocity
		self.y += math.sin(self.angle)*self.velocity
		self.angle += self.angular_velocity*dt/self.ttl
		for n, i in enumerate(self.color_increment):
			self.color[n] += i
			if self.color[n] < 0:
				self.color[n]= 0
	def draw(self):
		pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), 1, self.color)

class YellowParticle(Particle):
	def __init__(self, x, y, angle):
		Particle.__init__(self, x, y, 100, angle, random.uniform(0,2), random.uniform(-math.pi/2, math.pi/2), (255,255,0), (255,0,0))

class ParticleEmitter:
	def __init__(self, part, interval, count):
		"""Define a new particle emitter which creates and keep track of particles."""
		self.part = part
		self.part_list = []
		self.interval = interval
		self.count = count
	def create_part(self, x, y, angle, jitter):
		for i in range(self.count):
			var = random.uniform(-jitter, jitter)
			a = angle + var
			self.part_list.append(self.part(x, y, a))
	def update(self):
		for n,i in enumerate(self.part_list):
			i.update(dt)
			if i.ttl <= 0:
				self.part_list[n] = self.part_list[len(self.part_list)-1]
				self.part_list.pop()
	def draw(self):
		for i in self.part_list:
			i.draw()

def update():
	global bot_ctr, dt, last_shot, mouse_x, mouse_y, score
	score = 0
	#Bot spawning
	bot_ctr += 1
	if (bot_ctr%(max(600-(played_time / 20000), 80/difficulty_modifier/len(players) )) <= 1): # more bots through time and with more players
		bots.append(ImprovedBot(players[0].x, players[0].y))
	if (bot_ctr >= 2000/len(players)):
		bot_ctr = 0
		bots.append(TankBot(players[0].x, players[0].y))
		
	#Update every bot
	for i in bots[:]:
		if i.health <= 0:
			bots.remove(i)
		i.update(dt)

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

	#Players' updates
	for i in players:
		i.input_()
		i.move()
		i.update()
		score += i.score

def draw():
	global should_update_infos
	screen.blit(background, (0, 0)) #Blit background to real screen
	time_txt = font.render("Time :" + str(int(played_time/1000)),True,(255,255,255))
	score_txt = font.render("Score :" + str(score),True,(255,255,255))
	screen.blit(time_txt, (0, win_height-20))
	screen.blit(score_txt, (0,0))
	for i in bots: #Draw every bot to screen
		i.draw()
	for i in players:	
		i.draw()
		i.pe.draw()
	pygame.display.flip()

#Game preparation
init_players()
old_time = time.time()

# Main loop
while game:
	new_time = time.time()
	dt = (new_time - old_time)*1000 #Time since last frame
	old_time = new_time
	played_time += dt * len(players) * difficulty_modifier
	time_since_last_frame += dt
	update()
	if time_since_last_frame >= 16:
		time_since_last_frame = 0
		draw()
		pygame.display.update() #Send the frame to GPU
	clock.tick(600) # Advance time and limit to 60 FPS

scorefile.close()
if score > hiscore:
	scorefile = open("score", "w")
	scorefile.write(str(score))
	scorefile.close()
	strt = "You beat the HiScore of {0} !".format(hiscore)
else:
	strt = "You DID NOT beat the HiScore of {0}, too bad !".format(hiscore)
txt = font.render(strt, True, (255,0,0))
width, height = font.size(strt)

screen.blit(background, (0, 0)) #Blit background to real screen

scorestring = "Your score : " + str(score)
finalscore_txt = font.render(scorestring, True, (255,255,255))
width_2, height_2 = font.size(scorestring)

screen.blit(txt, (win_width/2- width/2, win_height/2- height/2))
screen.blit(finalscore_txt, (win_width/2- width_2/2, win_height/2+ height_2/2))
pygame.display.flip()
while wait_key():
	pass
