import fileinput
import sys
import math

stateid = 2
startstate = 1
finalstate = 0

alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_','S','E']
trigramcountmap = dict()
trigramprobmap = dict()
adjustedtrigramfreqmap = dict()
adjustedbigramfreqmap = dict()

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
			trigramcountmap[token] = 0.0
			trigramprobmap[token] = 0.0

element1 = 'S'
element2 = 'S'
for element3 in alphabets :
	if element3 == 'S' :
		continue
	token =  element1 + element2 + element3
	trigramcountmap[token] = 0.0
	trigramprobmap[token] = 0.0


def sgttrigram() :
	global trigramprobmap

	calctrigramcount('TRAIN')
	calcsgt()
	calcadjustedbigramfreq()
	calctrigramprob()
	writetrigramfsa(trigramprobmap,'trigram_sgt.wfsa')

def calctrigramcount(inputfilename) :	
	global trigramcountmap
	
	for inputline in fileinput.input(inputfilename) :
		inputline = inputline.strip('\r\n')
		inputline = inputline.strip(' ')
		if len(inputline) == 0 :
			continue
		start = 0
		currentletter = ''
		previousletter1 = ''
		previousletter2 = ''
		token = ''
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

def calcsgt() :
	global trigramcountmap
	trigramclassmap = dict()
	trigramlist = [[] for index in range(2000)]
	listindex = 0
	zrvaluemap = dict()
	rvaluemap = dict()
	global adjustedtrigramfreqmap

	for element in trigramcountmap :
		classvalue = int(trigramcountmap[element])
		if classvalue in trigramclassmap :
			templist = trigramclassmap[classvalue]
			templist.append(element)
		else :
			trigramlist[listindex].append(element)
			trigramclassmap[classvalue] = trigramlist[listindex]
			listindex += 1

	rvaluesortedlist = trigramclassmap.keys()
	rvaluesortedlist.sort()
	
	previousrvalue = 0
	nextrvalue = 0
	nrplusonevalue = 0

	for element in rvaluesortedlist :
		currentnrvalue = len(trigramclassmap[element])
		currentindex = rvaluesortedlist.index(element)
		if currentindex < len(rvaluesortedlist) - 1 and currentindex > 0 :
			nextrvalue = rvaluesortedlist[currentindex + 1]
			zrvalue = (currentnrvalue)/(0.5 * (nextrvalue - previousrvalue))	
		else :
			nextrvalue = 0
			zrvalue = currentnrvalue
		rvalue = element	
		zrvaluemap[element] = zrvalue
		previousrvalue = element

	#for key in trigramclassmap :
	#	print key,trigramclassmap[key]

	maxrvalue = max(rvaluesortedlist)
	minvalue = min(rvaluesortedlist)
	previousrvalue = minvalue
	currentrvalue = 0
	slope = 0

	for index in range(minvalue,maxrvalue + 1) :
		if index == 0 :
			previousvalue = index
			continue
		if index in zrvaluemap :
			currentrvalue = index
			y2 = zrvaluemap[currentrvalue]
			y1 = zrvaluemap[previousrvalue]
			x2 = currentrvalue
			x1 = previousrvalue
			#print y2,y1,x2,x1
			slope = 0.0
			slope = (y2-y1)/(x2-x1)	
			#print slope
			intercept = y2 - slope * x2
			for rvalue in range(previousrvalue + 1,currentrvalue) :
				zrvalue = slope * rvalue + intercept
				zrvaluemap[rvalue] = zrvalue
			previousrvalue = currentrvalue

	rvaluemap[minvalue] = zrvaluemap[minvalue]/zrvaluemap[minvalue]
	for index in range(minvalue+1,maxrvalue) :
		rvaluemap[index] = ((index+1) * zrvaluemap[index + 1]) / (zrvaluemap[index])
	rvaluemap[maxrvalue] = rvaluemap[maxrvalue - 1]

	classvalue = 0
	for key in trigramclassmap :
		templist = trigramclassmap[key]
		classvalue = key
		for element in templist :
			adjustedtrigramfreqmap[element] = rvaluemap[classvalue]

def calctrigramprob() :
	global adjustedtrigramfreqmap
	global adjustedbigramfreqmap	
	global trigramprobmap
	alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_']

	tempprobdict = dict()
	trigramprobmap = dict()

	for key in adjustedbigramfreqmap :
		tempprobdict[key] = 0.0

	for key in  adjustedtrigramfreqmap:
		token1 = key[0]
		token2 = key[1]
		token = token1 + token2
		trigramprobmap[key] = adjustedtrigramfreqmap[key]/adjustedbigramfreqmap[token]
		tempprobdict[token] += trigramprobmap[key]

	#for key in tempprobdict :
	#	print key,tempprobdict[key]

def calcadjustedbigramfreq() :
	global adjustedtrigramfreq
	global adjustedbigramfreqmap
	alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_','S','E']

	adjustedbigramfreqmap['SS'] = 0.0

	for element1 in alphabets :
		for element2 in alphabets :
			if element2 == 'S' or element1 == 'E':
				continue
			token = element1 + element2
			adjustedbigramfreqmap[token] = 0.0

	for key in adjustedtrigramfreqmap :
		token1 = key[0]
		token2 = key[1]
		token = token1 + token2
		adjustedbigramfreqmap[token] += adjustedtrigramfreqmap[key]

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


if __name__ == '__main__' :
	sgttrigram()

