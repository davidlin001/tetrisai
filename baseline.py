"""
Baseline Model:
Places blocks as low as possible on the board as specified
by the score() function. Considers translations and rotations. 

"""

def check_collision(board, shape, offset):
	""" Checks for collision. Copied from tetris.py """
	off_x, off_y = offset
	for cy, row in enumerate(shape):
		for cx, cell in enumerate(row):
			try:
				if cell and board[ cy + off_y ][ cx + off_x ]:
					return True
			except IndexError:
				return True
	return False

def rotate_clockwise(shape):
	""" Rotates shape """
	return [ [ shape[y][x]
			for y in xrange(len(shape)) ]
		for x in xrange(len(shape[0]) - 1, -1, -1) ]

def score(piece, lowest_row):
	""" 
	Provides a weight for putting a piece onto a particular row.
	Higher the weight the better. We use this to incentive our baseline
	to put blocks as low as possible.

	"""
	result = 0
	rowWeight = lowest_row - len(piece)
	for y in range(len(piece)):
		rowWeight += 1
		for x in range(len(piece[0])):
			result += piece[y][x]*rowWeight
	return result 

def findBestMove(board, piece, orig_x):
	"""
	@param board, piece from tetris
	@param orig_x: x-coor of original piece
	@return: Sequence of optimal moves 
	"""
	b_width = len(board[0])
	b_height = len(board)

	best_x = 0 
	best_num_rotations = 0 
	best_weight = 0 

	# Try all four rotations
	for i in range(4):
		if i > 0:
			piece = rotate_clockwise(piece)
		p_width = len(piece[0])
		p_height = len(piece)
		# Try every column 
		for j in range(b_width - p_width + 1):
			#KEY NOTE: COLUMN AND THEN ROW
			cur_offset = (j,0)
			while not check_collision(board, piece, cur_offset):
				cur_offset = (cur_offset[0], cur_offset[1]+1)
			lowest_row = cur_offset[1] + p_height - 2
			if cur_offset[1] != 0 and score(piece, lowest_row) > best_weight:
				best_weight = score(piece, lowest_row)
				best_x = j
				best_num_rotations = i%4
	moves = [] 
	d_x = best_x - orig_x
	if best_num_rotations > 0:
		moves = ['UP']*best_num_rotations
	if d_x > 0:
		moves.extend(['RIGHT']*d_x)
	if d_x < 0:
		d_x *= -1
		moves.extend(['LEFT']*d_x)
	moves.append('RETURN')
	return moves

			