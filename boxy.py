import esperanza
import random
entities = ["a","b","c","d"]
interactions = ["attract","innert"]
types = ["mag","met","plas"]
obs = [["attract", "a" ,"b" ] , ["innert", "a", "c"],["innert" , "b" , "c"],["attract", "a" ,"d"], ["innert" , "b" , "d"],["innert" , "d","c"]]
rules = [["attract","mag","met"],["innert","met","plas"],["innert","mag","plas"], ["innert","met","met"]]
assignment = [(e,random.choice(types)) for e in entities]
p = esperanza.Problem(entities,interactions,obs) 
p.run2()
