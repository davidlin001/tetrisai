"""
Primary Modifications;
Added a run_baseline() method (with modified fps time)
Run baseline tests in main
"""
#!/usr/bin/env python2
#-*- coding: utf-8 -*-

# Very simple tetris implementation
# 
# Control keys:
#       Down - Drop stone faster
# Left/Right - Move stone
#         Up - Rotate Stone clockwise
#     Escape - Quit game
#          P - Pause game
#     Return - Instant drop
#
# Have fun!

# Copyright (c) 2010 "Laria Carolin Chabowski"<me@laria.me>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from random import randrange as rand
import random
import pygame, sys
import baseline
import tetrisai
import copy
import time

# The configuration
cell_size =	18
cols =		10
rows =		22
maxfps = 	30

colors = [
(0,   0,   0  ),
(255, 85,  85),
(100, 200, 115),
(120, 108, 245),
(255, 140, 50 ),
(50,  120, 52 ),
(146, 202, 73 ),
(150, 161, 218 ),
(35,  35,  35) # Helper color for background grid
]

# Define the shapes of the single parts
tetris_shapes = [
	[[1, 1, 1],
	 [0, 1, 0]],
	
	[[0, 2, 2],
	 [2, 2, 0]],
	
	[[3, 3, 0],
	 [0, 3, 3]],
	
	[[4, 0, 0],
	 [4, 4, 4]],
	
	[[0, 0, 5],
	 [5, 5, 5]],
	
	[[6, 6, 6, 6]],
	
	[[7, 7],
	 [7, 7]]
]

def rotate_clockwise(shape):
	return [ [ shape[y][x]
			for y in xrange(len(shape)) ]
		for x in xrange(len(shape[0]) - 1, -1, -1) ]

def check_collision(board, shape, offset):
	off_x, off_y = offset
	for cy, row in enumerate(shape):
		for cx, cell in enumerate(row):
			try:
				if cell and board[ cy + off_y ][ cx + off_x ]:
					return True
			except IndexError:
				return True
	return False

def remove_row(board, row):
	del board[row]
	return [[0 for i in xrange(cols)]] + board
	
def join_matrixes(mat1, mat2, mat2_off):
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			mat1[cy+off_y-1	][cx+off_x] += val
	return mat1

def new_board():
	board = [ [ 0 for x in xrange(cols) ]
			for y in xrange(rows) ]
	board += [[ 1 for x in xrange(cols)]]
	return board

class TetrisApp(object):
	def __init__(self):
		pygame.init()
		pygame.key.set_repeat(250,25)
		self.width = cell_size*(cols+6)
		self.height = cell_size*rows
		self.rlim = cell_size*cols
		self.bground_grid = [[ 8 if x%2==y%2 else 0 for x in xrange(cols)] for y in xrange(rows)]
		
		self.default_font =  pygame.font.Font(
			pygame.font.get_default_font(), 12)
		
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.event.set_blocked(pygame.MOUSEMOTION) # We do not need
		                                             # mouse movement
		                                             # events, so we
		                                             # block them.
		self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
		self.init_game()
		self.key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		lambda:self.drop(True),
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'SPACE':	self.start_game,
			'RETURN':	self.insta_drop
		}
	
	def new_stone(self):
		self.stone = self.next_stone[:]
		self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
		self.stone_x = int(cols / 2 - len(self.stone[0])/2)
		self.stone_y = 0
		
		if check_collision(self.board,
		                   self.stone,
		                   (self.stone_x, self.stone_y)):
			self.gameover = True
	
	def init_game(self):
		self.board = new_board()
		self.new_stone()
		self.level = 1
		self.score = 0
		self.lines = 0
		pygame.time.set_timer(pygame.USEREVENT+1, 1000)
	
	def disp_msg(self, msg, topleft):
		x,y = topleft
		for line in msg.splitlines():
			self.screen.blit(
				self.default_font.render(
					line,
					False,
					(255,255,255),
					(0,0,0)),
				(x,y))
			y+=14
	
	def center_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  self.default_font.render(line, False,
				(255,255,255), (0,0,0))
		
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x //= 2
			msgim_center_y //= 2
		
			self.screen.blit(msg_image, (
			  self.width // 2-msgim_center_x,
			  self.height // 2-msgim_center_y+i*22))
	
	def draw_matrix(self, matrix, offset):
		off_x, off_y  = offset
		for y, row in enumerate(matrix):
			for x, val in enumerate(row):
				if val:
					pygame.draw.rect(
						self.screen,
						colors[val],
						pygame.Rect(
							(off_x+x) *
							  cell_size,
							(off_y+y) *
							  cell_size, 
							cell_size,
							cell_size),0)
	
	def add_cl_lines(self, n):
		linescores = [0, 40, 100, 300, 1200]
		self.lines += n
		self.score += linescores[n] * self.level
		if self.lines >= self.level*6:
			self.level += 1
			newdelay = 1000-50*(self.level-1)
			newdelay = 100 if newdelay < 100 else newdelay
			pygame.time.set_timer(pygame.USEREVENT+1, newdelay)
	
	def move(self, delta_x):
		if not self.gameover and not self.paused:
			new_x = self.stone_x + delta_x
			if new_x < 0:
				new_x = 0
			if new_x > cols - len(self.stone[0]):
				new_x = cols - len(self.stone[0])
			if not check_collision(self.board,
			                       self.stone,
			                       (new_x, self.stone_y)):
				self.stone_x = new_x
	def quit(self):
		self.center_msg("Exiting...")
		pygame.display.update()
		sys.exit()
	
	def drop(self, manual):
		if not self.gameover and not self.paused:
			self.score += 1 if manual else 0
			self.stone_y += 1
			if check_collision(self.board,
			                   self.stone,
			                   (self.stone_x, self.stone_y)):
				self.board = join_matrixes(
				  self.board,
				  self.stone,
				  (self.stone_x, self.stone_y))
				self.new_stone()
				cleared_rows = 0
				while True:
					for i, row in enumerate(self.board[:-1]):
						if 0 not in row:
							self.board = remove_row(
							  self.board, i)
							cleared_rows += 1
							break
					else:
						break
				self.add_cl_lines(cleared_rows)
				return True
		return False
	
	def insta_drop(self):
		if not self.gameover and not self.paused:
			while(not self.drop(True)):
				pass
	
	def rotate_stone(self):
		if not self.gameover and not self.paused:
			new_stone = rotate_clockwise(self.stone)
			if not check_collision(self.board,
			                       new_stone,
			                       (self.stone_x, self.stone_y)):
				self.stone = new_stone
	
	def toggle_pause(self):
		self.paused = not self.paused
	
	def start_game(self):
		if self.gameover:
			self.init_game()
			self.gameover = False
	
	def td_learning(self, weights):
		self.board = new_board()
		print self.board
		'''
		pygame.init()
		self.width = cell_size*(cols+6)
		self.height = cell_size*rows
		self.rlim = cell_size*cols
		self.init_game()
		'''
		self.gameover = False
		self.paused = False

		while not self.gameover:
			self.stone = self.next_stone
			self.stone_x = int(cols/2 - len(self.stone[0])/2)
			self.stone_y = 0
			if (check_collision(self.board, self.stone, (self.stone_x, self.stone_y))):
				self.gameover = True 
				return weights 

			features = tetrisai.extractFeatures(self.board, self.stone)
			eta = 0.01
			discount = 1

			prev_dot_product = 0
			for i in range(len(weights)):
				prev_dot_product += weights[i]*features[i]
			prev_score = self.score
			prev_lines = self.lines
			moves = baseline.findBestMove(self.board, self.stone, self.stone_x)
			for move in moves:
				self.key_actions[move]()
			'''
			# Random number of rotations
			numRotations = random.randint(0,3)
			for i in range(numRotations):
				key_actions["UP"]()
			
			# Random left right translation
			if random.randint(0,1) == 0:
				range_left = self.stone_x 
				for i in range(random.randint(0,range_left)):
					key_actions['LEFT']()
			else:
				range_right = len(self.board[0]) - (self.stone_x + len(self.stone[0]))
				for i in range(random.randint(0,range_right)):
					key_actions['RIGHT']()
			key_actions['RETURN']() '''

			new_score = self.score
			#score_reward = new_score - prev_score	
			reward = 10000*(self.lines - prev_lines)**2
			if self.gameover:
				print "GESSSS HERE"
				reward = -1000
			self.next_stone = tetris_shapes[rand(len(tetris_shapes))]

			newFeatures = tetrisai.extractFeatures(self.board, self.next_stone)
			new_dot_product = 0
			for i in range(len(weights)):
				new_dot_product += weights[i]*newFeatures[i]

			print prev_dot_product, new_dot_product
			for index, weight in enumerate(weights):
				weights[index] = weight - eta*(prev_dot_product - (reward + discount*new_dot_product))*features[index]
			sumWeights = sum(weights) + .01
			weights = [weight*1.0/sumWeights for weight in weights]
			print "Features", features
			print "WEIGHTS", weights
		return weights

	def train_evaluation_function(self):
		# EDIT THIS LATER!!!
		lenFeatures = len(tetrisai.extractFeatures(self.board, self.stone))
		weights = [0]*lenFeatures
		numGames = 30
		for i in range(numGames):
			print "GAME", i
			weights = self.td_learning(weights)	
		
		#weights = td_learning(self, weights)
		return weights

	def test_evaluation_function(self, weights, features):
		return sum([weights[i]*features[i] for i in range(len(weights))])	

	# For every possible action sequence, we try the action and retrieve the score 
	# of its successor
	def trySequence(self, weights, actionSequence, bestScore, bestSequence):
		#print "BEST SEQUENCE", bestSequence
		original_score = self.score
		#Maybe need to copy
		original_board = copy.deepcopy(self.board)
		original_stone = self.stone
		original_stone_x = self.stone_x
		original_stone_y = self.stone_y
		original_lines = self.lines

		#print "original"
		#print original_board

		for move in actionSequence:
			self.key_actions[move]()
		self.key_actions["RETURN"]()

		features = tetrisai.extractFeatures(self.board, self.next_stone)
		#print "Features for attempt",
		#print features

		score = self.test_evaluation_function(weights, features)
		
		#print "attempted: sequence", actionSequence, "score", score
		#print "resulting board"
		#print self.board
		# After trying the move, we have to revert everything
		self.score = original_score
		self.board = original_board
		self.stone = original_stone
		self.stone_x = original_stone_x
		self.stone_y = original_stone_y
		self.lines = original_lines
		#print "new board"
		#print self.board
		if score < bestScore:
			return score, list(actionSequence)
		else: 
			return bestScore, bestSequence

	# For every possible action sequence, we try the action and retrieve the score 
	# of its successor
	def getScore(self, weights, actionSequence, bestScore, bestSequence):
		#print "BEST SEQUENCE", bestSequence
		original_score = self.score
		#Maybe need to copy
		original_board = copy.deepcopy(self.board)
		original_stone = self.stone
		original_stone_x = self.stone_x
		original_stone_y = self.stone_y
		original_lines = self.lines

		#print "original"
		#print original_board

		for move in actionSequence:
			self.key_actions[move]()
		self.key_actions["RETURN"]()

		features = tetrisai.extractFeatures(self.board, self.next_stone)
		score = self.test_evaluation_function(weights, features)

		# After trying the move, we have to revert everything
		self.score = original_score
		self.board = original_board
		self.stone = original_stone
		self.stone_x = original_stone_x
		self.stone_y = original_stone_y
		self.lines = original_lines
		#print "new board"
		#print self.board
		return score

	def trySequence2(self, cutoff, weights, depth, actionSequence, bestScore, bestSequence):
		# Cache all old values
		original_score = self.score
		original_board = copy.deepcopy(self.board)
		original_stone = copy.deepcopy(self.stone)
		original_stone_x = self.stone_x
		original_stone_y = self.stone_y
		original_lines = self.lines
		original_next_stone = copy.deepcopy(self.next_stone)

		#print "original"
		#print original_board

		for move in actionSequence:
			self.key_actions[move]()
		self.key_actions["RETURN"]()

		features = tetrisai.extractFeatures(self.board, self.next_stone)
		score = self.test_evaluation_function(weights, features)
		#print "Features for attempt",
		#print features
		if (depth > 1 and score > cutoff):
			range_rotations = 3
			range_left = 5
			range_right = 6
			#range_left = self.stone_x 
			#range_right = len(self.board[0]) - (self.stone_x + len(self.stone[0])) + 1

			# Find best action sequence and its corresponding evaluation functino score
			nextBestScore = 999999999999999
			nextBestSequence = [] 
			nextActionSequence = [] 

			nextBestScore, nextBestSequence = self.trySequence2(cutoff, weights, depth-1, nextActionSequence, nextBestScore, nextBestSequence) 
			for i in range(range_rotations + 1):
				nextBestScore, nextBestSequence = self.trySequence2(cutoff, weights, depth-1,nextActionSequence, nextBestScore, nextBestSequence) 
				for j in range(range_left):
					nextActionSequence.append("LEFT")
					nextBestScore, nextBestSequence = self.trySequence2(cutoff, weights, depth-1,nextActionSequence, nextBestScore, nextBestSequence) 
				nextActionSequence = nextActionSequence[0:len(actionSequence) - range_left]
				for j in range(range_right):
					nextActionSequence.append("RIGHT")
					nextBestScore, nextBestSequence = self.trySequence2(cutoff, weights, depth -1,nextActionSequence, nextBestScore, nextBestSequence) 
				nextActionSequence = nextActionSequence[0:len(actionSequence) - range_right]
				nextActionSequence.append("UP")
			nextBestSequence.append("RETURN")
			score += nextBestScore

		# After trying the move sequence, we have to revert everything
		self.score = original_score
		self.board = original_board
		self.stone = original_stone
		self.stone_x = original_stone_x
		self.stone_y = original_stone_y
		self.lines = original_lines
		self.next_stone = original_next_stone

		if score < bestScore:
			return score, list(actionSequence)
		else: 
			return bestScore, bestSequence

	def run_depth2(self, weights):
		self.board = new_board()
		self.score = 0 
		self.lines = 0
		self.level = 0 
		self.gameover = False
		self.paused = False
		
		dont_burn_my_cpu = pygame.time.Clock()
		while 1:
			# THIS IS KEY FOR SPEEDING UP THE TIME STEPS
			pygame.time.set_timer(pygame.USEREVENT+1, 50)
			self.screen.fill((0,0,0))
			if self.gameover:
				self.center_msg("""Game Over!\nYour score: %d
Press space to continue""" % self.score)
				print "SCORE", self.score, "LINES", self.lines
				break
			else:
				if self.paused:
					self.center_msg("Paused")
				else:
					pygame.draw.line(self.screen,
						(255,255,255),
						(self.rlim+1, 0),
						(self.rlim+1, self.height-1))
					self.disp_msg("Next:", (
						self.rlim+cell_size,
						2))
					self.disp_msg("Score: %d\n\nLevel: %d\
\nLines: %d" % (self.score, self.level, self.lines),
						(self.rlim+cell_size, cell_size*5))
					self.draw_matrix(self.bground_grid, (0,0))
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone,
						(self.stone_x, self.stone_y))
					self.draw_matrix(self.next_stone,
						(cols+1,2))
			pygame.display.update()
			

			for event in pygame.event.get():
				'''if event.type == pygame.USEREVENT+1:
					self.drop(False)'''
				range_rotations = 3
				range_left = 5
				range_right = 6
				#range_left = self.stone_x 
				#range_right = len(self.board[0]) - (self.stone_x + len(self.stone[0])) + 1

				# Find best action sequence and its corresponding evaluation functino score
				bestScore = 999999999999999
				bestSequence = [] 
				actionSequence = [] 
				scores = [] 
				'''
				a = time.time()
				for i in range(range_rotations + 1):
					scores.append(self.getScore(weights, actionSequence, bestScore, bestSequence)) 
					for j in range(range_left):
						actionSequence.append("LEFT")
						scores.append(self.getScore(weights, actionSequence, bestScore, bestSequence)) 
					actionSequence = actionSequence[0:len(actionSequence) - range_left]
					for j in range(range_right):
						actionSequence.append("RIGHT")
						scores.append(self.getScore(weights, actionSequence, bestScore, bestSequence))  
					actionSequence = actionSequence[0:len(actionSequence) - range_right]
					actionSequence.append("UP")
				bestSequence.append("RETURN")
				
				scores.sort(reverse=True)
				'''
				cutoff = 0#scores[30]
				b = time.time()
				#print "Time to find cutoff", (b-a)

				bestScore = 999999999999999
				bestSequence = [] 
				actionSequence = [] 

				for i in range(range_rotations + 1):
					bestScore, bestSequence = self.trySequence2(cutoff, weights, 2, actionSequence, bestScore, bestSequence) 
					for j in range(range_left):
						actionSequence.append("LEFT")
						bestScore, bestSequence = self.trySequence2(cutoff, weights, 2, actionSequence, bestScore, bestSequence) 
					actionSequence = actionSequence[0:len(actionSequence) - range_left]
					for j in range(range_right):
						actionSequence.append("RIGHT")
						bestScore, bestSequence = self.trySequence2(cutoff, weights, 2, actionSequence, bestScore, bestSequence) 
					actionSequence = actionSequence[0:len(actionSequence) - range_right]
					actionSequence.append("UP")
				bestSequence.append("RETURN")

				c = time.time()
				#print "Time to figure out best choice", (c-b)
				for move in bestSequence:
					self.key_actions[move]()

				#print self.score

				if event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					'''	
					for key in self.key_actions:
						if event.key == eval("pygame.K_"
						+key):
							self.key_actions[key]()
					'''
			dont_burn_my_cpu.tick(maxfps)
	#def run_depth(depth, ):		

	def run_greedy(self, weights):
		self.board = new_board()
		self.score = 0 
		self.lines = 0
		self.level = 0 
		self.gameover = False
		self.paused = False
		
		dont_burn_my_cpu = pygame.time.Clock()
		while 1:
			# THIS IS KEY FOR SPEEDING UP THE TIME STEPS
			pygame.time.set_timer(pygame.USEREVENT+1, 10)
			self.screen.fill((0,0,0))
			if self.gameover:
				self.center_msg("""Game Over!\nYour score: %d
Press space to continue""" % self.score)
				#print "SCORE", self.score, "LINES", self.lines
				return self.score, self.lines
			else:
				if self.paused:
					self.center_msg("Paused")
				else:
					pygame.draw.line(self.screen,
						(255,255,255),
						(self.rlim+1, 0),
						(self.rlim+1, self.height-1))
					self.disp_msg("Next:", (
						self.rlim+cell_size,
						2))
					self.disp_msg("Score: %d\n\nLevel: %d\
\nLines: %d" % (self.score, self.level, self.lines),
						(self.rlim+cell_size, cell_size*5))
					self.draw_matrix(self.bground_grid, (0,0))
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone,
						(self.stone_x, self.stone_y))
					self.draw_matrix(self.next_stone,
						(cols+1,2))
			pygame.display.update()
			

			for event in pygame.event.get():
				range_rotations = 3
				range_left = 6
				range_right = 6
				#range_left = self.stone_x 
				#range_right = len(self.board[0]) - (self.stone_x + len(self.stone[0])) + 1

				# Find best action sequence and its corresponding evaluation functino score
				bestScore = 999999999999999
				bestSequence = [] 
				actionSequence = [] 

				bestScore, bestSequence = self.trySequence(weights, actionSequence, bestScore, bestSequence) 
				for i in range(range_rotations + 1):
					bestScore, bestSequence = self.trySequence(weights, actionSequence, bestScore, bestSequence) 
					for j in range(range_left):
						actionSequence.append("LEFT")
						bestScore, bestSequence = self.trySequence(weights, actionSequence, bestScore, bestSequence) 
					actionSequence = actionSequence[0:len(actionSequence) - range_left]
					for j in range(range_right):
						actionSequence.append("RIGHT")
						bestScore, bestSequence = self.trySequence(weights, actionSequence, bestScore, bestSequence) 
					actionSequence = actionSequence[0:len(actionSequence) - range_right]
					actionSequence.append("UP")
				bestSequence.append("RETURN")

				print self.score
				for move in bestSequence:
					self.key_actions[move]()

				if event.type == pygame.USEREVENT+1:
					self.drop(False)
				elif event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					for key in self.key_actions:
						if event.key == eval("pygame.K_"
						+key):
							self.key_actions[key]()
	
			dont_burn_my_cpu.tick(10000)
			#dont_burn_my_cpu.tick(maxfps)
	#def run_depth(depth, ):		

	
	def run(self):
		self.gameover = False
		self.paused = False
		
		dont_burn_my_cpu = pygame.time.Clock()
		while 1:
			self.screen.fill((0,0,0))
			if self.gameover:
				self.center_msg("""Game Over!\nYour score: %d
Press space to continue""" % self.score)
			else:
				if self.paused:
					self.center_msg("Paused")
				else:
					pygame.draw.line(self.screen,
						(255,255,255),
						(self.rlim+1, 0),
						(self.rlim+1, self.height-1))
					self.disp_msg("Next:", (
						self.rlim+cell_size,
						2))
					self.disp_msg("Score: %d\n\nLevel: %d\
\nLines: %d" % (self.score, self.level, self.lines),
						(self.rlim+cell_size, cell_size*5))
					self.draw_matrix(self.bground_grid, (0,0))
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone,
						(self.stone_x, self.stone_y))
					self.draw_matrix(self.next_stone,
						(cols+1,2))
			pygame.display.update()
			
			for event in pygame.event.get():
				print "[numBlocks, totalBlockWeight, bumpiness, maxHeight, minHeight, meanHeight, varianceHeight, maxHoleHeight, numHoles, density, numRowsWithHoles, numColsWithHoles]"
				print tetrisai.extractFeatures(self.board, self.stone)
				if event.type == pygame.USEREVENT+1:
					self.drop(False)
				elif event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					for key in self.key_actions:
						if event.key == eval("pygame.K_"
						+key):
							self.key_actions[key]()

			dont_burn_my_cpu.tick(maxfps)


	def run_baseline(self):
		self.gameover = False
		self.paused = False
		
		dont_burn_my_cpu = pygame.time.Clock()
		while 1:
			# THIS IS KEY FOR SPEEDING UP THE TIME STEPS
			pygame.time.set_timer(pygame.USEREVENT+1, 10)
			self.screen.fill((0,0,0))
			if self.gameover:
				self.center_msg("""Game Over!\nYour score: %d
Press space to continue""" % self.score)
				print "SCORE", self.score, "LINES", self.lines
				break
			else:
				if self.paused:
					self.center_msg("Paused")
				else:
					pygame.draw.line(self.screen,
						(255,255,255),
						(self.rlim+1, 0),
						(self.rlim+1, self.height-1))
					self.disp_msg("Next:", (
						self.rlim+cell_size,
						2))
					self.disp_msg("Score: %d\n\nLevel: %d\
\nLines: %d" % (self.score, self.level, self.lines),
						(self.rlim+cell_size, cell_size*5))
					self.draw_matrix(self.bground_grid, (0,0))
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone,
						(self.stone_x, self.stone_y))
					self.draw_matrix(self.next_stone,
						(cols+1,2))
			pygame.display.update()
			
			for event in pygame.event.get():
				moves = baseline.findBestMove(self.board, self.stone, self.stone_x)
				for move in moves:
					self.key_actions[move]() 
				if event.type == pygame.USEREVENT+1:
					self.drop(False)
				elif event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					#print moves
					#print self.board, moves
					for key in self.key_actions:
						if event.key == eval("pygame.K_"
						+key):
							self.key_actions[key]()
			#dont_burn_my_cpu.tick(10000)
			dont_burn_my_cpu.tick(maxfps)

# Run Tetris Normally: You play
def run_normal():
	App = TetrisApp()
	App.run()

# Run Greedy. If weights is [], trains with TD. Otherwises uses weights
# Plays automatically according to greedy. 
def run_greedy(weights, numIters):
	App = TetrisApp()
	if (weights == []):
		weights = App.train_evaluation_function()
	#print "[numBlocks, totalBlockWeight, bumpiness, maxHeight, minHeight, meanHeight, meanHeight**2, varianceHeight, maxHoleHeight, numHoles, density, numRowsWithHoles, numColsWithHoles]"
	#print "FINAL", weights
	score, linesCleared = 0, 0
	for i in range(numIters):
		App = TetrisApp()
		score, linesCleared = App.run_greedy(weights)
		print "SCORE:", score, "LINES CLEARED:", linesCleared
	return score, linesCleared

# Runs Baselines automatically for numIters iterations 
def run_baseline(numIters):
	for i in range(numIters):
		App = TetrisApp()
		App.run_baseline()

if __name__ == '__main__':
	#run_greedy([],10)
	#run_normal()
	#Fire HANDPICKED WEIGHTS
	#App = TetrisApp()
	#genetic_weights = [-0.225308157467, -0.423406394189, 0.129271775997, 0.157856639312, 0,0,0,0.332319029342, 0,0, 0.55599685547,0,0,0]
	genetic_weights_2 = [-0.246348765166 , -0.127112661126, 0.151661645718, 0.155480779546, 0,0,0, 0.27645405375,0,0,0.459974256647,0,0,0]
	#genetic_weights_3 = [-0.35886410085, -0.435430164693, 0.151661645718, 0.155480779546, 0,0,0, 0.381967006347,0,0, 0.158954620221, 0,0,0]
	#weights = [1, 0,1,0.25,0,0,0,3,0,0,3,0,0,0]
	#tdweights = [0.00085946930911114528, 0.071334321710978033, 0.71291427857754686, 0.0017189386348200899, 0.0085945072887023532, 0.0077350379795912061, 0.0082077450672657284, 0.15676812309855659, 0.00012462108839623112, 0.0081647829740243687, 0.010743128961679243, 0.00037347745709833264, 0.0081647829740243687, 0.0042972433127580999]
	run_greedy(genetic_weights_2, 1)
	#App.run_depth2(genetic_weights_2)
	#run_baseline(25)
