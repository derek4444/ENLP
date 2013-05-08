import fileinput
import sys
import math
from operator import itemgetter

alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_','S','E']

unigramcountmap = dict
bigramcountmap	= dict()
trigramcountmap = dict()

unigramprobmap = dict()
bigramprobmap = dict()
trigramprobmap = dict()

bigramprodprobmap = dict()
trigramprodprobmap = dict()
trigramprodprobmap = dict()

adjustedbigramfreqmap = dict()
adjustedunigramfreqmap = dict()
adjustedtrigramfreqmap = dict()

binsize = 500
lambda1 = 0.10
lambda2 = 0.90
lambda0 = 0.00
adjustedunigramNvalue = 0.0

stateid = 2
startstate = 1
finalstate = 0

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
			trigramprodprobmap[token] = 0.0
element1 = 'S'
element2 = 'S'
for element3 in alphabets :
	if element3 == 'S' :
		continue
	token =  element1 + element2 + element3
	trigramcountmap[token] = 0.0
	trigramprobmap[token] = 0.0
	trigramprodprobmap[token] = 0.0


					##################### trigram module #####################################

def sgttrigram() :
	global trigramprobmap
	global unigramprobmap
	global bigramprobmap
	global bigramcountmap	
	global bigramprodprobmap
	global trigramprodprobmap	
	global adjustedtrigramfreqmap 
	biniddict = dict()
	biniddict1 = dict()
	templist = []	

	unigramprobmap = calcunigramprob('TRAIN')
	bigramprodprobmap = calcbigramprodprob(unigramprobmap)
	biniddict = bigrambinning(bigramprodprobmap) 
	bigramcountmap = calcfilebigramcount('TRAIN')	

	for key in biniddict :
		templist = biniddict[key]
		calcsgtbigram(templist,bigramcountmap)

	calcadjustedunigramfreq()
	bigramprobmap = calcbigramprob()
	calcadjustedunigramNvalue()
	bigramprobmap = calcinterpolatedbigramprob(unigramprobmap)

	trigramprodprobmap = calctrigramprodprob(unigramprobmap)
	biniddict1 = trigrambinning(trigramprodprobmap)	
	trigramcountmap = calctrigramcount('TRAIN')

	for key in biniddict1 :
		templist = biniddict1[key]
		calcsgttrigram(templist,trigramcountmap)
	
	#print '============================'
	#print len(adjustedtrigramfreqmap)

	#for key in adjustedtrigramfreqmap :
		#print key,adjustedtrigramfreqmap[key]

	calcadjustedbigramfreq()
	trigramprobmap = calctrigramprob()
	writetrigramfsa(trigramprobmap,'trigram_sgt_binning.wfsa')

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

def calcsgttrigram(bintrigramlist,trigramcountmap) :
	trigramclassmap = dict()
	trigramlist = [[] for index in range(2000)]
	listindex = 0
	zrvaluemap = dict()
	rvaluemap = dict()
	global adjustedtrigramfreqmap

	for element in bintrigramlist :
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
	
	for key in tempprobdict :
		print key,tempprobdict[key]
	return trigramprobmap

def calctrigramprodprob(unigramprobmap) :
	alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_']
	global trigramprodprobmap	
	
	for element in trigramprodprobmap :
		token1 = element[0]
		token2 = element[1]
		token3 = element[2]
		trigramprodprobmap[element] = unigramprobmap[token1] * unigramprobmap[token2] * unigramprobmap[token3]
	
	return trigramprodprobmap

def trigrambinning(trigramprodprobmap) :
	biniddict = dict()
	global binsize
	binid = 0
	binlist = [[] for index in range(1000)]
	sortedtrigramproblist = []
	
	sortedtrigramproblist = sorted(trigramprodprobmap.items(), key=itemgetter(1))
	index = 0
	listindex = 0
	for element in sortedtrigramproblist :
		binid = index / binsize		
		if binid in biniddict :
			templist = biniddict[binid]
			templist.append(element[0])
		else :
			binlist[listindex].append(element[0])
			biniddict[binid] = binlist[listindex]
			listindex += 1
		index += 1	
	return biniddict

	################################################# bigram module ####################################################


def calcbigramprodprob(unigramprobmap) :
	alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_']
	bigramprodprobmap = dict()
	totalbigrams = 0	
	token1 = 'S'
	token2 = 'E'
	token = ''

	for element in alphabets :
		tokenstart = token1 + element
		tokenend = element + token2
		bigramprodprobmap[tokenstart] = 0.0
		bigramprodprobmap[tokenend] = 0.0
	for element1 in alphabets :
		for element2 in alphabets :
			token = element1 + element2
			bigramprodprobmap[token] = 0.0
	token = token1 + token2
	bigramprodprobmap[token] = 0.0
	for element in bigramprodprobmap :
		token1 = element[0]
		token2 = element[1]
		bigramprodprobmap[element] = unigramprobmap[token1] * unigramprobmap[token2]
	return bigramprodprobmap

def calcsgtbigram(binbigramlist,bigramcountmap) :
	bigramclassmap = dict()
	bigramlist = [[] for index in range(2000)]
	listindex = 0
	zrvaluemap = dict()
	rvaluemap = dict()
	global adjustedbigramfreqmap

	for element in binbigramlist :
		classvalue = int(bigramcountmap[element])
		if classvalue in bigramclassmap :
			templist = bigramclassmap[classvalue]
			templist.append(element)
		else :
			bigramlist[listindex].append(element)
			bigramclassmap[classvalue] = bigramlist[listindex]
			listindex += 1

	rvaluesortedlist = bigramclassmap.keys()
	rvaluesortedlist.sort()
	
	previousrvalue = 0
	nextrvalue = 0
	nrplusonevalue = 0

	for element in rvaluesortedlist :
		currentnrvalue = len(bigramclassmap[element])
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
	for key in bigramclassmap :
		templist = bigramclassmap[key]
		classvalue = key
		for element in templist :
			adjustedbigramfreqmap[element] = rvaluemap[classvalue]

def calcinterpolatedbigramprob(unigramprobmap) :
	global adjustedbigramfreqmap
	global adjustedunigramfreqmap
	global adjustedunigramNvalue
	global lambda2
	global lambda1
	global lambda0
	
	tempprobdict = dict()
	bigramprobmap = dict()

	tempprobdict['S'] = 0.0
	tempprobdict['E'] = 0.0
	for key in adjustedunigramfreqmap :
		tempprobdict[key] = 0.0

	for key in adjustedbigramfreqmap:
		token1 = key[0]
		token2 = key[1]
		term1 = lambda2 * adjustedbigramfreqmap[key]/adjustedunigramfreqmap[token1]
		term2 = lambda1 * adjustedunigramfreqmap[token2]/adjustedunigramNvalue
		bigramprobmap[key] = term1 + term2 + lambda0
		tempprobdict[token1] += bigramprobmap[key]
	return bigramprobmap

def calcbigramprob() :
	global adjustedbigramfreqmap
	global adjustedunigramfreqmap	
	tempprobdict = dict()
	bigramprobmap = dict()

	tempprobdict['S'] = 0.0
	tempprobdict['E'] = 0.0
	for key in adjustedunigramfreqmap :
		tempprobdict[key] = 0.0

	for key in  adjustedbigramfreqmap:
		token1 = key[0]
		bigramprobmap[key] = adjustedbigramfreqmap[key]/adjustedunigramfreqmap[token1]
		tempprobdict[token1] += bigramprobmap[key]
	return bigramprobmap


def calcfilebigramcount(filename) :
	bigramcountmap = dict()
	totalbigramsfromfile = 0
	alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_']
	token1 = 'S'
	token2 = 'E'
	token = ''

	for element in alphabets :
		tokenstart = token1 + element
		tokenend = element + token2
		bigramcountmap[tokenstart] = 0.0
		bigramcountmap[tokenend] = 0.0
		
	for element1 in alphabets :
		for element2 in alphabets :
			token = element1 + element2
			bigramcountmap[token] = 0.0
			
	token = token1 + token2
	bigramcountmap[token] = 0.0

	for inputline in fileinput.input(filename) :
		inputline = inputline.strip('\r\n')
		inputline = inputline.strip(' ')
		if len(inputline) == 0 :
			continue
		start = 0
		currentalphaid = 0
		previousalphaid = 0
		previouscharacter = 'S'
		token = ''
		for character in inputline :
			if character == ' ' :
				continue
			token =  previouscharacter + character
			bigramcountmap[token] += 1.0
			previouscharacter = character
			totalbigramsfromfile += 1.0
		token = previouscharacter + 'E'
		bigramcountmap[token] += 1.0
	return bigramcountmap


def calcadjustedbigramfreq() :
	global adjustedtrigramfreqmap
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

def bigrambinning(bigramprodprobmap) :
	biniddict = dict()
	global binsize
	binid = 0
	binlist = [[] for index in range(1000)]
	sortedbigramproblist = []
	
	sortedbigramproblist = sorted(bigramprodprobmap.items(), key=itemgetter(1))

	index = 0
	listindex = 0
	for element in sortedbigramproblist :
		binid = index / binsize		
		if binid in biniddict :
			templist = biniddict[binid]
			templist.append(element[0])
		else :
			binlist[listindex].append(element[0])
			biniddict[binid] = binlist[listindex]
			listindex += 1
		index += 1	
	return biniddict


		################################################    unigram module    #################################################3


def calcadjustedunigramNvalue() :
	global adjustedunigramNvalue
	global adjustedunigramfreqmap
	for element in adjustedunigramfreqmap :
		#print element,adjustedunigramfreqmap[element]
		adjustedunigramNvalue += adjustedunigramfreqmap[element]


def calcadjustedunigramfreq() :
	global adjustedbigramfreq
	global adjustedunigramfreqmap

	alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_']
	adjustedunigramfreqmap['S'] = 0
	adjustedunigramfreqmap['E'] = 0
	for element in alphabets :
		adjustedunigramfreqmap[element] = 0

	for key in adjustedbigramfreqmap :
		token1 = key[0]
		adjustedunigramfreqmap[token1] += adjustedbigramfreqmap[key]

def calcunigramprob(inputfilename) :
	unigramcount = dict()
	unigramprob = dict()
	totallettercount = 0.0
	endcount = 0.0

	for inputline in fileinput.input(inputfilename) :
		inputline = inputline.strip('\r\n')
		inputline = inputline.strip(' ')
		if len(inputline) == 0 :
			continue
		for character in inputline :
			if character == ' ' :
				continue
			if character in unigramcount :
				unigramcount[character] = unigramcount[character] + 1.0
			else :
				unigramcount[character] = 1.0
			totallettercount += 1.0
		endcount += 1.0
	unigramcount['S'] = endcount
	unigramcount['E'] = endcount
	totallettercount += (2*endcount)
	for key in unigramcount :
		if key not in unigramprob :
			unigramprob[key] = unigramcount[key]/totallettercount

	fileinput.close()
	return unigramprob

		######################################    write fsa       ##################################################


def writetrigramfsa(trigramprobmap,outputfilename) :
	alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_']
	stateid = 2
	startstate = 1
	finalstate = 0
	statemap = dict()
	newline = '\r\n'
	epsilon = '*e*'

	print len(trigramprobmap)

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

