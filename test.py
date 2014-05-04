import hope


        observations =          [("attract" , "a" , "b"),
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


																																																																				~

