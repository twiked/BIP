#!/usr/bin/python
import pygame, math, random, sys
from pygame.locals import *
pygame.init()


# Class definitions
class Player:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.width = 20
		self.height = 20
		self.firemode = 0
		self.ch_angle = 0
		self.speed = 300
class Bot:
	def __init__(self, x=0, y=0, max_health=100, alpha=255):
		self.x = x
		self.y = y
		self.max_health = max_health
		self.health = max_health
		self.alpha = alpha
		self.width = 20
		self.height = 20
		self.reward = 100
		self.angle = 0
		self.vx = 0
		self.vy = 0
		self.speed = 0.1
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

class Shot:
	def __init__(self, x=0, y=0, angle=0, damage=100, width=5, height=3, mode="cl", speed=100):
		self.x = x
		self.y = y
		self.angle = angle
		self.speed = speed
		self.damage = damage
		self.width = width
		self.height = height
		self.mode = mode
		self.image = pygame.image.load("bullet" + mode + ".png")

		# vector of bullet
		self.vx = math.cos(angle)
		self.vy = math.sin(angle)
	def update(self, dt = 1):
		self.x += self.vx*dt
		self.y += self.vy*dt

#Global table definitions
bots = []
players = []
shots = []

#Some variables
bot_ctr = 0
last_shot = 0
dt = 0
mouse_x = 0
mouse_y = 0
#crosshair definitions
ch_x1=0
ch_y1=0
ch_x2=0
ch_y2=0
ch_iradius=40
ch_oradius=45

pygame.init()
clock = pygame.time.Clock()
dt = clock.get_time()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Biggest Idiotic Program')
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))

# Display some text
font = pygame.font.Font(None, 36)
text = font.render("Hello There", 1, (10, 10, 10))
textpos = text.get_rect()
textpos.centerx = background.get_rect().centerx
background.blit(text, textpos)

#Add one player
players.append(Player())


def update():
	global bot_ctr, dt, last_shot, mouse_x, mouse_y
	bot_ctr += dt
	if (bot_ctr >= 0.2):
		pass
	bot_ctr = 0
	bots.append(Bot(random.randrange(300), random.randrange(300)))
		
	for i in bots:
		i.update(dt)
	for i in shots:
		i.update(dt)
		
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RIGHT:
				players[0].x = players[0].x + (players[0].speed * dt)
			elif event.key == pygame.K_LEFT:
				players[0].x = players[0].x - (players[0].speed * dt)
			if event.key == pygame.K_UP:
				players[0].y = players[0].y - (players[0].speed * dt)
			elif event.key == pygame.K_DOWN:
				players[0].y = players[0].y + (players[0].speed * dt)
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				shots.append(Shot(players[0].x, players[0].y, players[0].ch_angle))
				last_shot = 0
		else:
			last_shot += dt
		if event.type == pygame.MOUSEMOTION:
			mouse_x, mouse_y = event.pos
	#Calculate crosshair coords
	players[0].ch_angle=-math.atan2((mouse_x-players[0].x),(mouse_y-players[0].y)) + math.pi/2
	ch_x1=math.cos(players[0].ch_angle)*ch_iradius+players[0].x
	ch_y1=math.sin(players[0].ch_angle)*ch_iradius+players[0].y
	ch_x2=math.cos(players[0].ch_angle)*ch_oradius+players[0].x
	ch_y2=math.sin(players[0].ch_angle)*ch_oradius+players[0].y

def draw():
	# Blit everything to the screen
	screen.blit(background, (0, 0))
	
	pygame.display.flip()
	pygame.display.update()
	for i in bots:
		pygame.draw.circle(screen, (255,255,255), (int(i.x), int(i.y)), 10)

while True:
	dt = clock.get_time()
	
		#if(pygame.mouse.get_pressed()[0] and last_shot >= cooldown):
			#shots.append(Shot(players[0].x, players[0].y, players[0].ch_angle))
			#last_shot = 0
		#else:
			#last_shot += dt
	update()
	draw()
	clock.tick()
