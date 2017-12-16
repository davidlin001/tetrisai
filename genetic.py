import random 
import tetris
import copy
populationSize = 50
mutationRate = 0.15
mutationStep = 0.25

def initializePopulation():
	population = [] 
	for i in range(populationSize):
		chromosome = {
			'bumpiness': random.uniform(0,1)-0.5,
			'numHoles': random.uniform(0,1)*0.5,
			'maxHeightSquared': random.uniform(0,1)-0.5,
			'numBlocks': random.uniform(0,1)-0.5,
			'totalBlockWeight': random.uniform(0,1)-0.5,
			'heightRange': random.uniform(0,1)-0.5,
			'fitness': -1
		}
		population.append(chromosome)
	return population

def evaluatePopulation(population):
	for i in range(populationSize):
		cur = population[i]
		weights = [
		cur['heightRange'], 
		cur['numBlocks'], 
		cur['totalBlockWeight'], 
		cur['bumpiness'],
		0,
		0,
		0, 
		cur['maxHeightSquared'],
		0, 
		0, 
		cur['numHoles'],
		0,
		0,
		0
		]
		cur['fitness'] = tetris.run_greedy(weights, 1)[1]

def evolve(population):
	population.sort(key = lambda x: x['fitness'])
	population = population[7*populationSize/10:]
	#print_summary(population)
	children = []#copy.copy(population)
	numParents = len(population) 
	def getRandomChromosome():
		return random.randint(0, numParents-1)

	while (len(children) < populationSize):
		children.append(makeBaby(population[getRandomChromosome()], population[getRandomChromosome()]))

	return children

def makeBaby(mama, pops):
	child = {
		'bumpiness': random.choice([mama['bumpiness'],pops['bumpiness']]),
		'numHoles': random.choice([mama['numHoles'],pops['numHoles']]),
		'maxHeightSquared': random.choice([mama['maxHeightSquared'],pops['maxHeightSquared']]),
		'numBlocks': random.choice([mama['numBlocks'],pops['numBlocks']]),
		'totalBlockWeight': random.choice([mama['totalBlockWeight'],pops['totalBlockWeight']]),
		'heightRange': random.choice([mama['heightRange'],pops['heightRange']]),
		'fitness': -1
	}
	for key in child: 
		if key != 'fitness' and random.uniform(0,1) < mutationRate:
			child[key] += random.uniform(0,1)*mutationStep*2 - mutationStep

	return child

def run_genetic_algorithm(numGenerations):
	population = initializePopulation()
	evaluatePopulation(population)
	for i in range(numGenerations):
		print "GENERATION ", i
		print_summary(population)
		population = evolve(population)
		evaluatePopulation(population)
	print "GENERATION", numGenerations
	print_summary(population)

def print_summary(population):
	print "#", "bumpiness", "numHoles", "Height^2", "numBlocks", "totalBlockWeight", "heightRange", "fitness"
	average = 0
	bestIndex = 0 
	bestScore = 0 
	for i in range(len(population)):
		cur = population[i]
		print i, cur['bumpiness'], cur["numHoles"], cur["maxHeightSquared"], cur["numBlocks"], cur["totalBlockWeight"], cur["heightRange"], cur["fitness"]
		average += cur['fitness']
		if cur['fitness'] > bestScore:
			bestIndex = i 
			bestScore = cur['fitness']
	average = 1.0*average/len(population)
	print "Average Lines Cleared: ", average
	print "Best Chromosome:", bestIndex, "Lines Cleared:", bestScore

if __name__ == '__main__':
	run_genetic_algorithm(10)

