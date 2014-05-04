import random
import numpy 

def newRandomRow(interactions,typespace):
	rule = ["","",""]
	rule[0] = random.choice(interactions)
	rule[1] = random.choice(typespace)
	rule[2] = random.choice(typespace)
	return rule


def regrowRule(interactions, types,rules):
	if rules :
		typespace = [] 
		for rule in rules:
			typespace.append(rule[1])
			typespace.append(rule[2])
		typespace = set(typespace)
		nextType = list(set(types).difference(typespace))
		typespace = list(typespace) + ( [] if len(nextType)==0 else [nextType[0]])

		action = random.choice(["c","i","bc" ,"b1","b2","h"])
		index = random.choice(range(len(rules)))
	else:
		typespace = types
		action = "c"
		index = 0
	if   action == "c":
		random.shuffle(rules)
		rules = rules[0:index]
		numberNewRows = numpy.random.geometric(0.5) 
		rules = rules + [newRandomRow(interactions,typespace) for x in range(numberNewRows)]

	elif action == "i":
		rules[index] = newRandomRow(interactions,typespace); 
	elif action == "bc":
		rules[index][1] = random.choice(typespace)
		rules[index][2] = random.choice(typespace)
	elif action == "b1":
		rules[index][1] = random.choice(typespace)
	elif action == "b2":
		rules[index][2] = random.choice(typespace)
	elif action == "h":
		rules[index][0] = random.choice(interactions)
	return rules

#regrowRule(rules)
def listify(x):
	if type(x) == type(dict()):
		return [[z,x[z]] for z in x.keys()]
	return x

def gibbsv1(obs,rules, types, entities):
	x = []
	prods = [[e,t] for t in types for e in entities]
	random.shuffle(prods)
	for newAssignment in prods:
		x1 = listify(x)
		if newAssignment in x1:  x1.remove(newAssignment)
		print(newAssignment)
		print x1
		x1 = dict(x1)
		print(x1)
		x2 = dict(listify(x) + [newAssignment])
		print x2
		a1 = likelihood(obs,rules,types, entities,x1)
		a2 = likelihood(obs,rules,types, entities,x2)
		x = x1 if random.random() > float(a1)/float(a2) else x2
	return x

def gibbsv2(obs,rules, types, entities , oldAssignment, numtime = 1):
	x = dict(oldAssignment)
	entities = list(entities)
	trail = []
	trailLikelihoods = []
	mx = x
	mxa = 0
	for i in range(numtime):
		random.shuffle(entities)
		for entity in entities:
			proposals = []
			probs = []
			for typ in types:
				x2 = dict(x)
				x2[entity] = typ
				a2 = likelihood(obs,rules,types, entities,x2)
				proposals.append(x2)
				probs.append(a2) 
				if a2>mxa:
					mx = x2
					mxa = a2
			z = float(sum(probs))
			probs = [prob/z for prob in probs] 
			index = numpy.random.choice(range(len(proposals)),p=probs)
			x = proposals[index]
		#trail.append(x)
		#trailLikelihoods.append(likelihood(obs,rules,types, entities,x))
	
	#return trail[trailLikelihoods.index(max(trailLikelihoods))]
	return mx


def prior(rules):
	tipos = []
	for r in rules:
		tipos.append(r[1])
		tipos.append(r[2])
	tipos = list(set(tipos))
	return (0.5**(len(rules)))*(1.0/((float(len(tipos)))**(2*len(rules))))

def likelihood(obs,rules,types,entities, assignment ):
	b = 4
	interactions = []
	correct = 0
	assignment = dict(assignment)
	for e1 in entities:
		for e2 in entities:
			if e1 < e2 and e1 in assignment.keys()  and e2 in assignment.keys():
				pred = prediction(rules,assignment,e1,e2)
				#print (pred,e1,e2)
				if len(pred) == 1 and ( [pred[0],e1,e2] in obs or [pred[0],e2,e1] in obs) :
					correct =  correct +1			
	qt = float(len(obs) - correct)
	#print fracwrong
	return numpy.exp(-1*b*qt)


def prediction(rules,typedict,e1,e2):
	typedict = dict(typedict)
	t1 = typedict[e1]
	t2 = typedict[e2]
	pred=[]
	for r in rules:
		if t1 and t2 and r[1:] == [t1,t2] or r[1:] == [t2,t1]:
			pred.append(r[0])
	pred = list(set(pred))
	return pred







entities = ["a","b","c","d"]
interactions = ["attract","innert"]
types = ["mag","met","plas"]
obs = [["attract", "a" ,"b" ] , ["innert", "a", "c"],["innert" , "b" , "c"],["attract", "a" ,"d"], ["innert" , "b" , "d"],["innert" , "d","c"]] 


rules = [["attract","mag","met"],["innert","met","plas"],["innert","mag","plas"], ["innert","met","met"]]
#print(rules)
#print(obs)

#assignment = [(e,random.choice(types)) for e in entities] 
assignment =  [["a" , "plas"],["b","plas"],["c" ,"plas"],["d","plas"]] 
#print(assignment)
#print(likelihood(obs,rules,types,entities,assignment))

assignment =  [["a" , "mag"],["b","met"],["c" ,"plas"],["d","met"]] 
#print(assignment)
#print(likelihood(obs,rules,types,entities,assignment))

def detox(rules,assignments):
	typespace = list(set([t for (o,t) in listify(assignments)]))
	relevant = filter(lambda r: r[1] in typespace and r[2] in typespace, rules)
	indices = range(len(relevant))
	contradict= lambda r1,r2 : (r1[1],r1[2]) in [(r2[1],r2[2]),(r2[2],r2[1])]
	i = 0
	while( i < len(relevant)-1):
		r = relevant[i]
		relevant = relevant[0:i+1] + filter(lambda rn : not contradict(r,rn),relevant[i+1:])
		i=i+1
	return relevant
def clean(rules,assignments):
	random.shuffle(rules)
	return detox(rules,assignments)



rules = [["attract","mag","met"],["innert","met","plas"],["innert","mag","plas"], ["innert","met","met"]]
assignment = [(e,random.choice(types)) for e in entities] 
def randomAssignments(entities,types,rules):
	typespace = set(typespace)
	nextType = list(set(types).difference(typespace))
	typespace = list(typespace) + ( [] if len(nextType)==0 else [nextType[0]])
	assignment = [(e,random.choice(typespace)) for e in entities] 
	return assignment

def rand(interactions,entities,types,rules,assignments):
	newRules = regrowRule(interactions, types,rules)
	assignments = randomAssignments(entities,types,rules)
	return (newRules,assignments)

def erd(prand,interactions,entities,types,error,rules,assignment):
	assignment = dict(assignment)
	def errordriven():
		skip = 0.2
		(ei ,ee1 ,ee2) = error
		random.shuffle(rules)
		fixes = filter(lambda r : ei == r[0] , rules)
		if fixes and random.random() > skip:
			(fi,ft1,ft2) = fixes[0]
			assignment[ee1] = ft1
			assignment[ee2] = ft2
			return (rules,assignment)
		newRule = [ei,"",""]
		n = numpy.random.geometric(0.5) -1 
		if n == 0:
			newRule[1] = assignment[ee1]
			newRule[2] = assignment[ee2]
			return (detox([newRule] + rules,assignment), assignment)
		typespace = [] 
		for rule in rules:
			typespace.append(rule[1])
			typespace.append(rule[2])
		typespace = set(typespace)
		nextType = list(set(types).difference(typespace))
		typespace = list(typespace) + ( [] if len(nextType)==0 else [nextType[0]])
		if n == 1:
			if random.random() > 0.5: 
				newRule[1] = random.choice(typespace)
				newRule[2] = assignment[ee2]
			else:   
				newRule[1] = assignment[ee1]
				newRule[2] = random.choice(typespace)
			return (detox([newRule] + rules,assignment), assignment)
		newRule[1] = random.choice(typespace)
		newRule[2] = random.choice(typespace)
		return (detox([newRule] + rules,assignment) , assignment)	
	if prand< random.random():
		return errordriven()
	else:
		return rand(interactions,entities,types,rules,assignments)
		



x = regrowRule(interactions, types,[])
assignment = [(e,random.choice(types)) for e in entities] 
#print(sum([1 if {'a': 'mag', 'c': 'plas', 'b': 'met', 'd': 'met'} == gibbsv2(obs,rules,types, entities,assignment,100) else 0 for x in range(100)]))
a  = prior(x)*likelihood(obs,x,types,entities,assignment)
i=0 



def getError(obs,x,assignment):
	random.shuffle(obs)
	for ob in obs:
		(oi,oe1,oe2) = ob
		pred = prediction(x,assignment,oe1,oe2)
		if (not pred) or pred[0][0] != oi:
			return ob
	print("FATAL ERROR: no erroneous observations left")
	exit()


while(likelihood(obs,x,types,entities,assignment) < 1):
	prand = 0
	error = getError(obs,x,assignment)
	i = i +1 
	(xp,assignmentp) = erd(prand,interactions,entities,types,error,rules,assignment)
	ap = prior(xp)*likelihood(obs,xp,types,entities,assignmentp)
	if random.random() < ap/a :
		x = xp
		assignment = assignmentp
		a = ap
print i
exit();
x = regrowRule(interactions, types,[])
assignment = [(e,random.choice(types)) for e in entities] 
#print(sum([1 if {'a': 'mag', 'c': 'plas', 'b': 'met', 'd': 'met'} == gibbsv2(obs,rules,types, entities,assignment,100) else 0 for x in range(100)]))
a  = prior(x)*likelihood(obs,x,types,entities,assignment)
i=0 
while(likelihood(obs,x,types,entities,assignment) < 1):
	i = i +1 
	xp = regrowRule(interactions, types,x)
	assignmentp= gibbsv2(obs,xp,types, entities,assignment,50)
	ap = prior(xp)*likelihood(obs,xp,types,entities,assignmentp)
	if random.random() < ap/a :
		x = xp
		assignment = assignmentp
		a = ap

print "\n\n\nACCEPT!\n"
print obs
print "\n"
print x
print assignment
print a
print i
	



