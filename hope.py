from numpy import *
import scipy.sparse
from multiprocessing import Pool
import random
class Prover:
	def __init__(self,ents,ints,types,observations):
		self.entities  = array(ents)
		self.nument    = self.entities.shape[0]
		self.interactions = array(ints)
		self.numint    = self.interactions.shape[0]
		self.types = array(types)
		self.numtyp    = self.types.shape[0]
		self.numpairs  = self.nument**2
		print("making templates")
		vartt = ["X","Y","Z"] 
		variables = [("X","Y","X","Y")] 
		tmprelations = [(r1,r2) for r1 in types for r2 in types if r1 < r2]
		tmprelations += [(r1,r1) for r1 in types]
		self.templates = [(rh,vh1,vh2,r[0],vb1,r[1],vb2) for rh in self.interactions for r in tmprelations for (vh1,vh2,vb1,vb2) in variables]
		self.numrules = len(self.templates)
		print("alocating matrices ")
		self.T = scipy.sparse.lil_matrix((self.numrules,self.numint*self.numpairs*self.numtyp*self.nument*self.numtyp*self.nument))
		self.w  = scipy.sparse.lil_matrix((1,self.numrules))
		self.Tsize = [self.nument,self.nument,self.numint,self.nument,self.nument,self.numtyp,self.numtyp]
		map(self.paratemp,range(self.numrules))
		self.R = self.T.copy()
		print("loaded hope matrix with size:")
		print(self.T.shape)	
		self.observations =observations
		self.I = zeros((self.nument,self.nument,self.numint))
		self.T = zeros((self.nument,self.numtyp))
		self.w  = zeros((self.numrules))

	def unifies(self,hi,hj,i,ii,vh1,vh2,vb1,vb2):
		rle = [hi,hj,i,ii]
		gle = [vh1,vh2,vb1,vb2]
		return [x==y for x in rle for y in rle] == [x==y for x in gle for y in gle] 

	def paratemp(self,tempth):
	    sub2ind = lambda x,y: ravel_multi_index(y, dims=x )
	    (relh,vh1,vh2,relb1,vb1,relb2,vb2) = self.templates[tempth]
	    rh = where(self.interactions== relh)[0]
	    rb1 = where(self.types== relb1)[0]
	    rb2 = where(self.types== relb2)[0]
	    for hi in range(self.nument):
		for hj in range(self.nument):
		    for i in range(self.nument):
			for ii in range(self.nument):
			       if self.unifies(hi,hj,i,ii,vh1,vh2,vb1,vb2):
					self.T[tempth,sub2ind(self.Tsize,(hi,hj,rh,i,ii,rb1,rb2))] = 1

	def registerT(self,rel, entity1):
		i1 = where(self.entities == entity1)[0]
		i3 = where (self.types== rel)[0]
		self.T[i1,i3] = 1


	def registerI(self,rel, entity1, entity2):
		i1 = where(self.entities == entity1)[0]
		i2 = where(self.entities == entity2)[0]
		i3 = where(self.interactions == rel)[0]
		self.I[i1,i2,i3] = 1

	def regrule(self,relh, vh1, vh2, relb1, vb1, relb2, vb2):
		for tempth in range(self.numrules) :
			(trelh,tvh1,tvh2,trelb1,tvb1,trelb2,tvb2) = self.templates[tempth]
			if (trelh == relh) and (trelb1 == relb1) and (trelb2 == relb2) and unifies(tvh1,tvh2,tvb1,tvb2,vh1,vh2,vb1,vb2):
				self.w[tempth] = 1
				return
		print("regrule FAILURE")
		print((relh, vh1, vh2, relb1, vb1, relb2, vb2))
		exit()
	#########################################
	# PURRTY PRINT
	##############################
	#
	def printInt(self) :
		for r in range(0,self.numint):
		    for i in range(0,self.nument):
			for j in range(0,self.nument):
				if self.I[i,j,r] > 0 :
					rrr =  self.interactions[r]
					eee1 = self.entities[i]
					eee2 = self.entities[j]
					print(  rrr+ "("+eee1+")." if eee1 == eee2 else rrr+"(" +eee1+","+eee2+")." )
		
	#
	def printTyp(self) :
		for r in range(0,self.numtyp):
		    for i in range(0,self.nument):
				if self.T[i,r] > 0 :
					rrr =  self.types[r]
					eee1 = self.entities[i]
					print(  rrr+ "("+eee1+")." )


	def printThe(self) :
		print(array(self.templates)[nonzero(self.w)])


	def getForward(self):
		Fp = scipy.sparse.lil_matrix(self.w.reshape((1,self.numrules))).dot(self.R)
		F = asarray(Fp.todense())
		F = F.reshape((self.numint*self.numpairs,self.numtyp*self.nument*self.numtyp*self.nument))
		return F

	def runTheory(self): 
		print("\n\nObservations:")
	#	printInt(I)
		print("\nTheory:")
		self.printThe()
		print("\nType System:")
		self.printTyp()
		F = self.getForward()
		self.I = F.dot(kron(self.T.reshape(self.nument,self.numtyp),self.T.reshape(self.nument,self.numtyp)).flatten()).reshape((self.nument,self.nument,self.numint))
		print("\n\nResult:")
		self.printInt()
		print("\n\n")
		return self.I

	def checkTemplate(self,w,t):
		(rh,vh1,vh2,r1,vb1,r2,vb2) = t
		if any([(wl[0] == rh and  ((wl[1]==r1 and wl[2] == r2) or (wl[1]==r2 and wl[2] == r1))) for wl in w]):
			return 1
		else:  return 0
	def run(self,theory):
		(T,w) = theory
		self.w = array(map(lambda t: self.checkTemplate(w,t),self.templates))
		for tlet in T:
			self.registerT(tlet[0],tlet[1])
		return self.runTheory();

