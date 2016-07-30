import random, sys
from avl import AVLTree

rvals = list({random.randint(0, sys.maxsize) for x in range(5000)})
tree = AVLTree()

for val in rvals:
	tree.insert(val)
