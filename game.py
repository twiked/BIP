#!/usr/bin/python2

import pygame, math, random, sys
from pygame.locals import *

pygame.init()
clock = pygame.time.Clock()
# Font object to write text with it
font = pygame.font.Font(None, 25)
players = []
bots = []
shots = []

bot_ctr = 0
last_shot = 0
ch_iradius = 40
ch_oradius = 60
mouse_x = 0
mouse_y = 0
dt = clock.get_time()
win_width = 640
win_height = 480
screen = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption('Biggest Idiotic Program')
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))

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
		self.speed = 300
		self.image = pygame.image.load("ship.png").convert_alpha()
		self.health = 100
		self.damage = 9000
		self.shots = []
		self.isshooting = False
		self.last_shot = 0
		
	def update(self):
		global dt
		keys = pygame.key.get_pressed()
		if keys[pygame.K_RIGHT]: players[0].x += 1
		if keys[pygame.K_LEFT]: players[0].x -= 1
		if keys[pygame.K_DOWN]: players[0].y += 1
		if keys[pygame.K_UP]: players[0].y -= 1
		self.ch_angle = -math.atan2((mouse_x-self.x),(mouse_y-self.y)) + math.pi/2
		self.ch_x1=math.cos(self.ch_angle)*ch_iradius+self.x
		self.ch_y1=math.sin(self.ch_angle)*ch_iradius+self.y
		self.ch_x2=math.cos(self.ch_angle)*ch_oradius+self.x
		self.ch_y2=math.sin(self.ch_angle)*ch_oradius+self.y
		
		if self.isshooting and self.last_shot > 500:
			self.shots.append(Shot(self.x, self.y, self.ch_angle))
			self.last_shot = 0
		self.last_shot += dt
		
		for i in self.shots:
			i.update()
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
		
#Add one player
players.append(Player())

class Bot:
	"""Generic bot class"""
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
		self.max_health = 100
		self.health = self.max_health
		self.width = 20
		self.height = 20
		self.reward = 100
		self.angle = 0
		self.vx = 0
		self.vy = 0
		self.speed = 0.1
		self.damage = 9000
		
	def hit(self, hitter):
		self.health = self.health - hitter.damage
		
	def update(self, dt):
		old_x=self.x
		old_y=self.y
		self.angle = -math.atan2((players[0].x-self.x),(players[0].y)-self.y) + math.pi/2
		self.vx = math.cos(self.angle)
		self.vy = math.sin(self.angle)
		self.x = self.x + self.vx * self.speed
		self.y = self.y + self.vy * self.speed
		self.check_collision()
		
	def draw(self):
		"""Method for printing the bot to screen """
		pygame.draw.circle(screen, (255,255,255), (int(self.x), int(self.y)), 10)
		
	def check_collision(self):
		global players
		for j in players:
			if check_collision(self, j):
				j.hit(self)
				self.hit(j)
	
"""
class BotSubClassType(Bot):
	# Bot with random spawn between the most far angle of the screen and player position. Random speed
	def __init__(self, plx, ply):	
		Class.__init__(self, plx, ply)"""

class StandardBot(Bot):
	"""Bot with random spawn between the most far angle of the screen and player position. Random speed"""
	def __init__(self, plx, ply):
		x1, y1, x2, y2 = 0, 0, plx, ply
		if(plx > win_width/2): #bottom screen
			if (ply > win_height/2):
				#print "Quarter 3 == player in bottom right corner"
				x1,y1,x2,y2 = 0,0, plx-20,ply-20
			else:
				#print "Quarter 2 == player in bottom left corner"
				x1,y1,x2,y2 = 0, ply+20,plx-20, win_height
		else: #top screen
			if (ply > win_height/2):
				#print "Quarter 4 == player in top right corner"
				x1,y1,x2,y2 = plx+20, 0, win_width,ply-20
			else:
				#print "Quarter 1 == player in top left corner"
				x1,y1,x2,y2 = plx+20, ply+20, win_width, win_height	
		Bot.__init__(self, random.randint(x1, x2), random.randint(y1, y2))

class Shot:
	"""Generic shot class"""
	def __init__(self, x=0, y=0, angle=0, damage=100, width=5, height=3, mode="cl", speed=100):
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
		self.check_collision()
		
	def hit(self, hitter):
		self.health -= hitter.damage
		print self.health
	
	def draw(self):
		pygame.draw.circle(screen, (255,0,0), (int(self.x), int(self.y)), 10)
		
	def check_collision(self):
		for i in bots:
			if check_collision(self, i):
				i.hit(self)
				self.hit(i)

class RocketShot(Shot): 
	"""Small rocket propelled bullet that goes faster with time. Higher damage - lower initial speed -- might as well change 'mode' """
	
	def __init__(self, x=0, y=0, angle=0, damage=150, width=5, height=3, mode="cl", speed=50):
		Shot.__init__(self, x, y, angle, damage, width, height, mode, speed) # calls __init__ from parent

	def update(self):
		self.x += self.vx*dt*(self.speed/100) # use speed of bot in calculation
		self.y += self.vy*dt*(self.speed/100)
		self.speed += 2 # increase shot speed -- higher increase might be better

def update():
	global bot_ctr, dt, last_shot, mouse_x, mouse_y

	#Spawn bots
	bot_ctr += dt
	if (bot_ctr >= 3000):
		bot_ctr = 0
		bots.append(StandardBot(players[0].x, players[0].y))
		
	#Update every bot
	for i in bots[:]:
		i.update(dt)
		if i.health <= 0:
			bots.remove(i)

	#Event handling	
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				players[0].isshooting = True
		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				players[0].isshooting = False
		if event.type == pygame.MOUSEMOTION:
			mouse_x, mouse_y = event.pos

	for i in players:
		i.update()

def draw():
	text = font.render("Deb:",True,(255,255,255))
	screen.blit(background, (0, 0)) #Blit background to real screen
	screen.blit(text, (0,0)) #Blit Text to real screen
	for i in bots: #Draw every bot to screen
		i.draw()
	for i in players[0].shots: #Draw every player shot to screen
		i.draw()
	players[0].draw()
	pygame.draw.line(screen, (255,255,255), (players[0].ch_x1, players[0].ch_y1), (players[0].ch_x2, players[0].ch_y2))	
	pygame.display.flip()

# Main loop
while True:
	dt = clock.get_time() #Time since last frame
	update() #Update coords
	draw()
	pygame.display.update() #Send the frame to GPU
	#Advance the time precisely
	clock.tick_busy_loop()
