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
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		lambda:self.drop(True),
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'SPACE':	self.start_game,
			'RETURN':	self.insta_drop
		}
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

			moves = baseline.findBestMove(self.board, self.stone, self.stone_x)
			for move in moves:
				key_actions[move]()
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
			reward = new_score - prev_score	

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
		weights = [0]*12
		numGames = 10
		for i in range(numGames):
			print "GAME", i
			weights = self.td_learning(weights)	
		
		#weights = td_learning(self, weights)
		return weights

	def test_evaluation_function(self, weights, features):
		return sum([weights[i]*features[i] for i in range(len(weights))])	

	# For every possible action sequence, we try the action and retrieve the score 
	# of its successor
	def trySequence(self, actionSequence, bestScore, bestSequence):
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		lambda:self.drop(True),
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'SPACE':	self.start_game,
			'RETURN':	self.insta_drop
		}
		original_score = 100 
		#Maybe need to copy
		original_board = copy.deepcopy(self.board)
		original_stone = self.stone

		#print "original"
		#print original_board

		for move in actionSequence:
			key_actions[move]()
		key_actions["RETURN"]()

		features = tetrisai.extractFeatures(self.board, self.next_stone)
		score = self.test_evaluation_function(weights, features)
		
		print "attempted: sequence", actionSequence, "score", score
		# After trying the move, we have to revert everything
		self.score = original_score
		self.board = original_board
		self.stone = original_stone
		#print "new board"
		#print self.board
		if score < bestScore:
			return score, actionSequence
		else: 
			return bestScore, bestSequence

	def run_greedy(self, weights):
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		lambda:self.drop(True),
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'SPACE':	self.start_game,
			'RETURN':	self.insta_drop
		}
		self.board = new_board()
		self.score = 0 
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
			
			# Recursive backtracking every possible action sequence
			# Given action sequence, execute, revert, record evaluation score

			for event in pygame.event.get():
				#if event.type == pygame.USEREVENT+1:
				#	self.drop(False)
				#elif event.type == pygame.QUIT:
				#	self.quit()
				if event.type == pygame.KEYDOWN:
					print "Current board"
					print self.board
					# Number of possible rotations, and translations
					range_rotations = 3
					range_left = self.stone_x 
					range_right = len(self.board[0]) - (self.stone_x + len(self.stone[0]))

					# Find best action sequence and its corresponding evaluation functino score
					bestScore = 999999999999999
					bestSequence = [] 
					actionSequence = [] 

					bestScore, bestSequence = self.trySequence(actionSequence, bestScore, bestSequence) 
					for i in range(range_left):
						actionSequence.append("LEFT")
						bestScore, bestSequence = self.trySequence(actionSequence, bestScore, bestSequence) 
						for j in range(range_rotations):
							actionSequence.append("UP")
							bestScore, bestSequence = self.trySequence(actionSequence, bestScore, bestSequence) 
						actionSequence = actionSequence[0:len(actionSequence) - range_rotations]
					actionSequence = [] 
					for i in range(range_right):
						actionSequence.append("RIGHT")
						bestScore, bestSequence = self.trySequence(actionSequence, bestScore, bestSequence) 
						for j in range(range_rotations):
							actionSequence.append("UP")
							bestScore, bestSequence = self.trySequence(actionSequence, bestScore, bestSequence) 
						actionSequence = actionSequence[0:len(actionSequence) - range_rotations]

					bestSequence.append("RETURN")
					for move in bestSequence:
						key_actions[move]()
					print "Executed: ", bestSequence, self.score
					#print moves
					#print self.board, moves
					for key in key_actions:
						if event.key == eval("pygame.K_"
						+key):
							key_actions[key]()
			dont_burn_my_cpu.tick(10000)
			
			#dont_burn_my_cpu.tick(maxfps)
	#def run_depth(depth, ):		

	
	def run(self):
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		lambda:self.drop(True),
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'SPACE':	self.start_game,
			'RETURN':	self.insta_drop
		}
		
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
					for key in key_actions:
						if event.key == eval("pygame.K_"
						+key):
							key_actions[key]()

			dont_burn_my_cpu.tick(maxfps)


	def run_baseline(self):
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		lambda:self.drop(True),
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'SPACE':	self.start_game,
			'RETURN':	self.insta_drop
		}
		
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
					key_actions[move]()
				
				if event.type == pygame.USEREVENT+1:
					self.drop(False)
				elif event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					#print moves
					#print self.board, moves
					for key in key_actions:
						if event.key == eval("pygame.K_"
						+key):
							key_actions[key]()
			#dont_burn_my_cpu.tick(10000)
			dont_burn_my_cpu.tick(maxfps)

if __name__ == '__main__':
	# Run Normally
	App = TetrisApp()
	
	weights = App.train_evaluation_function()

	total = sum(weights)
	
	weights = [weight*1.0/total for weight in weights]
	print "[numBlocks, totalBlockWeight, bumpiness, maxHeight, minHeight, meanHeight, varianceHeight, maxHoleHeight, numHoles, density, numRowsWithHoles, numColsWithHoles]"
	print "FINAL", weights
	App.run_greedy(weights)
	
	#App.run()


	# Run Baseline for a certain number of trials
	#for i in range(250):
	#	App = TetrisApp()
	#	App.run_baseline()
	
