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
	
def update(dt):
bot_ctr = bot_ctr + dt
if ( bot_ctr >= 0.2) then
bot_ctr = 0
spawn_bot()
end
    if (love.keyboard.isDown("right") and players[1].x < win_width) then
        players[1].x = players[1].x + (players[1].speed * dt)
    elseif (love.keyboard.isDown("left") and players[1].x > 0) then
        players[1].x = players[1].x - (players[1].speed * dt)
    end
    
    if (love.keyboard.isDown("down") and players[1].y < win_height ) then
        players[1].y = players[1].y + (players[1].speed * dt)
    elseif love.keyboard.isDown("up") and players[1].y > 0 then
        players[1].y = players[1].y - (players[1].speed * dt)
    end
    if (love.mouse.isDown( "l" ) and last_shot >= cooldown) then
        table.insert(shots, Shot.create{ width=8,
height=3,
speed=400,
damage=20,
angle=players[1].ch_angle,
vx=math.cos(players[1].ch_angle),
vy=math.sin(players[1].ch_angle)
})
        last_shot = 0
    else
        last_shot = last_shot + dt
    end
    
    adv_shots(shots, bots, dt)
move_bots(bots, dt)

    mouse_x = love.mouse.getX()
    mouse_y = love.mouse.getY()
    
    --Calculate crosshair coords
    players[1].ch_angle=-math.atan2((mouse_x-players[1].x),(mouse_y-players[1].y)) + math.pi/2
    ch_x1=math.cos(players[1].ch_angle)*ch_iradius+players[1].x
    ch_y1=math.sin(players[1].ch_angle)*ch_iradius+players[1].y
    ch_x2=math.cos(players[1].ch_angle)*ch_oradius+players[1].x
    ch_y2=math.sin(players[1].ch_angle)*ch_oradius+players[1].y

load()
while 1:
	for event in pygame.event.get():
		if event.type == QUIT:
			return
	update()
		draw()