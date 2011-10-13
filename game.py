#!/usr/bin/python
import pygame
from pygame.locals import *
pygame.init()
def load():
	class Player:
		def __init__(self):
			x = 0
			y = 0
			width = 20
			height = 20
			firemode = 0
			ch_angle = 0
			speed = 300
	class Bot:
		def __init__(self):
			x = 0
			y = 0
			max_health = 100
			health = max_health
			alpha = 255
			width = 20
			height = 20
			reward = 100
			angle = 0
			vx = 0
			vy = 0
			speed = 0.1
	class Shot:
		def __init__(self, x=0, y=0, angle=0, damage=100, width=):
			x = 0
			y = 0
			angle = 0
			speed = 100
			damage = 100
			width = 10
			height = 3
			mode = 1
			image = love.graphics.newImage("bullet" .. mode .. ".png")
	
			-- vector of bullet
			vx = math.cos(angle)
			vy = math.sin(angle)
	pygame.init()
	screen = pygame.display.set_mode((150, 50))
	pygame.display.set_caption('Biggest Idiotic Program')
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((250, 250, 250))
	# Display some text
	font = pygame.font.Font(None, 36)
	text = font.render("Hello There", 1, (10, 10, 10))
	textpos = text.get_rect()
	textpos.centerx = background.get_rect().centerx
	background.blit(text, textpos)

	# Blit everything to the screen
	screen.blit(background, (0, 0))
	pygame.display.flip()


		screen.blit(background, (0, 0))
		pygame.display.flip()

def update():
	


if __name__ == '__main__':
	load()
	while 1:
		for event in pygame.event.get():
			if event.type == QUIT:
				return
		update()
		draw()