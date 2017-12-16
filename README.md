tetris.py
This contains the infrastructure for the game. In other words, all functionalities including score/ board updates and the GUI are contained here.

Further, ALL the different models are run from this file. Specifically, there are methods to run an ordinary Tetris game (human played), greedy, baseline, and depth 2 search. The training for the all the different models also happens here. 

baseline.py
Baseline model that just seeks to keep pieces as low as possible. No optimization is made to clear lines

tetrisai.py
Extracts the following features for any given game state
[diffHeight, numBlocks, totalBlockWeight, bumpiness, maxHeight, minHeight, meanHeight, meanHeight**2, varianceHeight, maxHoleHeight, numHoles, density, numRowsWithHoles, numColsWithHoles]

genetic.py
Hyperparameters mutation size, population, and mutation rate are set at the top. Then, this runs the genetic algorithm (for a specific number of generational iterations) to determine an evaluation function. The evolution process generates runs games with a greedy search on tetris.py. 
The genes and fitness scores of each chromosome in each generation are printed to stdout. 