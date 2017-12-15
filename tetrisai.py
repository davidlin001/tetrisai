import pygame, sys
import tetris
import numpy as np

def extractFeatures(board, piece):

	numBlocks = 0
	b_width = len(board[0])
	b_height = len(board)
	totalBlockWeight = 0 

	numHolesByRow = [0]*b_height
	numHolesByCol = [0]*b_width
	numHoles = 0 
	heights = [] 
	for col in range(b_width):
		found_top = False
		for row in range(b_height - 1):
			if board[row][col] != 0:
				numBlocks += 1
				totalBlockWeight += (b_height - row - 1)
			if not found_top and board[row][col] != 0:
				found_top = True
				heights.append(b_height - row - 1)
			if found_top and board[row][col] == 0:
				numHoles += 1
				numHolesByRow[row] += 1
				numHolesByCol[col] += 1
			if row == b_height - 2 and board[row][col] == 0 and not found_top:
				heights.append(0)
	bumpiness = 0
	maxHoleHeight = 0 
	for i in range(len(heights)):
		if i > 0:
			bumpiness += abs(heights[i]- heights[i-1])
	for i in range(len(numHolesByRow)):
		if numHolesByRow[i] > 0: 
			maxHoleHeight = b_height - i - 1
			break

	maxHeight = max(heights)
	minHeight = min(heights)
	meanHeight = np.average(heights)
	varianceHeight = np.var(heights)
	density = (numBlocks)*1.0/(numBlocks + numHoles+ 0.0001)
	numRowsWithHoles = sum(i > 0 for i in numHolesByRow)
	numColsWithHoles = sum(i > 0 for i in numHolesByCol)
	diffHeight = maxHeight - minHeight

	features = [diffHeight, numBlocks, totalBlockWeight, bumpiness, maxHeight, minHeight, meanHeight, meanHeight**2, varianceHeight, maxHoleHeight, numHoles, density, numRowsWithHoles, numColsWithHoles]
	#features = [totalBlockWeight, numHoles, meanHeight, bumpiness, numBlocks]
	#features = [numBlocks, totalBlockWeight, bumpiness, maxHeight, meanHeight, meanHeight**2, maxHoleHeight, numHoles, numRowsWithHoles, numColsWithHoles]
	
	return features