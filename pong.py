##########################################################################################################################################
# 															pong.py
#										This game was created using pygame in python 3
# 									Pong game written by Aaron Baumgartner - December 2021			    
# 		This game utilizes OOP concepts, game design techniques, and some math to predict the trajectory/path of the pong ball
#							 In order to run this game, pygame must be installed (pip install pygame)
#														Thanks for playing!
##########################################################################################################################################
import pygame, sys
from pygame.locals import *
import random, time

pygame.init()

# setup fps values
FPS = 60
FramePerSec = pygame.time.Clock()
tick_count = 1

# colors
WHITE = (255,255,255)
BLACK = (0,0,0)

# dispay information
width = 1100
height = 650
draw_prediction_line = False
mouse_over = False

# ball/player/ai speed information
paddle_speed = 10
ai_paddle_speed = 10
ai_reaction = False
prediction = True
ball_speed_x = 7
ball_speed_y = 6
ball_speed_inc = 0.5
MAX_BALL_SPEED = 10

# game state information
reset = False
difficulty = ''
running = False
play_again = False
players = 1

# setup display
game_board = pygame.display.set_mode((width,height))
game_board.fill(BLACK)
pygame.display.set_caption("Pong")

# fonts
font_title = pygame.font.SysFont("Verdana", 50)
font = pygame.font.SysFont("Verdana", 30)
font_small = pygame.font.SysFont("Verdana", 20)



# Game Objects Paddle/Ball
class Paddle(pygame.sprite.Sprite):
	def __init__(self, xpos, ypos):
		super().__init__()
		self.rect = pygame.Rect(xpos, ypos, 20, 100)
		self.score = 0

	# the move() function is used for the player to manually move the paddle
	def move(self):
		pressed_keys = pygame.key.get_pressed()

		if self.rect.top > 0:
			if pressed_keys[K_UP]:
				self.rect.move_ip(0,-paddle_speed)
		if self.rect.bottom < height:
			if pressed_keys[K_DOWN]:
				self.rect.move_ip(0,paddle_speed)

	# the move_ai() function automatically moves the paddle based on a desired y position (this y position will be obtained from a calculated prediction)
	def move_ai(self,Ball,ypos):
		if self.rect.top > ypos-40 and self.rect.top > 0:
			self.rect.move_ip(0,-ai_paddle_speed)
		elif self.rect.bottom < ypos+40 and self.rect.bottom < height:
			self.rect.move_ip(0, ai_paddle_speed)

	# Calculate what y position the ball will be at when it reaches the paddle (add random error to make the computer beatable)
	def ai_prediction(self,Ball,difficulty):
		if difficulty == 'easy':
			rand_error = 150
		elif difficulty == 'medium':
			rand_error = 75
		elif difficulty == 'hard':
			rand_error = 25
		elif difficulty == 'insane':
			rand_error = 1
		# calculate the time it will take the ball to reach the ceiling/floor
		if ball_speed_y > 0:
			time_to_vert = (height - Ball.rect.bottom)/ball_speed_y
		elif ball_speed_y < 0:
			time_to_vert = -(Ball.rect.top)/ball_speed_y
		else:
			time_to_vert = 0

		# calculate the time it will take the ball to reach one of the walls
		if ball_speed_x < 0:
			time_to_wall = (Ball.rect.left - 30)/-ball_speed_x
		if ball_speed_x > 0:
			time_to_wall = (width - 30 - Ball.rect.right)/ball_speed_x

		### This commented code calculates the expected y position after a floor/ceiling bounce ###
		### This code isnt being used because we can just recalculate the exact y position with no bounce anytime we hit the ceiling or the floor ###
		#if time_to_vert < time_to_wall and ball_speed_y > 0:
		#	time_to_wall = time_to_wall - time_to_vert
		#	y_prediction = height - (ball_speed_y*time_to_wall)
		#elif time_to_vert < time_to_wall and ball_speed_y < 0:
		#	time_to_wall = time_to_wall - time_to_vert
		#	y_prediction = -ball_speed_y*time_to_wall

		# find the exact location the ball will end up (this calculation does not take into account any ceiling/floor bounces)
		if ball_speed_y > 0:
			y_prediction = Ball.rect.bottom + (time_to_wall)*ball_speed_y + 7.5
		elif ball_speed_y < 0:
			y_prediction = Ball.rect.top + time_to_wall*ball_speed_y + 7.5
		else:
			y_prediction = Ball.rect.top+7.5

		# introduce +/- random error to the y position to make the cpu miss occasionally (increasing/decreasing this error will increase/decrease the difficulty)
		if random.random() < 0.5:
			return y_prediction+random.randint(0,rand_error)
		else:
			return y_prediction-random.randint(0,rand_error)

	# reset the paddles back to the middle of the screen (do this anytime a point is scored)
	def reset(self):
		self.rect = pygame.Rect(10,height/2-100, 20, 100)



class Ball(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.rect = pygame.Rect(width/2-10, height/2-10, 15, 15)

	# move the ball based on the current x and y speed
	def move(self,Ai,P1):
		global ball_speed_y
		global ball_speed_x

		# if the ball hits the floor/ceiling, bounce the ball back in the opposite y direction
		if self.rect.top < 0 or self.rect.bottom > height:
			ball_speed_y = -ball_speed_y
		self.rect.move_ip(ball_speed_x, ball_speed_y)

		# check scoring conditions (return True if someone scored)
		if self.rect.left > width:
			Ai.score += 1
			self.reset()
			Ai.reset()
			return True
		elif self.rect.right < 0:
			P1.score += 1
			self.reset()
			Ai.reset()
			return True
		return False

	# reset the ball to the middle of the screen (do this anytime a point is scored)
	def reset(self):
		global ball_speed_x
		global ball_speed_y
		global ball_speed_inc

		# revert the speeds back to their original values
		ball_speed_x = 7
		ball_speed_y = random.randint(6,10)
		ball_speed_inc = 1

		self.rect = pygame.Rect(width/2-10, height/2-10, 15, 15)

		# launch the ball in a random direction to start
		if random.randint(0, 1) == 0:
			ball_speed_x = -ball_speed_x
		if random.randint(0, 1) == 0:
			ball_speed_y = -ball_speed_y


# Game display functions 
def menu():
	title = font.render('Welcome to Pong!', True, WHITE)
	sel_difficulty = font.render('Please select your difficulty:', True, WHITE)
	easy = font.render('Easy', True, WHITE)
	medium = font.render('Medium', True, WHITE)
	hard = font.render('Hard', True, WHITE)
	insane = font.render('Insane', True, WHITE)

	game_board.blit(title, (width/2-130, height/2-260))
	game_board.blit(sel_difficulty, (width/2-200, height/2-150))
	game_board.blit(easy, (width/2-40, height/2-70))
	game_board.blit(medium, (width/2-60, height/2-10))
	game_board.blit(hard, (width/2-40, height/2+50))
	game_board.blit(insane, (width/2-55, height/2+110))

	pygame.display.update()

def countdown():
	three = font_title.render('3', True, WHITE)
	two = font_title.render('2', True, WHITE)
	one = font_title.render('1', True, WHITE)

	game_board.fill(BLACK)
	game_board.blit(three, (width/2-20, height/2-50))
	pygame.display.update()
	time.sleep(1)
	game_board.fill(BLACK)
	game_board.blit(two, (width/2-20, height/2-50))
	pygame.display.update()
	time.sleep(1)
	game_board.fill(BLACK)
	game_board.blit(one, (width/2-20, height/2-50))
	pygame.display.update()
	time.sleep(1)
	game_board.fill(BLACK)

def wall_time(Ball):
	if ball_speed_x < 0:
		return (Ball.rect.left - 30)/-ball_speed_x, 30
	else:
		return (width-30-Ball.rect.right)/ball_speed_x, width-30

def vert_time(Ball):
	if ball_speed_y > 0:
		return (height - Ball.rect.bottom)/ball_speed_y
	else:
		return -(Ball.rect.top)/ball_speed_y

def prediction_line(Ball):
	if not(draw_prediction_line):
		return list([False,False])

	time_to_wall, line_x_pos = wall_time(Ball)
	time_to_vert = vert_time(Ball)
	vert_x = Ball.rect.left+15-time_to_vert*-ball_speed_x

	if time_to_vert < time_to_wall and ball_speed_y > 0:
		time_to_wall = time_to_wall - time_to_vert
		pygame.draw.line(game_board, WHITE, (Ball.rect.left,Ball.rect.bottom), (vert_x,height))
		pygame.draw.line(game_board, WHITE, (vert_x,height), (line_x_pos,height-time_to_wall*ball_speed_y))
	elif time_to_vert < time_to_wall and ball_speed_y < 0:
		time_to_wall = time_to_wall - time_to_vert
		pygame.draw.line(game_board, WHITE, (Ball.rect.left,Ball.rect.top), (vert_x,0))
		pygame.draw.line(game_board, WHITE, (line_x_pos,time_to_wall*-ball_speed_y), (vert_x,0))
	elif ball_speed_y > 0:
		pygame.draw.line(game_board, WHITE, (line_x_pos,Ball.rect.bottom+time_to_wall*ball_speed_y), (Ball.rect.left,Ball.rect.bottom))
	elif ball_speed_y < 0:
		pygame.draw.line(game_board, WHITE, (line_x_pos,Ball.rect.top+time_to_wall*ball_speed_y), (Ball.rect.left,Ball.rect.top))
	else:
		pygame.draw.line(game_board, WHITE, (line_x_pos,Ball.rect.top+7.5), (Ball.rect.left,Ball.rect.top+7.5))

def game_over():
	pygame.draw.rect(game_board, BLACK, Rect(width/2+width/4-125, height/2-70, 250, 55))
	pygame.draw.rect(game_board, BLACK, Rect(width/2+width/4-125, height/2, 250, 55))

	pygame.draw.rect(game_board, WHITE, Rect(width/2+width/4-125, height/2-70, 250, 55), 2, 5)
	game_board.blit(font.render("Play again?", True, WHITE), (width/2+width/4-86, height/2-64))

	pygame.draw.rect(game_board, WHITE, Rect(width/2+width/4-125, height/2, 250, 55), 2, 5)
	game_board.blit(font.render("Exit", True, WHITE), (width/2+width/4-30, height/2+7))

	pygame.display.update()

# Setup Paddles/Ball
Ai = Paddle(10,height/2-100)
P1 = Paddle(width-30, height/2-100)
Ball = Ball()

paddles = pygame.sprite.Group()
paddles.add(Ai)
paddles.add(P1)

# display the opening menu
menu()

# Start the main game loop
while True:
	# event handling
	for event in pygame.event.get():
		# close application
		if event.type == QUIT:
			pygame.quit()
			sys.exit()

		# keyboard events
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_p:
				if draw_prediction_line:
					draw_prediction_line = False
				else:
					draw_prediction_line = True
			if event.key == pygame.K_ESCAPE:
				if running:
					game_board.blit(font_title.render("Paused", True, WHITE), (width/2-90,height/2-30))
					pygame.display.update()
				running = not running
			if event.key == pygame.K_q:
				if not running:
					game_board.fill(BLACK)
					difficulty = ''
					prediction = True
					P1.score = 0
					Ai.score = 0
					Ball.reset()
					menu()

		# mouse events
		if event.type == pygame.MOUSEBUTTONDOWN:
			if not running and not play_again:
				mouse = event.pos
				if width/2-40 <= mouse[0] <= width/2+40 and height/2-70 <= mouse[1] <= height/2-30:
					difficulty = 'easy'
					running = True
					countdown()
				if width/2-60 <= mouse[0] <= width/2+60 and height/2-10 <= mouse[1] <= height/2+30:
					difficulty = 'medium'
					ball_speed_y += 3
					ball_speed_inc += 0.5
					MAX_BALL_SPEED = 15
					running = True
					countdown()
				if width/2-40 <= mouse[0] <= width/2+40 and height/2+50 <= mouse[1] <= height/2+90:
					difficulty = 'hard'
					ball_speed_y += 3
					ball_speed_inc += 1
					MAX_BALL_SPEED = 20
					ai_paddle_speed = 15
					running = True
					countdown()
				if width/2-55 <= mouse[0] <= width/2+55 and height/2+110 <= mouse[1] <= height/2+150:
					difficulty = 'insane'
					ball_speed_y += 4
					ball_speed_inc += 2
					MAX_BALL_SPEED = 20
					FPS += 40
					running = True
			else:
				mouse = event.pos
				if width/2+width/4-125 <= mouse[0] <= width/2+width/4+125:
					if height/2-70 <= mouse[1] <= height/2-15:
						running = True
						play_again = False
						P1.score = 0
						Ai.score = 0
					elif height/2 <= mouse[1] <= height/2+55:
						pygame.quit()
						sys.exit()

	# mouse hover event
	if not running and play_again:
		s = pygame.Surface((246,51), pygame.SRCALPHA)
		s.fill((255,255,255,128))
		mouse = pygame.mouse.get_pos()
		if width/2+width/4-125 <= mouse[0] <= width/2+width/4+125:
			if height/2-70 <= mouse[1] <= height/2-15:
				if not mouse_over:
					mouse_over = True
					game_board.blit(s,(width/2+width/4-123,height/2-68))
			elif height/2 <= mouse[1] <= height/2+55:
				if not mouse_over:
					mouse_over = True
					game_board.blit(s,(width/2+width/4-123,height/2+2))
			else:
				mouse_over = False
				game_over()
		else:
			mouse_over = False
			game_over()

		pygame.display.update()

	# Begin the pong game with the desired difficulty
	if difficulty != '' and running:
		game_board.fill(BLACK)

		# setup initial prediction
		if prediction:
			if ball_speed_x > 0:
				ypos = P1.ai_prediction(Ball,difficulty)
			else:
				ypos = Ai.ai_prediction(Ball,difficulty)
			prediction = False

		# display scores
		player_score = font_small.render(str(P1.score), True, WHITE)
		ai_score = font_small.render(str(Ai.score), True, WHITE)
		game_board.blit(player_score, (width-100,10))
		game_board.blit(ai_score, (10,10))		

		# update and draw game entities
		prediction_line(Ball)
		if ball_speed_x < 0 and players != 2:
			if pygame.sprite.collide_rect(P1,Ball) or Ball.rect.top < 10 or Ball.rect.bottom > height-10:
				ypos = Ai.ai_prediction(Ball,difficulty)
			if difficulty == 'hard' or difficulty == 'insane':
				if random.randint(0,5000) == 0:
					if random.random() < 0.5:
						ypos += random.randint(0,100)
					else:
						ypos -= random.randint(0,100)
			Ai.move_ai(Ball,ypos)
		elif players == 2:
			Ai.move()
		if ball_speed_x > 0 and players == 0:
			if tick_count%20  == 0:
				ypos = P1.ai_prediction(Ball,difficulty)
			P1.move_ai(Ball,ypos)
		else:
			P1.move()
		for entity in paddles:
			pygame.draw.rect(game_board, WHITE, entity.rect)
		pygame.draw.rect(game_board, WHITE, Ball)
		pygame.draw.line(game_board, WHITE, (width/2,0), (width/2,height))

		# detect collision with the ball and the paddles
		if pygame.sprite.spritecollideany(Ball, paddles):
			prediction = True
			if ball_speed_x+ball_speed_inc > MAX_BALL_SPEED:
				ball_speed_x = MAX_BALL_SPEED
				ball_speed_inc = 0
			elif ball_speed_x-ball_speed_inc < -MAX_BALL_SPEED:
				ball_speed_x = -MAX_BALL_SPEED
				ball_speed_inc = 0
			if ball_speed_x > 0:
				ball_speed_x = -(ball_speed_x+ball_speed_inc)
			else:
				ball_speed_x = -(ball_speed_x-ball_speed_inc)
			if Ball.rect.left < 10:
				ball_speed_x = -ball_speed_x
			elif Ball.rect.right > width-10:
				ball_speed_x = -ball_speed_x
			if Ball.rect.right > width/2:
				if Ball.rect.bottom+7.5 <= P1.rect.top+25:
					ball_speed_y = -6
				elif Ball.rect.bottom+7.5 >= P1.rect.bottom-25:
					ball_speed_y = 6

		# move the ball after checking for collision to avoid moving the ball inside the paddles
		if Ball.move(Ai, P1):
			reset = True

		if P1.score >= 10:
			game_board.blit(font_title.render("Player 1 wins", True, WHITE), (width/2-190, 100))
			running = False
		elif Ai.score >= 10:
			game_board.blit(font_title.render("CPU wins", True, WHITE), (width/2-110, 100))
			running = False

		#game_board.blit(s,(width/2+width/4-123,height/2-68))
		if P1.score >= 10 or Ai.score >= 10:
			play_again = True
			game_over()

		# update the screen with the new drawings
		pygame.display.update()

		# point scored, sleep for a short time before launching the ball back out
		if reset:
			time.sleep(.2)
			reset = False

	# Run this loop FPS times every second. Default FPS = 60, increasing the FPS will cause everything to move faster
	FramePerSec.tick(FPS)
	tick_count += 1



	# Written by Aaron Baumgartner - December, 2021