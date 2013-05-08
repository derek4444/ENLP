import fileinput
import sys
import math
from operator import itemgetter

adjustedbigramfreqmap = dict()
adjustedunigramfreqmap = dict()
adjustedunigramNvalue = 0.0
binsize = 95
lambda1 = 0.10
lambda2 = 0.90
lambda0 = 0.00
normalunigramcount = 0.0


####	Simple Good Turing Smoothing for Language Modelling

def gt_binning(trainfilename,outputfilename) :
	unigramprobmap = dict()
	trainfilename = 'TRAIN'
	bigramprodprobmap = dict()
	biniddict = dict()
	bigramcountmap = dict()
	sortedbigramproblist = []
	rclassmap = dict()
	global adjustedbigramfreqmap
	global adjustedunigramfreqmap	
	bigramprobmap = dict()

	unigramprobmap = calcunigramprob(trainfilename)
	bigramprodprobmap = calcbigramprodprob(trainfilename,unigramprobmap)
	biniddict = bigrambinning(bigramprodprobmap) 
	bigramcountmap = calcfilebigramcount(trainfilename)
	
	for key in biniddict :
		templist = biniddict[key]
		calcsgt(templist,bigramcountmap)
	calcadjustedunigramfreq()
	bigramprobmap = calcbigramprob()
	writefsa(bigramprobmap,'bigram_binning_sgt.wfsa')
	calcadjustedunigramNvalue()
	bigramprobmap = calcinterpolatedbigramprob(unigramprobmap)	
	writefsa(bigramprobmap,'bigram_binning_sgt_interpolated.wfsa')
	fileinput.close()

####	Finds the adjusted unigram frequency values

def calcadjustedunigramNvalue() :
	global adjustedunigramNvalue
	global adjustedunigramfreqmap
	global normalunigramcount
	for element in adjustedunigramfreqmap :
		print element,adjustedunigramfreqmap[element]
		adjustedunigramNvalue += adjustedunigramfreqmap[element]

	print 'adjusted unigram frequnecy :',adjustedunigramNvalue
	print 'normal unigram frequency :',normalunigramcount	

####	Finds interpolated Bi-gram probability values

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
		#term2 = unigramprobmap[token2]
		bigramprobmap[key] = term1 + term2 + lambda0
		print 'term1 :',term1
		print 'term2 :',term2
		print 'term3 :',lambda0 
		tempprobdict[token1] += bigramprobmap[key]

	for element in tempprobdict :
		print element,tempprobdict[element]
	return bigramprobmap

####	Calculates the bigram probability values

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

####	Applies Simple Good Turing Method and finds adjusted frequencies of Uni-Gram terms

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
	return adjustedunigramfreqmap

####	Applies Simple Good Turing Method and finds adjusted frequencies of Bi-Gram terms

def calcsgt(binbigramlist,bigramcountmap) :
	bigramclassmap = dict()
	bigramlist = [[] for index in range(2000)]
	listindex = 0
	zrvaluemap = dict()
	rvaluemap = dict()
	global adjustedfreqmap

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

####	Gets the input file name as argument and calculates the bigram probability values

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
	#for key in bigramcountmap :
	#	print key,bigramcountmap[key]
	return bigramcountmap

####	Gets the input file name as argument and calculates the unigram probability values

def calcunigramprob(inputfilename) :
	unigramcount = dict()
	unigramprob = dict()
	totallettercount = 0.0
	endcount = 0.0
	global normalunigramcount

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
	normalunigramcount = totallettercount
	for key in unigramcount :
		if key not in unigramprob :
			unigramprob[key] = unigramcount[key]/totallettercount
	return unigramprob

####	Gets the name of the test file, unigram probs as parameter and finds the Bigram Probability values

def calcbigramprodprob(testfilename,unigramprobmap) :
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

####	Writes the output FSA in the format accepted by Carmel

def writefsa(bigramprobmap,outputfilename) :
	alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_']
#	global stateid 
#	global startstate
#	global finalstate
	
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
		
	print 'inside the write fsa function'
	outputfile.close()


if __name__ == '__main__' :
	gt_binning(sys.argv[1],sys.argv[2])

