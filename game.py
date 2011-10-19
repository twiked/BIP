#!/usr/bin/python2
import pygame, math, random, sys
from pygame.locals import *
pygame.init()

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
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Biggest Idiotic Program')
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))

class Player:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.vx = 0
		self.vy = 0
		self.width = 20
		self.height = 20
		self.firemode = 0
		self.ch_angle = 0
		self.speed = 300
		self.image = pygame.image.load("ship.png").convert_alpha()
	def update(self):
		self.x += self.vx
		self.y += self.vy
		self.ch_angle = -math.atan2((mouse_x-self.x),(mouse_y-self.y)) + math.pi/2
	def hit(self, hitter):
		self.health = self.health - hitter.damage
		
#Add one player
players.append(Player())

def check_collision(a, b):
	if (a.x + a.width > b.x) and (a.x < b.x + b.width) and (a.y + a.height > b.y) and (a.y < b.y + b.height):
		return true
	else:
		return false


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

class StandardBot(Bot):
	def __init__(self, plx, ply):
		x1 = 0
		y1 = 0
		x2 = plx
		y2 = ply
		if(plx > win_width/2):
			if (ply > win_height/2):
				x1,y1,x2,y2 = 0,0, x2-20,y2-20
			else:
				x1,y2,x2,y1 = 0, win_height,x2-20, y2+20
		else:
			if (ply > win_height/2):
				x2,y1,x2,y1 = win_width, 0,x2+20,y2-20
			else:
				x2,y2,x2,y2 = win_width, win_height,x2+20,y2+20
		self.speed = random.random()*10
		bots.append(self)

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
		self.image = pygame.image.load("bullet" + mode + ".png").convert()

		# vector of bullet
		self.vx = math.cos(angle)
		self.vy = math.sin(angle)
	def update(self, dt = 1):
		self.x += self.vx*dt
		self.y += self.vy*dt


def update():
	global bot_ctr, dt, last_shot, mouse_x, mouse_y
	bot_ctr += dt
	if (bot_ctr >= 4000):
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
			pass
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1 and last_shot > 10:
				shots.append(Shot(players[0].x, players[0].y, players[0].ch_angle))
				last_shot = 0
		else:
			last_shot += dt
		if event.type == pygame.MOUSEMOTION:
			mouse_x, mouse_y = event.pos
	keys = pygame.key.get_pressed()
	if keys[pygame.K_RIGHT]: players[0].x += 1
	if keys[pygame.K_LEFT]: players[0].x -= 1
	if keys[pygame.K_DOWN]: players[0].y += 1
	if keys[pygame.K_UP]: players[0].y -= 1
	#Calculate crosshair coords
	players[0].ch_angle=-math.atan2((mouse_x-players[0].x),(mouse_y-players[0].y)) + math.pi/2
	players[0].ch_x1=math.cos(players[0].ch_angle)*ch_iradius+players[0].x
	players[0].ch_y1=math.sin(players[0].ch_angle)*ch_iradius+players[0].y
	players[0].ch_x2=math.cos(players[0].ch_angle)*ch_oradius+players[0].x
	players[0].ch_y2=math.sin(players[0].ch_angle)*ch_oradius+players[0].y
	players[0].update()

def draw():
	text = font.render("Time :" + str(clock.get_time()) + " and " + str(dt),True,(255,255,255))
	# Blit everything to the screen
	screen.blit(background, (0, 0))
	screen.blit(text, (0,0))
	for i in bots:
		pygame.draw.circle(screen, (255,255,255), (int(i.x), int(i.y)), 10)
	for i in shots:
		pygame.draw.circle(screen, (255,0,0), (int(i.x), int(i.y)), 10)
	pygame.draw.line(screen, (255,255,255), (players[0].ch_x1, players[0].ch_y1), (players[0].ch_x2, players[0].ch_y2))
	#screen.blit(players[0].image, (int(players[0].x) - players[0].width/2,int(players[0].y) - players[0].height/2))
	screen.blit(pygame.transform.rotate(players[0].image, -math.degrees(players[0].ch_angle)),(int(players[0].x) - players[0].width/2,int(players[0].y) - players[0].height/2))
	pygame.display.flip()

while True:
	dt = clock.get_time()
	update()
	draw()
	pygame.display.update()
	clock.tick_busy_loop()
