import fileinput
import sys
import math

alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_','S','E']
bigramprobmap = dict()
bigramtrainingcountmap = dict()
bigramheldoutcountmap = dict()
totalbigramheldoutcount = 0
totalbigramtrainingcount = 0
lambda1 = 0.10
lambda2 = 0.90
lambda0 = 0.00
startstate = 1
finalstate = 0
epsilon = '*e*'
newline = '\r\n'
unigramcountmap = dict()
unigramprobmap = dict()
totalunigramcount = 0
trigramtrainingcountmap = dict()
trigramheldoutcountmap = dict()
trigramprobmap = dict()
totaltrigramheldoutcount = 0
totaltrigramtrainingcount = 0

for element1 in alphabets :
	if element1 == 'E':
		continue
	for element2 in alphabets :
		if element2 == 'E' or element2 == 'S' :
			continue
		for element3 in alphabets :
			if element3 == 'S' :
				continue
			token = element1 + element2 + element3
			trigramtrainingcountmap[token] = 0.0
			trigramheldoutcountmap[token] = 0.0
			trigramprobmap[token] = 0.0

element1 = 'S'
element2 = 'S'
for element3 in alphabets :
	if element3 == 'S' :
		continue
	token =  element1 + element2 + element3
	trigramtrainingcountmap[token] = 0.0
	trigramheldoutcountmap[token] = 0.0
	trigramprobmap[token] = 0.0
	

for element1 in alphabets :
	if element1 == 'E' :
		continue
	for element2 in alphabets :
		if element2 == 'S' :
			continue
		token = element1 + element2
		bigramtrainingcountmap[token] = 0.0
		bigramheldoutcountmap[token] = 0.0
		bigramprobmap[token] = 0.0

def trigramcalc() :
	global trigramprobmap
	global trigramtrainingcountmap
	global trigramheldoutcountmap

	trigramtrainingcountmap = calctrigramcount('TRAIN',trigramtrainingcountmap)
	trigramheldoutcountmap = calctrigramcount('HELDOUT',trigramheldoutcountmap)
	calctrigramprob()
	writetrigramfsa(trigramprobmap,'trigramheldout.wfsa')

####	Calculate the count of trigram terms in the vocabulary

def calctrigramcount(inputfilename,trigramcountmap) :	
	global alphabets

	for inputline in fileinput.input(inputfilename) :
		inputline = inputline.strip('\r\n')
		inputline = inputline.strip(' ')
		if len(inputline) == 0 :
			continue
		start = 0
		currentletter = ''
		previousletter1 = ''
		previousletter2 = ''
		for character in inputline :
			if character == ' ' :
				continue
			currentletter = character
			if start == 0 :
				previousletter1 = 'S'
				previousletter2 = 'S'
				token = previousletter1 + previousletter2 + currentletter
				trigramcountmap[token] += 1.0
				previousletter1 = previousletter2
				previousletter2 = currentletter
				start = 1
				continue
			token = previousletter1 + previousletter2 + currentletter
			trigramcountmap[token] += 1.0
			previousletter1 = previousletter2
			previousletter2 = currentletter
		currentletter = 'E'
		token = previousletter1 + previousletter2 + currentletter
		trigramcountmap[token] += 1.0
	fileinput.close()
	return trigramcountmap

####	Calculate trigram probability values

def calctrigramprob() :
	global alphabets
	global trigramtrainingcountmap
	global trigramheldoutcountmap
	global trigramprobmap
	global totaltrigramheldoutcount
	global bigramprobmap	
	trigramclassmap = dict()
	trigramclasslist = [[] for index in range(10000)]
	trigramheldoutclassmap = dict()
	trigramaveragemap = dict()
	samplebigramcountmap = dict()
	tempprobmap = dict()
	

	listindex = 0				 	
	for key1 in trigramtrainingcountmap :
		trigramtoken = key1
		trigramcount = int(trigramtrainingcountmap[trigramtoken])
		if trigramcount in trigramclassmap:
			templist = trigramclassmap[trigramcount]
			templist.append(trigramtoken)
		else :
			trigramclasslist[listindex].append(trigramtoken)
			trigramclassmap[trigramcount] = trigramclasslist[listindex]
			listindex = listindex + 1

	for key in trigramclassmap :
		trigramheldoutclassmap[key] = 0
		trigramaveragemap[key] = 0	

	for key in trigramclassmap :
		templist = trigramclassmap[key]
		totaltrigramheldoutcount += len(templist)
		for element in templist :
			trigramheldoutclassmap[key] += trigramheldoutcountmap[element]
	templist = []	
	for key in trigramheldoutclassmap :
		trigramaveragemap[key] = trigramheldoutclassmap[key]/len(trigramclassmap[key])
		templist = trigramclassmap[key]
		for element in templist :
			token = element[0] + element[1]
			if token in samplebigramcountmap :
				samplebigramcountmap[token] += trigramaveragemap[key]
			else :
				samplebigramcountmap[token] = trigramaveragemap[key]

	templist = []
	for key in trigramheldoutclassmap :
		templist = trigramclassmap[key]
		for element in templist :
			token = element[0] + element[1]
			trigramprobmap[element] = trigramaveragemap[key]/samplebigramcountmap[token]

	tempprobmap = dict()

	for key in trigramprobmap :
		token =  key[0] + key[1]
		if token in tempprobmap :
			tempprobmap[token] += trigramprobmap[key]
		else :			 		
			tempprobmap[token] = trigramprobmap[key]

	for element in trigramprobmap :
		print element,trigramprobmap[element]

	#for element in tempprobmap :
		#print element,tempprobmap[element]

####	Write trigram FSA in the format accepted by Carmel

def writetrigramfsa(trigramprobmap,outputfilename) :
	alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_']

	stateid = 2
	startstate = 1
	finalstate = 0
	statemap = dict()
	newline = '\r\n'
	epsilon = '*e*'

	for element in alphabets :
		token = 'S' + element
		statemap[token] = stateid
		stateid = stateid + 1 

	for element1 in alphabets :
		for element2 in alphabets :
			token = element1 + element2
			statemap[token] = stateid
			stateid = stateid + 1
	
	outputfile = open(outputfilename,'w')
	outputstring = "%s%s" % (finalstate,newline)
	outputfile.write(outputstring)
	token1 = 'SS'
	token2 = 'S'
	token3 = 'E'

	for element in alphabets :
		token = token1 + element
		statetoken = token2 + element
		outputstring = "(%s (%s %s %s %s))%s" % (startstate,statemap[statetoken],epsilon,element,trigramprobmap[token],newline) 	
		outputfile.write(outputstring)
		token = token2 + element + token3
		outputstring = "(%s (%s %s %s %s))%s" % (statemap[statetoken],finalstate,epsilon,epsilon,trigramprobmap[token],newline) 	
		outputfile.write(outputstring)

	for element1 in alphabets :
		for element2 in alphabets :
			statetoken1 = token2 + element1
			statetoken2 = element1 + element2
			probtoken = token2 + element1 + element2
			outputstring = "(%s (%s %s %s %s))%s" % (statemap[statetoken1],statemap[statetoken2],epsilon,element2,trigramprobmap[probtoken],newline)
			outputfile.write(outputstring)

	for element1 in alphabets :
		for element2 in alphabets :
			statetoken1 = element1 + element2
			for element3 in alphabets :
				statetoken2 = element2 + element3
				probtoken = element1 + element2 + element3
				outputstring = "(%s (%s %s %s %s))%s" % (statemap[statetoken1],statemap[statetoken2],epsilon,element3,trigramprobmap[probtoken],newline) 	
				outputfile.write(outputstring)

	endtoken = 'E'

	for element1 in alphabets :
		for element2 in alphabets :
			statetoken1 = element1 + element2
			probtoken = statetoken1 + endtoken				
			outputstring = "(%s (%s %s %s %s))%s" % (statemap[statetoken1],finalstate,epsilon,epsilon,trigramprobmap[probtoken],newline)
			outputfile.write(outputstring)

	token = 'SS' + 'E'
	outputstring = "(%s (%s %s %s %s))%s" % (startstate,finalstate,epsilon,epsilon,trigramprobmap[token],newline) 	
	outputfile.write(outputstring)

	print 'inside the write fsa function'
	outputfile.close()
					

def bigramcalc() :
	global bigramprobmap
	global bigramtrainingcountmap
	global bigramheldoutcountmap

	bigramtrainingcountmap = calcbigramcount('TRAIN',bigramtrainingcountmap)
	bigramheldoutcountmap = calcbigramcount('HELDOUT',bigramheldoutcountmap)
	calcbigramprob()
	writebigramfsa(bigramprobmap,'bigramheldout.wfsa')

####	Calculate the count of bigram terms in the vocabulary

def calcbigramcount(inputfilename,bigramcountmap) :	
	global alphabets

	for inputline in fileinput.input(inputfilename) :
		inputline = inputline.strip('\r\n')
		inputline = inputline.strip(' ')
		if len(inputline) == 0 :
			continue
		start = 0
		currentletter = ''
		previousletter = ''
		for character in inputline :
			if character == ' ' :
				continue
			currentletter = character
			if start == 0 :
				previousletter = 'S'
				token = previousletter + currentletter
				bigramcountmap[token] += 1.0
				previousletter = currentletter
				start = 1
				continue
			token = previousletter + currentletter
			bigramcountmap[token] += 1.0
			previousletter = currentletter
		currentletter = 'E'
		token = previousletter + currentletter
		bigramcountmap[token] += 1.0
	fileinput.close()
	return bigramcountmap

####	Calculate the bigram robability value of bigram terms in the vocabulary

def calcbigramprob() :
	global alphabets
	global bigramtrainingcountmap
	global bigramheldoutcountmap
	global bigramprobmap
	global totalbigramheldoutcount
	bigramclassmap = dict()
	bigramclasslist = [[] for index in range(10000)]
	bigramheldoutclassmap = dict()
	bigramaveragemap = dict()
	tempprobmap = dict()

	listindex = 0				 	
	for key1 in bigramtrainingcountmap :
		bigramtoken = key1
		bigramcount = int(bigramtrainingcountmap[bigramtoken])
		if bigramcount in bigramclassmap:
			templist = bigramclassmap[bigramcount]
			templist.append(bigramtoken)
		else :
			bigramclasslist[listindex].append(bigramtoken)
			bigramclassmap[bigramcount] = bigramclasslist[listindex]
			listindex = listindex + 1

	for key in bigramclassmap :
		bigramheldoutclassmap[key] = 0
		bigramaveragemap[key] = 0	

	for key in bigramclassmap :
		templist = bigramclassmap[key]
		totalbigramheldoutcount += len(templist)
		for element in templist :
			bigramheldoutclassmap[key] += bigramheldoutcountmap[element]		
	templist = []	
	for key in bigramheldoutclassmap :
		bigramaveragemap[key] = bigramheldoutclassmap[key]/len(bigramclassmap[key])
		tempprobmap[key] = bigramaveragemap[key]/totalbigramheldoutcount
		templist = bigramclassmap[key]
		for element in templist :
			bigramprobmap[element] = tempprobmap[key]

####	Write the output FSA of bi-gram terms
	
def writebigramfsa(bigramprobmap,outputfilename) :
	alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_']
	
	stateid = 2
	startstate = 1
	finalstate = 0
	statemap = dict()
	newline = '\r\n'
	epsilon = '*e*'

	for element in alphabets :
		statemap[element] = stateid
		stateid = stateid + 1

	outputfile = open(outputfilename,'w')
	outputstring = "%s%s" % (finalstate,newline)
	outputfile.write(outputstring)
	token1 = 'S'
	token2 = 'E'

	for element in alphabets :
		token = token1 + element
		outputstring = "(%s (%s %s %s %s))%s" % (startstate,statemap[element],epsilon,element,bigramprobmap[token],newline) 	
		outputfile.write(outputstring)
		token = element + token2
		outputstring = "(%s (%s %s %s %s))%s" % (statemap[element],finalstate,epsilon,epsilon,bigramprobmap[token],newline) 	
		outputfile.write(outputstring)

	token = 'S' + 'E'
	outputstring = "(%s (%s %s %s %s))%s" % (startstate,finalstate,epsilon,epsilon,bigramprobmap[token],newline) 	
	outputfile.write(outputstring)

	for element1 in alphabets :
		for element2 in alphabets :
			token = element1 + element2
			outputstring = "(%s (%s %s %s %s))%s" % (statemap[element1],statemap[element2],epsilon,element2,bigramprobmap[token],newline)
			outputfile.write(outputstring)
		
	outputfile.close()

def unigramcalc() :
	calcunigramcount()
	calcunigramprob()	
	writeunigramfsa()

####	Calculate the count of unigram terms in the vocabulary

def calcunigramcount() :
	global unigramcountmap
	global totalunigramcount

	for inputline in fileinput.input('TRAIN') :
		inputline = inputline.strip('\r\n')
		inputline = inputline.strip(' ')
		if len(inputline) == 0 :
			continue
		unigramcountmap['E'] = 0.0
		for character in inputline :
			if character == ' ' :
				continue
			if character in unigramcountmap :
				unigramcountmap[character] = unigramcountmap[character] + 1.0
			else :
				unigramcountmap[character] = 1.0
			totalunigramcount += 1.0
		unigramcountmap['E'] += 1.0
		totalunigramcount += 1.0
	fileinput.close()

####	Calculate unigram probability values of the terms in the vocabulary

def calcunigramprob() :
	global unigramcountmap
	global totalunigramcount
	global unigramprobmap

	for key in unigramcountmap :
		unigramprobmap[key] = unigramcountmap[key]/totalunigramcount

####	Write the output in the format accepted by Carmel

def writeunigramfsa() :
	global finalstate
	global startstate
	global newline
	global unigramprobmap
	global unigramcountmap
	global totalunigramcount
	global epsilon

	outputfile = open('unigramheldout.wfsa','w')
	outputstring = '%s%s' % (finalstate,newline)
	outputfile.write(outputstring)

	for key in unigramprobmap :
		unigramprobmap[key] = unigramcountmap[key]/totalunigramcount
		outputstring = '(%s (%s %s %s %s))%s' % (startstate,startstate,epsilon,key,unigramprobmap[key],newline)
		outputfile.write(outputstring)
		print key,unigramcountmap[key],unigramprobmap[key]

	endcount = unigramcountmap['E']
	outputstring = '(%s (%s %s %s %s))%s' % (startstate,finalstate,epsilon,epsilon,endcount/totalunigramcount,newline)
	outputfile.write(outputstring)
	outputfile.close()

if __name__ == '__main__' :
	unigramcalc()	
	bigramcalc()
	trigramcalc()
