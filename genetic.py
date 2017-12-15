import random 

populationSize = 50

def initializePopulation():
	population = [] 
	for i in range(populationSize):
		chromosome = {
			bumpiness: random.uniform(0,1)-0.5
			numHoles: random.uniform(0,1)*0.5
			maxHeightSquared: random.uniform(0,1)-0.5
			numBlocks: random.uniform(0,1)-0.5
			totalBlockWeight: random.uniform(0,1)-0.5
			heightRange: random.uniform(0,1)-0.5
			fitness: -1
		}
		population.append(chromosome)
	return population

def evaluatePopulation(population):
	for i in range(populationSize):
		curChromosome = population[i]
		# Bumpiness, NumHoles, MaxHeight**2 (Consider 1.5), numBlocks, TotalBlockWeight, Range of Heights


		# Play game with this 



def evolve(population):
	# Sort by fitness

def makeBaby(mama, pops):
