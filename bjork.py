from numpy import *
import scipy.sparse
from multiprocessing import Pool

#}}p = Pool(5)
###############################
# HERE WE INITIALIZE 'T' AND 'A'
###############################
#
# A: Activation matrix
# anne : female, parent of tom
# tom 
# cristi : female
# rule : mother :- parent female
entities  = array(["a" , "b" ,"c"])
nument    = entities.shape[0]
relations = array(["attracted" , "repelled", "innert", "t1","t2","t3"])
numrel    = relations.shape[0]
numpairs  = nument**2

sub2ind = lambda x,y: ravel_multi_index(y, dims=x )
#
#


print("making templates")
vartt = ["X","Y","Z"] 
tvariables = [(vh1,vh2,vb11,vb12,vb21,vb22) for vh1 in vartt for vh2 in vartt for vb11 in vartt for vb12 in vartt for vb21 in vartt for vb22 in vartt]
variables = [] 

def covered(x):
	space = [[v1==v2 for v1 in varvars for v2 in  varvars] for varvars in variables]
	return [v1==v2 for v1 in x for v2 in  x]  in space

for x in tvariables:
	(vh1,vh2,vb11,vb12,vb21,vb22) = x
	bvs = [vb11,vb12,vb21,vb22]
	if  (vh1 >= vh2) and any([ vh1 == bv for bv in bvs]+ [vh2 == bv] ) and any([vb11 == vb21, vb11==vb22 , vb12 ==  vb21, vb12 == vb22]) and not covered(x)  : 
		variables.append(x)

print(variables)


tmprelations = [(r1,r2) for r1 in relations for r2 in relations if r1 < r2]
tmprelations += [(r1,r1) for r1 in relations]

templates = [(rh,vh1,vh2,r[0],vb11,vb12,r[1],vb21,vb22) for rh in relations for r in tmprelations for (vh1,vh2,vb11,vb12,vb21,vb22) in tvariables]




numrules = len(templates)
print(numrules)
print("alocating matrices ")
T = scipy.sparse.lil_matrix((numrules,numrel*numpairs*numrel*numpairs*numrel*numpairs))
w  = scipy.sparse.lil_matrix((1,numrules))
Tsize = [nument,nument,numrel,nument,nument,nument,nument,numrel,numrel]

def unifies(hi,hj,i,j,ii,jj,vh1,vh2,vb11,vb12,vb21,vb22):
        rle = [hi,hj,i,j,ii,jj]
        gle = [vh1,vh2,vb11,vb12,vb21,vb22]
        return [x==y for x in rle for y in rle] == [x==y for x in gle for y in gle] 

#for tempth in range(numrules):
def paratemp( tempth):
    (relh,vh1,vh2,relb1,vb11,vb12,relb2,vb21,vb22) = templates[tempth]
    rh = where(relations== relh)[0]
    rb1 = where(relations== relb1)[0]
    rb2 = where(relations== relb2)[0]
    print(tempth);    
    for hi in range(nument):
	for hj in range(nument):
	    for i in range(nument):
		for j in range(nument):
		    for ii in range(nument):
		       for jj in range(nument):
			       if unifies(hi,hj,i,j,ii,jj,vh1,vh2,vb11,vb12,vb21,vb22):
                               		T[tempth,sub2ind(Tsize,(hi,hj,rh,i,j,ii,jj,rb1,rb2))] = 1
map(paratemp,range(numrules))
#T = load("tspace.npy");
save("ctspace",T)
#
#
################################################



################################################
# Rule and facts registration helper functions
################################################
#
def register(A,rel, entity1, entity2=0):
	if entity2:
		i1 = where(entities == entity1)[0]
		i2 = where(entities == entity2)[0]
		i3 = where(relations == rel)[0]
		A[i1,i2,i3] = 1
	else:
		i1 = where(entities == entity1)[0]
		i3 = where (relations == rel)[0]
		A[i1,i1,i3] = 1

def regrule(A,w,relh, vh1, vh2, relb1, vb11,vb12, relb2, vb21, vb22):
	for tempth in range(numrules) :
       		(trelh,tvh1,tvh2,trelb1,tvb11,tvb12,trelb2,tvb21,tvb22) = templates[tempth]
		if (trelh == relh) and (trelb1 == relb1) and (trelb2 == relb2) and unifies(tvh1,tvh2,tvb11,tvb12,tvb21,tvb22,vh1,vh2,vb11,vb12,vb21,vb22):
           		w[0,tempth] = 1
           		break

#########################################
# PURRTY PRINT
##############################
#
def purrtyPrint(At) :
	#print(A)
	for r in range(0,numrel):
	    for i in range(0,nument):
	    	for j in range(0,nument):
			#print( sub2ind((nument,nument,numrel),(i,j,r)))
			#print( At[sub2ind((nument,nument,numrel),(i,j,r))])
			if At[sub2ind((nument,nument,numrel),(i,j,r)),0] > 0 :
		     		rrr =  relations[r]
			    	eee1 = entities[i]
			  	eee2 = entities[j]
				print(  rrr+ "("+eee1+")." if eee1 == eee2 else rrr+"(" +eee1+","+eee2+")." )
	print("\n\n")



#
##########



##############################
#   Register ground facts
##############################
#
#register("female","anne")
#register("male","rob")

A = zeros((nument,nument,numrel))
register(A,"attract","a","b")
register(A,"innert","a","c")
register(A,"innert","b","c")

#register("female","cristi")
#####################
#   Register a rule
#####################
#
#regrule(w,"mother" , "X", "Y" , "female" , "X","X", "parent", "X", "Y")
#regrule(w,"father" , "X", "Y" , "male" , "X","X", "parent", "X", "Y")
#regrule(w,"eloped" , "X", "Y" , "father" , "X","Z", "mother", "Y", "Z")
#
####

def getForward(w):
	Fp = w.dot(T)
	F = Fp.todense()
	F = F.reshape((numrel*numpairs,numrel*numpairs*numrel*numpairs))
	return F


def run(w):
	Fp = w.dot(T)
	F = Fp.todense()
	F = F.reshape((numrel*numpairs,numrel*numpairs*numrel*numpairs))


	At = A.reshape(numpairs*numrel,1)
	#purrtyPrint(At)
	for t in range(0,2):
		AtAt = kron(At.reshape(numpairs,numrel),At.reshape(numpairs,numrel)).reshape(numpairs*numpairs*numrel*numrel,1)
#		print(F.shape)
#		print(AtAt.shape)
		At = At + F.dot(AtAt)
	#	print("Epoch " , t)
	#	purrtyPrint(At)
	return At
#
####
def mag(wx):
	print sum(sum(wx))
atcorrect = run(w)

exit();


def likelihood(A0,Af,w):
	Awf = runWith(A0,w) 
	error = mag(Af - Awf)
	return exp(1.0/error)

def prior(A0,Af,w):
	print(nonzero(w.flatten()).shape)
	return length(nonzero(w.flatten()))

def posterior(A0,Af,w):
	return likelihood(A0,Af,w)* prior(A0,Af,w)

def newHypothese(A0,Af,beam,wx):
	pass

def edss(A0,Af):
	beam = 4
	wx  = scipy.sparse.lil_matrix(random.rand(1,numrules))
	while(unconverged(A0,Af,wx)):
		newwx = newHypotheses(A0,Af,beam, wx)
		
		

wx  = scipy.sparse.lil_matrix(random.rand(1,numrules))
error = None;
epoch = 0;
momentum = 0
noise = 0.001
learningrate = 0.05
wxv = False ; 
while(error == None or error > 0.5):
	epoch = epoch + 1 
	atx = run(wx)
	error = sum(sum(square(atcorrect - atx)))
	print("Epoch " + str(epoch) + " : " + str(error) + " entries" )
	gwx =  ((getForward(wx).transpose()).dot(-1*(atcorrect - atx))).dot(atx.transpose())
	winc = (T * (gwx.flatten().transpose())).transpose()
	if epoch == 1 :
		wxv = 0*winc
	wxv = momentum*wxv + winc
	print(wxv)
	print(wx)
	wx = wx + scipy.sparse.lil_matrix(learningrate*wxv)+ noise*scipy.sparse.lil_matrix(random.randn(1,numrules))
	#print(wx)


