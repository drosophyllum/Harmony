from numpy import *
import scipy.sparse
from multiprocessing import Pool
import random

entities  = array(["a" , "b" ,"c"])
nument    = entities.shape[0]
interactions = array(["attract" , "repelled", "innert"])
numint    = interactions.shape[0]
types = array(["t1","t2","t3"])
numtyp    = types.shape[0]
numpairs  = nument**2
sub2ind = lambda x,y: ravel_multi_index(y, dims=x )

print("making templates")
vartt = ["X","Y","Z"] 
variables = [("X","Y","X","Y")] 

tmprelations = [(r1,r2) for r1 in types for r2 in types if r1 < r2]
tmprelations += [(r1,r1) for r1 in types]

templates = [(rh,vh1,vh2,r[0],vb1,r[1],vb2) for rh in interactions for r in tmprelations for (vh1,vh2,vb1,vb2) in variables]

numrules = len(templates)
print("alocating matrices ")
T = scipy.sparse.lil_matrix((numrules,numint*numpairs*numtyp*nument*numtyp*nument))
w  = scipy.sparse.lil_matrix((1,numrules))
Tsize = [nument,nument,numint,nument,nument,numtyp,numtyp]

def unifies(hi,hj,i,ii,vh1,vh2,vb1,vb2):
        rle = [hi,hj,i,ii]
        gle = [vh1,vh2,vb1,vb2]
        return [x==y for x in rle for y in rle] == [x==y for x in gle for y in gle] 

def paratemp( tempth):
    (relh,vh1,vh2,relb1,vb1,relb2,vb2) = templates[tempth]
    rh = where(interactions== relh)[0]
    rb1 = where(types== relb1)[0]
    rb2 = where(types== relb2)[0]
    for hi in range(nument):
	for hj in range(nument):
	    for i in range(nument):
		for ii in range(nument):
		       if unifies(hi,hj,i,ii,vh1,vh2,vb1,vb2):
				T[tempth,sub2ind(Tsize,(hi,hj,rh,i,ii,rb1,rb2))] = 1

map(paratemp,range(numrules))
R = T
print("loaded hope matrix with size:")
print(R.shape)

def registerT(A,rel, entity1):
	i1 = where(entities == entity1)[0]
	i3 = where (types== rel)[0]
	A[i1,i3] = 1


def registerI(A,rel, entity1, entity2):
	i1 = where(entities == entity1)[0]
	i2 = where(entities == entity2)[0]
	i3 = where(interactions == rel)[0]
	A[i1,i2,i3] = 1

def regrule(w,relh, vh1, vh2, relb1, vb1, relb2, vb2):
	for tempth in range(numrules) :
       		(trelh,tvh1,tvh2,trelb1,tvb1,trelb2,tvb2) = templates[tempth]
		if (trelh == relh) and (trelb1 == relb1) and (trelb2 == relb2) and unifies(tvh1,tvh2,tvb1,tvb2,vh1,vh2,vb1,vb2):
           		w[tempth] = 1
           		break

#########################################
# PURRTY PRINT
##############################
#
def printInt(At) :
	for r in range(0,numint):
	    for i in range(0,nument):
	    	for j in range(0,nument):
			if At[i,j,r] > 0 :
		     		rrr =  interactions[r]
			    	eee1 = entities[i]
			  	eee2 = entities[j]
				print(  rrr+ "("+eee1+")." if eee1 == eee2 else rrr+"(" +eee1+","+eee2+")." )
	
#
def printTyp(At) :
	for r in range(0,numtyp):
	    for i in range(0,nument):
			if At[i,r] > 0 :
		     		rrr =  types[r]
			    	eee1 = entities[i]
				print(  rrr+ "("+eee1+")." )


def printThe(w) :
	print(array(templates)[nonzero(w)])
#
##########


observations = 		[("attract" , "a" , "b"),
		  	("innert"  , "a" , "c"),
			("innert"  , "b" , "c")]

I = zeros((nument,nument,numint))
registerI(I,"attract","a","b")
registerI(I,"innert","a","c")
registerI(I,"innert","b","c")


T = zeros((nument,numtyp))
registerT(T,"t1","a")
registerT(T,"t2","b")
registerT(T,"t3","c")


w  = zeros((numrules))


regrule(w,"attract" , "X", "Y" , "t1" , "X", "t2", "Y")


def getForward(w):
	Fp = scipy.sparse.lil_matrix(w.reshape((1,numrules))).dot(R)
	F = asarray(Fp.todense())
	F = F.reshape((numint*numpairs,numtyp*nument*numtyp*nument))
	return F

def runTheory(T,w): #,I):
	print("\n\nObservations:")
#	printInt(I)
	print("\nTheory:")
	printThe(w)
	print("\nType System:")
	printTyp(T)
	F = getForward(w)
	Ip = F.dot(kron(T.reshape(nument,numtyp),T.reshape(nument,numtyp)).flatten()).reshape((nument,nument,numint))
	print("\n\nResult:")
	printInt(Ip)
	print("\n\n")
	return Ip
runTheory(T,w)

def getObs(observations):
	return observations[random.randint(0,len(observations)-1)]

def initTheories(beam):
	diag = eye(nument)
	return [(zeros((numrules)),copy(diag)) for i in range(beam)]

def proposalsFromError(theories,error):
	print(theories)
	print(error)
	(i,e1,e2)= error
	I = zeros((nument,nument,numint))
	registerI(I,"attract","a","b")
	for (w,T) in theories:
		F= getForward(w)
		print(I.shape)
		print(R.shape)
		x = F.transpose().dot(I.flatten())
		print(x)
	
	

def unconverged(theories):
	return True

def pruneTheories(theories,observations):
	return theories

def edss(observations):
	beam = 2
	theories = initTheories(beam)
	while(unconverged(theories)):
		(i,e1,e2)  = obs =  getObs(observations)
		print (i,e1,e2)
		newtheories = proposalsFromError(theories,obs)
		theories = pruneTheories(newtheories,observations)
		exit()


edss(observations)
