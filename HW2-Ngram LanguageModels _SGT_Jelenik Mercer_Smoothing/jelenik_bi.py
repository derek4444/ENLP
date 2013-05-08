import fileinput
import sys
import math

alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_','S','E']
bigramtrainingcount = [[0.0]*29 for index in range(28)]
bigramheldoutcount = [[0.0]*29 for index in range(28)]
totalbigramheldoutcount = 0
bigrammlprobmap = dict()
bigramprobmap = dict()
lambda1 = 0.10
lambda2 = 0.90
lambda0 = 0.00
startstate = 1
finalstate = 0
epsilon = '*e*'
newline = '\r\n'

def bigramcalc() :
	global bigramprobmap
	global bigramtrainingcount
	global bigramheldoutcount

	bigramtrainingcount = calcbigramcount('TRAIN',bigramtrainingcount)
	bigramheldoutcount = calcbigramcount('HELDOUT',bigramheldoutcount)
	calcbigramprob()
	writebigramfsa()


####	Calculate the count of bigram terms in our vocabulary

def calcbigramcount(inputfilename,bigramcount) :	
	global alphabets

	for inputline in fileinput.input(inputfilename) :
		inputline = inputline.strip('\r\n')
		inputline = inputline.strip(' ')
		if len(inputline) == 0 :
			continue
		start = 0
		currentalphaid = 0
		previousalphaid = 0

		for character in inputline :
			if character == ' ' :
				continue
			currentalphaid = alphabets.index(character)
			if start == 0 :
				previousalphaid = alphabets.index('S')
				bigramcount[previousalphaid][currentalphaid] += 1.0
				previousalphaid = currentalphaid
				start = 1
				continue
			bigramcount[previousalphaid][currentalphaid] += 1.0
			previousalphaid = currentalphaid
		
		currentalphaid = alphabets.index('E')
		bigramcount[previousalphaid][currentalphaid] += 1.0
	fileinput.close()
	return bigramcount

####	Calculate the probability of bigram terms in our vocabulary

def calcbigrammlprob() :
	global alphabets
	global bigramtrainingcount
	global bigramheldoutcount
	global bigramprobmap
	global totalbigramheldoutcount
	bigramclassmap = dict()
	bigramclasslist = [[] for index in range(10000)]
	bigramheldoutclassmap = dict()
	bigramaveragemap = dict()



def calcbigramprob() :
	global alphabets
	global bigramtrainingcount
	global bigramheldoutcount
	global bigramprobmap
	global totalbigramheldoutcount
	bigramclassmap = dict()
	bigramclasslist = [[] for index in range(10000)]
	bigramheldoutclassmap = dict()
	bigramaveragemap = dict()

	for index in range(0,len(alphabets)-1) :	
		bigramprobmap[alphabets[index]] = 0.0

	listindex = 0				 	
	for i in range(0,len(bigramtrainingcount)) :
		for j in range(0,len(bigramtrainingcount[i])) :
			if alphabets[j] == 'S' :
				continue
			bigramtoken = alphabets[i] + alphabets[j]
			bigramcount = int(bigramtrainingcount[i][j])
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
			letter1 = element[0]
			letter2 = element[1]
			letter1id = alphabets.index(letter1)
			letter2id = alphabets.index(letter2)
			bigramheldoutclassmap[key] += bigramheldoutcount[letter1id][letter2id]		
	
	for key in bigramheldoutclassmap :
		bigramaveragemap[key] = bigramheldoutclassmap[key]/len(bigramclassmap[key])
		bigramprobmap[key] = bigramaveragemap[key]/totalbigramheldoutcount

####	Write the output FSA in a format accepted by CARMEL

def writebigramfsa() :
	global startstate
	global finalstate
	global newline
	global epsilon

	stateid = 2
	statemap = dict()
	

	outputfile = open('bigram_j.wfsa','w')	
	statemap[alphabets[27]] = startstate
	statemap[alphabets[28]] = finalstate

	outputstring = "%s%s" % (finalstate,newline)
	outputfile.write(outputstring)
	
	for index in range(0,29) :
		currenttoken = 'S' + alphabets[index]
		letter1id = alphabets.index('S')
		letter2id = alphabets.index(alphabets[index])

		if letter2id == alphabets.index('S') :
			continue

		if alphabets[index] not in statemap :
			statemap[alphabets[index]] = stateid
			stateid += 1

		traincount = bigramtrainingcount[letter1id][letter2id]

		if alphabets[index] != 'E' :
			token2 = alphabets[index]
		else :
			token2 = '*e*'

		outputstring = "(%s (%s %s %s %s))%s" % (startstate,statemap[alphabets[index]],epsilon,token2,bigramprobmap[traincount],newline)	
		outputfile.write(outputstring)
		if alphabets[index] not in statemap :
			statemap[alphabets[index]] = stateid
			stateid += 1
		
	for i in range(0,29) :
		for j in range(0,29):
			if alphabets[i] == 'S' or alphabets[j] == 'S' or alphabets[i] == 'E' :
				continue
			currenttoken = alphabets[i] + alphabets[j]
			letter1id = alphabets.index(alphabets[i])
			letter2id = alphabets.index(alphabets[j])
			traincount = bigramtrainingcount[letter1id][letter2id]
			
			
			if alphabets[j] != 'E' :
				token2 = alphabets[j]
			else :
				token2 = '*e*'

			outputstring = "(%s (%s %s %s %s))%s" % (statemap[alphabets[i]],statemap[alphabets[j]],epsilon,token2,bigramprobmap[traincount],newline)
			outputfile.write(outputstring)	
	outputfile.close()

if __name__ == '__main__' :
	bigramcalc()
