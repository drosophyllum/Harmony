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
		numberNewRows = numpy.random.geometric(0.1) 
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
#		print(newAssignment)
#		print x1
		x1 = dict(x1)
#		print(x1)
		x2 = dict(listify(x) + [newAssignment])
#		print x2
		a1 = likelihood(obs,rules,types, entities,x1)
		a2 = likelihood(obs,rules,types, entities,x2)
		x = x1 if random.random() > float(a1)/float(a2) else x2
	return x

def gibbsv2(obs,rules, types, entities , oldAssignment, numtime = 1):
	#print(obs)
	#print(rules,oldAssignment)
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
	#print(rules,mx)
	#print mxa
	return mx


def prior(rules):
	tipos = []
	for r in rules:
		tipos.append(r[1])
		tipos.append(r[2])
	tipos = list(set(tipos))
	return (0.5**(len(rules)))*((1.0/float(len(tipos)+1))**(2*len(rules)))

def likelihood(obs,rules,types,entities, assignment ):
	b = 30
	interactions = []
	mistakes = 0
	assignment = dict(assignment)
	for e1 in entities:
		for e2 in entities:
			if not (e1 == e2):
				if e1 in assignment.keys()  and e2 in assignment.keys():
					pred = prediction(rules,assignment,e1,e2)
					if not (len(pred) == 1 and ( [pred[0],e1,e2] in obs or [pred[0],e2,e1] in obs) ):
						mistakes  = mistakes + 1
				else: 
					mistakes  = mistakes + 1
	return numpy.exp(-1*b*mistakes)


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







def detox(rules,assignments):
	#print("detox")
	typespace = list(set([t for (o,t) in listify(assignments)]))
	relevant = filter(lambda r: r[1] in typespace and r[2] in typespace, rules)
	indices = range(len(relevant))
	contradict= lambda r1,r2 : (r1[1],r1[2]) in [(r2[1],r2[2]),(r2[2],r2[1])]
	i = 0
	while( i < len(relevant)):
		r = relevant[i]
		relevant = relevant[0:i+1] + filter(lambda rn : not contradict(r,rn),relevant[i+1:])
		i=i+1
	applyable = list(relevant)
	for r in applyable:
		v = list(dict(assignments).values())
		try:
			v.remove(r[1])
			v.remove(r[2])
		except ValueError:
			relevant.remove(r)
	assert len(relevant) <= 1 or not  any([ contradict(r1,r2) for r1 in relevant for r2 in relevant if r1 != r2])
	return relevant

def clean(rules,assignments):
	random.shuffle(rules)
	return detox(rules,assignments)



def randomAssignments(entities,types,rules):
	typespace = set(types)
	nextType = list(set(types).difference(typespace))
	typespace = list(typespace) + ( [] if len(nextType)==0 else [nextType[0]])
	assignment = [(e,random.choice(typespace)) for e in entities] 
	return assignment

def rand(interactions,entities,types,rules,assignments):
	newRules = regrowRule(interactions, types,rules)
	assignments = randomAssignments(entities,types,rules)
	return (newRules,assignments)

def erd(prand,interactions,entities,types,error,rules,assignment,obs):
	assignment = dict(assignment)
	def errordriven2():
		skip = 0.5
                (ei ,ee1 ,ee2) = error
                random.shuffle(rules)
                fixes = filter(lambda r : ei == r[0] , rules)
                if fixes and random.random() > skip:
                        (fi,ft1,ft2) = fixes[0]
                        assignment[ee1] = ft1
                        assignment[ee2] = ft2
                        return (rules,assignment)
                newRule = [ei,"",""]
                n = numpy.random.geometric(0.1) 
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
				assignment[ee1] = newRule[1]
                                newRule[2] = assignment[ee2]
                        else:
                                newRule[1] = assignment[ee1]
                                newRule[2] = random.choice(typespace)
				assignment[ee2] = newRule[2]
                        return (detox([newRule] + rules,assignment), assignment)
                newRule[1] = random.choice(typespace)
		assignment[ee1] = newRule[1]
                typespace = []
                typespace.append(newRule[1])
                for rule in rules:
                        typespace.append(rule[1])
                        typespace.append(rule[2])
                nextType = list(set(types).difference(typespace))
                typespace = list(typespace) + ( [] if len(nextType)==0 else [nextType[0]])
                
		newRule[2] = random.choice(typespace)
		assignment[ee2] = newRule[2]
                return (detox([newRule] + rules,assignment) , assignment)
        

	def errordriven():
		skip = 0.8
                (ei ,ee1 ,ee2) = error
                random.shuffle(rules)
                fixes = filter(lambda r : ei == r[0] , rules)
                #if fixes and random.random() > skip:
                #        (fi,ft1,ft2) = fixes[0]
                #        assignment[ee1] = ft1
                #        assignment[ee2] = ft2
	#		assert prediction(detox(rules,assignment),assignment,error[1],error[2]) == [error[0]]
        #                return (rules,assignment)
		n = min(numpy.random.geometric(0.1),2)
		q = [ee1,ee2]
		random.shuffle(q)
		toReassign = q[0:n]
		typespace = [] 
		for rule in rules:
			typespace.append(rule[1])
			typespace.append(rule[2])
		typespace = set(typespace)
		nextType = list(set(types).difference(typespace))
		typespace = list(typespace) + ( [] if len(nextType)==0 else nextType[0:min(2,len(nextType))])
		#print typespace
		for e in toReassign:
			assignment[e] = random.choice(typespace)

		newRules = [[ei,assignment[ee1],assignment[ee2]]]
		for ob in obs:
			if ob != error and ob[1] in toReassign or ob[2] in toReassign:
				newRules.append([ob[0],assignment[ob[1]],assignment[ob[2]]])
		
		assert prediction(detox(newRules + rules,assignment),assignment,error[1],error[2]) == [error[0]]
		return (detox(newRules + rules,assignment), assignment)
	if error and prand< random.random():
		(outr,outa)=  errordriven()
		outr= detox(outr,outa)
#		print
#		print (outr,outa)
#		print(prediction(outr,outa,error[1],error[2]))
#		print
#		print error
		assert prediction(outr,outa,error[1],error[2]) == [error[0]]
		return [outr,outa]
	else:
		return rand(interactions,entities,types,rules,assignment)
		
def getError(obs,x,assignment):
	random.shuffle(obs)
	for ob in obs:
		(oi,oe1,oe2) = ob
		pred = prediction(x,assignment,oe1,oe2)
		if (not pred) or pred[0] != oi:
			return ob
	#print("FATAL ERROR: no erroneous observations left")
	#exit()

class Problem:
	def __init__(self,entities,interactions,obs):
		self.entities = entities
		self.interactions = interactions
		self.obs = obs
		self.types = ["t" + str(i) for i in range(len(entities))]
	def run(self,prand,neval=None):
		if neval == None:
			neval = len(self.obs)
		x = regrowRule(self.interactions, self.types,[])
		assignment = [(e,random.choice(self.types)) for e in self.entities] 
		a  = prior(x)*likelihood(self.obs,x,self.types,self.entities,assignment)
		i=0 



		while(likelihood(self.obs,x,self.types,self.entities,assignment) < 1):
			error = getError(self.obs,x,assignment)
			i = i +1 
			(xp,assignmentp) = erd(prand,self.interactions,self.entities,self.types,error,x,assignment,self.obs)
			xp = clean(xp,assignmentp)
			random.shuffle(self.obs)
			ap = prior(xp)*likelihood([error]+self.obs[0:neval-1],xp,self.types,self.entities,assignmentp)
			print x, assignment
			print error
			print xp,assignmentp
			print

			if True : #random.random() < ap/a :
				x = xp
				assignment = assignmentp
				a = ap
		print i
	def run2(self,correct, neval=None,prand=None ,temperature=1):
		print(prand)
		if neval == None:
			neval = len(self.obs)
		x = regrowRule(self.interactions, self.types,[])
		assignment = [(e,random.choice(self.types)) for e in self.entities] 
		a  = prior(x)*likelihood(self.obs,x,self.types,self.entities,assignment)
		i=0 
		ac = likelihood(self.obs,correct[0],self.types,self.entities,correct[1])*prior(correct[0])
		xp = None
		assignmentp = None
		while(likelihood(self.obs,x,self.types,self.entities,assignment) < 1 or len(x) > len(correct[0])):
			i = i +1 
#			print i
			if prand == None: 
				xp = regrowRule(self.interactions, self.types,x)
				assignmentp= gibbsv2(self.obs,xp,self.types, self.entities,assignment,50)
				xp = clean(xp,assignmentp)
			else :	
				error = getError(self.obs,x,assignment)
				(xp,assignmentp) = erd(prand,self.interactions,self.entities,self.types,error,x,assignment,self.obs)	
				xp = clean(xp,assignmentp)
				
			random.shuffle(self.obs)
			ap = prior(xp)*likelihood(self.obs[0:neval],xp,self.types,self.entities,assignmentp)
			if random.random() < (ap/a)**(float(1)/float(temperature)) :
				#print(x,assignment)
				#print("accept!: " , (a,ap,ac))
				#print(xp,assignmentp)
				#print
				x = xp
				assignment = assignmentp
				a = ap
		return i 
#		print "\n\n\nACCEPT!\n"
#		print self.obs
#		print "\n"
#		print x
#		print assignment
#		print a
#		print i
			



