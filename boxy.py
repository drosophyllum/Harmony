import esperanza
import random
import timeit
from numpy import *
entities = ["a","b","c","d","e"]
interactions = ["attract","innert"]
types = ["mag","met","plas"]
obs = [["attract", "a" ,"b" ] , ["innert", "a", "c"],["innert" , "b" , "c"],["attract", "a" ,"d"], ["innert" , "b" , "d"],["innert" , "d","c"],["attract","e" ,"a"],["attract","e" ,"b"],["innert","e" ,"c"],["attract","e" ,"d"]]
rules = [["attract","mag","met"],["innert","met","plas"],["innert","mag","plas"], ["innert","met","met"],["attract","mag","mag"]]

correctAssignment = [["a","mag"],["b","met"],["c","plas"],["d","met"],["e","mag"]]
assignment = [(e,random.choice(types)) for e in entities]
p = esperanza.Problem(entities,interactions,obs) 
#print(esperanza.likelihood(obs,rules,types,entities,assignment))
#print(esperanza.likelihood(obs,rules,types,entities,correctAssignment))
#i1 = p.run2((rules,correctAssignment),prand=0.1 ,temperature=3)
#print i1
#exit()
nr = 100
prands = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
data = zeros((len(prands),nr))
for pr in  range(len(prands)):
	prnd = prands[pr]
	runtimes = zeros((nr))
	for i in range(nr):
		print i
		i1 = p.run2((rules,correctAssignment),prand=prnd ,temperature=3)
		runtimes[i] = i1
		data[pr,i] = i1
	print(prnd)
	print("average runtimes:",mean(runtimes))
	print("error bar       :",std(runtimes))
	save("boxy1",data)



#print(runtimes)
