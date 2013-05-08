import fileinput
import sys
import math

def unigramcalc(trainfile,outputfile) :
	epsilon = '*e*'
	newline = '\r\n'
	endcount = 0.0
	startstate = 1
	finalstate = 0
	totallettercount = 0.0
	totalcount = 0.0
	linecount = 0.0
	i = 0
	unigramcount = dict()
	unigramprob = dict()
	outputfile = open(outputfile,'w')

	outputstring = '%s%s' % (finalstate,newline)
	outputfile.write(outputstring)

	for inputline in fileinput.input(trainfile) :
		i = i + 1
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

	totallettercount += endcount

	for key in unigramcount :
		if key not in unigramprob :
			unigramprob[key] = unigramcount[key]/totallettercount
		outputstring = '(%s (%s %s %s %s))%s' % (startstate,startstate,epsilon,key,unigramprob[key],newline)
		outputfile.write(outputstring)
		print key,unigramcount[key],unigramprob[key]

	print endcount/totallettercount
	outputstring = '(%s (%s %s %s %s))%s' % (startstate,finalstate,epsilon,epsilon,endcount/totallettercount,newline)
	outputfile.write(outputstring)
	print endcount
	print totallettercount
	print totalcount
	outputfile.close()
	fileinput.close()

def bigramcalc() :
	alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','_','S','E']
	bigramprobmap = dict()
	bigramtrainingcount = [[0.0]*29 for index in range(28)]
	bigramheldoutcount = [[0.0]*29 for index in range(28)]
	bigramclassmap = dict()
	bigramclasslist = [[] for index in range(10000)]
	bigramheldoutclassmap = dict()
	bigramaveragemap = dict()
	totalheldoutlength = 0	
	outputfile = open('bigram.wfsa','w')
	epsilon = '*e*'
	newline = '\r\n'
	finalstate = 0
	startstate = 1
	stateid = 2
	statemap = dict()
	totalbigramcount = 0

	statemap[alphabets[27]] = startstate
	statemap[alphabets[28]] = finalstate

	for index in range(0,len(alphabets)-1) :	
		bigramprobmap[alphabets[index]] = 0.0

	for inputline in fileinput.input('TRAIN') :
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
				bigramtrainingcount[previousalphaid][currentalphaid] += 1.0
				previousalphaid = currentalphaid
				start = 1
				continue
			bigramtrainingcount[previousalphaid][currentalphaid] += 1.0
			previousalphaid = currentalphaid
		
		currentalphaid = alphabets.index('E')
		bigramtrainingcount[previousalphaid][currentalphaid] += 1.0

	currentalphaid = 0
	previousalphaid = 0

	for inputline in fileinput.input('HELDOUT') :
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
				bigramheldoutcount[previousalphaid][currentalphaid] += 1.0
				previousalphaid = currentalphaid
				start = 1
				totalheldoutlength += 1
				continue
			bigramheldoutcount[previousalphaid][currentalphaid] += 1.0
			previousalphaid = currentalphaid
			totalheldoutlength += 1
		
		totalheldoutlength += 1
		currentalphaid = alphabets.index('E')
		bigramheldoutcount[previousalphaid][currentalphaid] += 1.0

	#for lists in bigramtrainingcount :
	#	print lists
	
	maxtrainvalue = max(max(b) for b in bigramtrainingcount)
	maxheldoutvalue = max(max(b) for b in bigramheldoutcount)
	#print maxtrainvalue
	#print maxheldoutvalue
	#print 'maxvalue : ',max(maxtrainvalue,maxheldoutvalue)	

	listindex = 0				 	

	for i in range(0,len(bigramtrainingcount)) :
		for j in range(0,len(bigramtrainingcount[i])) :
			if alphabets[j] == 'S' :
				continue
			bigramtoken = alphabets[i] + alphabets[j]
			bigramcount = int(bigramtrainingcount[i][j])
			#print bigramcount,bigramtoken
			if bigramcount in bigramclassmap:
				templist = bigramclassmap[bigramcount]
				templist.append(bigramtoken)
			else :
				bigramclasslist[listindex].append(bigramtoken)
				bigramclassmap[bigramcount] = bigramclasslist[listindex]
				listindex = listindex + 1
	
	#print 'length : ',len(bigramclasslist)

	for key in bigramclassmap :
		#print key,bigramclassmap[key]
		bigramheldoutclassmap[key] = 0
		bigramaveragemap[key] = 0
	

	for key in bigramclassmap :
		templist = bigramclassmap[key]
		totalbigramcount += len(templist)
		for element in templist :
			letter1 = element[0]
			letter2 = element[1]
			letter1id = alphabets.index(letter1)
			letter2id = alphabets.index(letter2)

			bigramheldoutclassmap[key] += bigramheldoutcount[letter1id][letter2id]		
	
	for key in bigramheldoutclassmap :
		bigramaveragemap[key] = bigramheldoutclassmap[key]/len(bigramclassmap[key])
		bigramprobmap[key] = bigramaveragemap[key]/totalbigramcount		
		print key,bigramheldoutclassmap[key],bigramclassmap[key],bigramaveragemap[key],bigramprobmap[key]
		#print bigramprobmap[key]

	print 'total number of bigrams : ',totalheldoutlength,totalbigramcount

	outputstring = "%s%s" % (finalstate,newline)
	outputfile.write(outputstring)
	
	for index in range(0,29) :
		currenttoken = 'S' + alphabets[index]
		letter1id = alphabets.index('S')
		letter2id = alphabets.index(alphabets[index])
		#if alphabets[index] == 'S':
		#	continue

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
		print outputstring
		if alphabets[index] not in statemap :
			statemap[alphabets[index]] = stateid
			stateid += 1
		

	for element in statemap :
		print element,statemap[element]
	
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
			#print outputstring
			 
	fileinput.close()
	outputfile.close()

if __name__ == '__main__' :
	#unigramcalc(sys.argv[1],sys.argv[2])
	bigramcalc()
 	
