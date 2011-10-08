--================ Class definitions
Shot = {} --Shot class
function Shot.create(width, height, mode, speed, damage, angle)
    local sht = {}
    sht.x = players[1].x
    sht.y = players[1].y
    sht.angle = ch_angle
    sht.speed = speed
    sht.damage = damage
	sht.width = width
	sht.height = height
	sht.mode = mode
	sht.image = love.graphics.newImage("bullet" .. mode .. ".png")
    -- vector of bullet
    sht.vx = math.cos(angle)
    sht.vy = math.sin(angle)
    return sht
end

Bot = {} -- Bots table
function Bot.create(x, y, speed, rew) -- no more speed argument ? (determined by rew ?)
    local bt = {}
    bt.x = x
    bt.y = y
    --bt.max_health = math.random(50,200) -- random health
    --bt.max_health = math.random(rew/20 +10, rew/2) -- health determined by rew (+10 is for low rewarding bots)
	bt.max_health = 100 --old fixed health or should the same class bots have same health ?
    bt.health = bt.max_health
	bt.color = bt.health -- not sure if this will not be screwed by random health
	
	bt.width = 20
	bt.height = 20
	bt.reward = rew --Gain obtained by player killing it
	bt.angle = 0
	bt.vx = 0
	bt.vy = 0
	
	--bt.speed = speed
	bt.speed = (rew/10) / bt.max_health -- that will make bots with lots of HP slow
	function bt.hit(hitter)
		bt.health = bt.health - hitter.damage
	end
    return bt
end

Player = {}
function Player.create(x,y)
	local pl = {}
	pl.x = x
	pl.y = y
	pl.width = 10
	pl.height = 10
	pl.firemode = 0
	pl.ch_angle = 0
	pl.speed = 300
	return pl
end

--================

function check_collision(a, b)
if (a.x + a.width > b.x) and (a.x < b.x + b.width) and (a.y + a.height > b.y) and (a.y < b.y + b.height) then
        return true
    else
        return false
    end
end

function spawn_bot()
	local x1,y1,x2,y2=0,0,players[1].x, players[1].y
	if(players[1].x > win_width/2) then
		if (players[1].y > win_height/2) then
			x1,y1,x2,y2 = 0,0, x2-20,y2-20
		else
			x1,y2,x2,y1 = 0, win_height,x2-20, y2+20
		end
	else
		if (players[1].y > win_height/2) then
			x2,y1,x2,y1 = win_width, 0,x2+20,y2-20
		else
			x2,y2,x2,y2 = win_width, win_height,x2+20,y2+20
		end
	end
	sp = math.random(1,20)/10
	--x1,x2,y1,y2 = math.min(x1,x2),math.max(x1,x2),math.min(y1,y2),math.max(y1,y2)
	table.insert(bots,Bot.create(math.random(x1, x2), math.random(y1, y2), sp, sp*1000))
end

function move_bots(b) -- Move bots around
	local old_x=0
	local old_y=1
	for i,v in ipairs(b) do
		if b[i].health <= 0 then
			score = score + b[i].reward
			table.remove(b,i)
			break
		end
		old_x=b[i].x
		old_y=b[i].y
		b[i].angle = -math.atan2((players[1].x-b[i].x),(players[1].y)-b[i].y) + math.pi/2
		b[i].vx = math.cos(b[i].angle)
		b[i].vy = math.sin(b[i].angle)
		b[i].x = b[i].x + b[i].vx * b[i].speed
		b[i].y = b[i].y + b[i].vy * b[i].speed
		if(check_collision(b[i], players[1])) then
			Game = false
		end
		if (b[i].x < 0 or  b[i].x > win_width or b[i].y < 0 or b[i].y > win_height) then
			b[i].x = old_x
			b[i].y = old_y
		end
	end
end

function adv_shots(s, obj, dt) -- Move the shots further and check collisions
	for i, v in ipairs(s) do
		s[i].x = s[i].x + dt * s[i].speed * s[i].vx
		s[i].y = s[i].y + dt * s[i].speed * s[i].vy
		if ( s[i].x < 0 or s[i].x > win_width or s[i].y < 0 or s[i].y > win_height) then
			table.remove(s, i)
		else
			--Check collision between shots and items
			for j, y in ipairs(obj) do
				if check_collision(s[i],obj[j]) then
					boom = boom + 1
					obj[j].hit(s[i])
				end
			end
		end
    end
end

function love.load()

	Game = true
	
	-- Windows definitions
	love.graphics.setCaption( "BIP" ) --Defining window title
    win_height = love.graphics.getHeight()
    win_width = love.graphics.getWidth()
    
    mouse_x = 0
    mouse_y = 0
	
	-- player definitions
	players = {}
	players[1] = Player.create(win_width/2, win_height/2)
    
    score = 0
	
    -- crosshair definitions
    ch_x1=0
    ch_y1=0
    ch_x2=0
    ch_y2=0
    ch_iradius=40
    ch_oradius=45
    
    love.graphics.setLine( 3, "smooth" )
    ship = love.graphics.newImage("ship.png")
    cooldown = 0.3 -- delay before new shot, in seconds
    last_shot = cooldown -- time since last shot, initialized to allow immediate shooting at start
    bots = {} --Table containing all the bots
	table.insert(bots,Bot.create(5, 90, 1, 10)) --Create a first bot
    shots = {} -- table of player shots
    boom = 0 -- Number of hits
	bot_ctr = 0 -- Time since last spawn of bot
    end
    
function love.update(dt)
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
    shot_type = "cl" -- ugly hack for 2 lines under
    if (love.mouse.isDown( "l" ) and last_shot >= cooldown) then
        table.insert(shots, Shot.create(8, 3, 1, 400, 20, ch_angle))
        last_shot = 0
    else
        last_shot = last_shot + dt
    end
    adv_shots(shots, bots, dt)
	--if love.mouse.isDown( "r" ) then
	move_bots(bots, dt)
	--end
    mouse_x = love.mouse.getX()
    mouse_y = love.mouse.getY()
    ch_angle=-math.atan2((mouse_x-players[1].x),(mouse_y-players[1].y)) + math.pi/2
    ch_x1=math.cos(ch_angle)*ch_iradius+players[1].x
    ch_y1=math.sin(ch_angle)*ch_iradius+players[1].y
    ch_x2=math.cos(ch_angle)*ch_oradius+players[1].x
    ch_y2=math.sin(ch_angle)*ch_oradius+players[1].y
end

function love.draw()
    --love.graphics.print("Hello World", 400, 300)
    --love.graphics.point(x,y)
    love.graphics.draw( ship, players[1].x , players[1].y, ch_angle, 2, 2, 8, 8 )
    love.graphics.line( ch_x1, ch_y1, ch_x2, ch_y2 )
    for i, v in ipairs(shots) do
		love.graphics.draw (shots[i].image , shots[i].x, shots[i].y, shots[i].angle, 1, 1)
    end
	love.graphics.setColor(255,0,0,255)
	for j,v in ipairs(bots) do
		love.graphics.setColor(255,0,0,bots[j].health/bots[j].max_health*255)
		love.graphics.circle ("line", bots[j].x, bots[j].y, 10, 3)
    end
	love.graphics.setColor(255,255,255,255)
    --=== Debug
    --love.graphics.print (bots[j].x ,45, 120)
    --love.graphics.print(last_shot, 100, 200)
    --if (#shots >= 1) then
    --love.graphics.print(math.floor(shots[1].x) .. "*" .. math.floor(shots[1].y), 100, 100)
    --end
     if (score) then
         love.graphics.print("Score : " .. score, 100, 300)
     end
    --love.graphics.print( #shots, 50, 200)
	love.graphics.print("FPS: " .. love.timer.getFPS(), 540, 10)
    -- for i,v in ipairs(shots) do
        -- love.graphics.print(math.floor(shots[1].x))
    -- end
    --love.graphics.print(shots[2].x .. shots[2].y, 100, 200)
    
    --===
end