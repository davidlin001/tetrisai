import pygame, sys
import tetris
import numpy as np

def extractFeatures(board):

	numBlocks = 0 
	b_width = len(board[0])
	b_height = len(board)

	numHolesByRow = [0]*b_height
	numHolesByCol = [0]*b_width
	numHoles = 0 
	heights = [] 
	for col in range(b_width):
		found_top = False
		for row in range(b_height):
			if board[row][col] != 0:
				numBlocks += 1
			if not found_top and board[row][col] != 0:
				found_top = True
				heights.append(b_height - row)
			if found_top and board[row][col] == 0:
				numHoles += 1


	maxHeight = max(heights)
	minHeight = min(heights)
	meanHeight = np.average(heights)
	varianceHeight = np.var(heights)
	density = (numBlocks - numHoles)*1.0/numBlocks




	features = [maxHeight, minHeight, meanHeight, varianceHeight]
	return features