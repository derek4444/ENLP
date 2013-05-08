
import fileinput
import operator
import sys
import math

stateid = []
startstate = 1
endstate = 0
wordlist = []
taglist = []
wordtagcount = dict()
distinctcount = dict()
tagtagcount = dict()
tagprobmap = dict()
wordprobmap = dict()
inputlines = [[] for index in range(1000)]
stateid = []
edgecostlist = []
taglines = [[] for index in range(1000)]
eeta = 0.01
regular_constant = 0.05
N = 0
testlines = [[] for index in range(1000)]

####	Max - Margin Method to find POS Tagging

def calcExpectation(restartcount,iterationcount) :
	global inputlines
	global taglines
	alphamap = dict()
	betamap = dict()	
	global taglist
	global wordprobmap
	global tagprobmap
	global wordtagcount
	global N
	worsttagsequence = []
	edgecost = []

	N = len(inputlines)
	i = 0
	initializewordprobvalues()	
	for inputline in inputlines :
		if len(inputline) == 0 :	
			continue
		calcWordTagCounts(i)			
		totalnodes = len(inputline) * 2 * len(taglist) + 2
		stateid.append(totalnodes-1)
		edgecost = createArrayGraph(inputline,i)
		#if i == 10 :
			#print '---------------------------------'
			#print '------------edgecost-----------'
			#for element in edgecost :
				#print element
			#print '----------------------------------'
		edgecostlist.append(edgecost)
		worsttagsequence = calcAlphaValues(inputline,edgecost,i)
		#print worsttagsequence
		updateFeatureValues(i,worsttagsequence)
		clearWordTagCounts(i)
		i = i + 1

	#print '---------------------'
	#print 'edgecostlist[10]'
	#for element in edgecostlist[10] :
		#print element
	#print '---------------------'
	
	for z in range(0,3) :
		i = 0 
		for inputline in inputlines :
			if len(inputline) == 0 :
				continue
			calcWordTagCounts(i)
			applyRevisedValues(i)			
			totalnodes = len(inputline) * 2 * len(taglist) + 2
			worsttagsequence = calcAlphaValues(inputline,edgecostlist[i],i)					
			updateFeatureValues(i,worsttagsequence)
			clearWordTagCounts(i)	
			i = i +1

def updateFeatureValues(lineno,worsttagsequence) :
	global tagprobmap
	global wordprobmap
	global taglist
	global eeta
	global tagtagcount
	global wordtagcount	
	worstwordtagcount = dict()
	worsttagtagcount = dict()
	worstwordtagcount.clear()
	worsttagtagcount.clear()
	global inputlines
	global taglines
	global N
	global regular_constant

	########################### worst tag parameter calculation ############################

	for i in range(0,len(inputlines[lineno])) :  
		key = inputlines[lineno][i] + '_' + worsttagsequence[i]
		if key not in worstwordtagcount :
			worstwordtagcount[key] = 1
		else :
			worstwordtagcount[key] += 1

	key1 = 'S'
	for element in worsttagsequence :
		key = key1 + '_' + element
		if key not in worsttagtagcount :
			worsttagtagcount[key] = 1
		else :
			worsttagtagcount[key] += 1
		key1 = element
	key = key1 + '_' + 'E'
	worsttagtagcount[key] = 1

	#########################################################################################	
	
	for element1 in taglist :
		for element2 in taglist :
			key = element1 + '_' + element2
			if key in worsttagtagcount :
				term2 = worsttagtagcount[key]
			else :
				term2 = 0
			if key in tagtagcount:
				regterm = ((eeta * regular_constant) * tagprobmap[key]/N)
				tagprobmap[key] = tagprobmap[key] + (eeta * (tagtagcount[key] - term2)) - regterm 
			else :
				regterm = ((eeta * regular_constant) * tagprobmap[key]/N)
				tagprobmap[key] = tagprobmap[key] + (eeta * (0 - term2)) - regterm

	for element1 in taglist :
		for element2 in wordlist :
			key = element2 + '_' + element1
			if key in worstwordtagcount :
				term2 = worstwordtagcount[key]
			else :
				term2 = 0
			if key in wordtagcount:
				regterm = ((eeta * regular_constant) * wordprobmap[key]/N)
				wordprobmap[key] = wordprobmap[key] + (eeta * (wordtagcount[key] - term2)) - regterm
			else :
				regterm = ((eeta * regular_constant) * wordprobmap[key]/N)
				wordprobmap[key] = wordprobmap[key] + (eeta * (0 - term2)) - regterm

def clearWordTagCounts(lineno) :
	global wordtagcount
	global tagtagcount
	global inputlines
	global taglines

	#print inputlines[lineno]
	#print taglines[lineno]

	for i in range(0,len(inputlines[lineno])) :  
		key = inputlines[lineno][i] + '_' + taglines[lineno][i]
		wordtagcount[key] = 0

	key1 = 'S'
	for element in taglines[lineno] :
		key = key1 + '_' + element
		tagtagcount[key] = 0
		key1 = element
	key = key1 + '_' + 'E'
	tagtagcount[key] = 0


def calcWordTagCounts(lineno) :
	global wordtagcount
	global tagtagcount
	global inputlines
	global taglines

	for i in range(0,len(inputlines[lineno])) :  
		key = inputlines[lineno][i] + '_' + taglines[lineno][i]
		if key not in wordtagcount :
			wordtagcount[key] = 1
		else :
			wordtagcount[key] += 1

	key1 = 'S'
	for element in taglines[lineno] :
		key = key1 + '_' + element
		if key not in tagtagcount :
			tagtagcount[key] = 1
		else :
			tagtagcount[key] += 1
		key1 = element
	key = key1 + '_' + 'E'
	tagtagcount[key] = 1				


def applyRevisedValues(lineno) :
	global taglist
	global taglines
	global inputlines
	global tagtagcount
	global wordtagcount
	global wordprobmap
	global tagprobmap
	global edgecostlist
	global stateid
	taglength = len(taglist)
	inputline = inputlines[lineno]
	tagline = taglines[lineno]
	edgecost = edgecostlist[lineno]

	for i in range(0,2) :
		for j in range(0,len(taglist)) :
			if i == 1 :
				key = 'S' + '_' + taglist[j]
				if key in tagtagcount and tagtagcount[key] != 0 :
					fvalue = 1.0
					term1 = fvalue * tagprobmap[key]
					lossvalue = 0.0
				else :
					term1 = 0.0
					lossvalue  = 0.0
				edgecost[i][j] = term1 + lossvalue
			else :
				key = taglist[j] + 'E'
				if key in tagtagcount and tagtagcount[key] != 0 :
					fvalue = 1.0
					term1 = fvalue * tagprobmap[key]
					lossvalue = 0.0
				else :
					term1 = 0.0
					lossvalue  = 0.0
				edgecost[i][j] = term1 + lossvalue
	
	for i in range(2,stateid[lineno]-taglength+1) :
		characterindex = (i - 2) % (2*taglength)
		tagindex = (i-2)%taglength
		key1 = taglist[tagindex]
			
		if characterindex < taglength :
			key2 = taglist[tagindex]
			key3 = inputline[(i - 2)/(2*taglength)] + '_' + key2
			key4 = tagline[(i - 2)/(2*len(taglist))]
			if key4 == key2 :			
				lossvalue = 0.0
				fvalue = 1
			else :
				lossvalue = 1.0
				fvalue = 0
			if key3 in wordtagcount :
				edgecost[i][0] = fvalue * wordprobmap[key3] + lossvalue
			else :
				edgecost[i][0] = lossvalue		
		else :
			for j in range(0,taglength) :
				tag1 = taglist[(i - 2)%taglength]
				tag2 = taglines[lineno][(i-2)/(taglength*2)]
				tag3 = taglist[j]
				tag4 = taglines[lineno][((i-2)/(taglength*2))+1]
				key3 = tag2 + '_' + tag4
				if tag1 == tag2 and tag3 == tag4 :
					lossvalue = 0.0
					fvalue = 1.0
					edgecost[i][j] = fvalue * tagprobmap[key3] + lossvalue
				else :
					lossvalue = 0.0
					fvalue = 0.0
					edgecost[i][j] = lossvalue	


def createArrayGraph(inputline,lineno) :
	global stateid
	global tagprobmap
	global startstate
	global endstate
	global taglist
	global wordprobmap
	global taglines
	global wordtagcount
	global tagtagcount

	taglength = len(taglist)
	totalnodes = (len(inputline) * len(taglist) * 2) + 2
	edgecost = []
	firstpart = []
	secondpart = []
	fvalue = 0.0
	term1 = 0.0

	for i in range(0,2) :
		firstpart = []
		for j in range(0,len(taglist)) :
			if i == 1 :
				key = 'S' + "_" + taglist[j]
				if key in tagtagcount and tagtagcount[key] != 0 :
					fvalue = 1.0
					term1 = fvalue * tagprobmap[key]
					lossvalue = 0.0
				else :
					term1 = 0.0
					lossvalue = 0.0
				firstpart.append(term1 + lossvalue)
			else :
				key = taglist[j] + "_" + 'E'
				if key in tagtagcount and tagtagcount[key] != 0:
					fvalue = 1.0
					term1 = fvalue * tagprobmap[key]
					lossvalue = 0.0
				else :
					term1 = 0.0
					lossvalue  = 0.0
				firstpart.append(term1 + lossvalue) 				
		edgecost.append(firstpart)
		
	for i in range(2,stateid[lineno]-taglength+1) :
		stateindex = (i - 2) % (2*taglength)
		tagindex = (i-2)%taglength
		key1 = taglist[tagindex]
		firstpart = []
		secondpart = []
		
		if stateindex < taglength :
			tagindex1 = (i-2)/(2*len(taglist))
			key2 = taglist[tagindex]
			key4 = taglines[lineno][tagindex1]
			key3 = inputline[tagindex1] + '_' + key2
			if key4 == key2 :
				lossvalue = 0.0
				fvalue =  1
				secondpart.append(fvalue * wordprobmap[key3] + lossvalue)
			else :
				lossvalue = 1.0
				fvalue = 0
				term1 = 0
				secondpart.append(term1 + lossvalue)		
		else :
			for j in range(0,taglength) :
				tag1 = taglist[(i - 2)%taglength]
				tag2 = taglines[lineno][(i-2)/(taglength*2)]
				tag3 = taglist[j]
				tag4 = taglines[lineno][((i-2)/(taglength*2))+1]
				key3 = tag2 + '_' + tag4 
				if tag1 == tag2 and tag3 == tag4 :
					lossvalue = 0.0
					fvalue = 1.0
					firstpart.append(fvalue * tagprobmap[key3] + lossvalue)
				else :
					lossvalue = 0.0
					fvalue = 0.0
					firstpart.append(lossvalue)
		if stateindex < taglength :
			#print secondpart
			edgecost.append(secondpart)
		else :
			#print firstpart		
			edgecost.append(firstpart)
	#print '-------'
	#print edgecost
	#print '-------'
	return edgecost

def calcAlphaValues(inputline,edgecost,lineno) :
	global stateid
	global edgecostlist
	alphamap = dict()
	global startstate
	global endstate
	global taglist
	global taglines
	alphamap.clear()
	alphamap[startstate] = 0.0
	taglength = len(taglist) 
	totalnodes = len(inputline) * 2 * len(taglist) + 2
	statevalue = totalnodes - 1

	worsttagsequence = []	
	bestprevious = dict()
	bestvalue = dict()
	bestprevious.clear()
	bestvalue.clear()
	
	nextstate = startstate + 1
	for i in range(taglength) :
		alphamap[nextstate] = alphamap[startstate] + edgecost[1][i]
		bestvalue[nextstate] = alphamap[nextstate]
		bestprevious[nextstate] = startstate
		nextstate = nextstate + 1

	for i in range(nextstate,statevalue + 1) :
		#bestvalue[i] = float('-inf')
		#alphamap[i] = float('inf')
		if ((i-2)%(2*taglength)) > taglength -1 :
			alphamap[i] = alphamap[i-taglength] + edgecost[i-taglength][0]
			bestvalue[i] = alphamap[i]
			bestprevious[i] = i-taglength
		else :
			for j in range(nextstate-taglength,nextstate) :
				if i not in bestvalue :
					term1 = alphamap[j] + edgecost[j][(i-2)%taglength]
					bestvalue[i] = term1
					bestprevious[i] = j
				else :
					term2 = alphamap[j] + edgecost[j][(i-2)%taglength]
					if term2 > bestvalue[i] :
						bestvalue[i] = term2
						bestprevious[i] = j
			alphamap[i] = bestvalue[i]
			
		if (i-2)%taglength == taglength-1 :
			nextstate = nextstate + taglength

	nextstate = nextstate - taglength
	best = float('-inf')
	#print best
	for i in range(len(taglist)) :
		term1 = alphamap[nextstate] + edgecost[0][i]
		if term1 > best :
			#print 'inside final best calculation'
			bestvalue[endstate] = term1
			bestprevious[endstate] = nextstate
			best = term1
		nextstate = nextstate + 1

	#print 'nextstate : ',nextstate
	nextstate = totalnodes - 1
	if endstate not in bestprevious :
		#print 'endstate not in best previous'
		x = (nextstate-taglength) + taglist.index('.')
		bestprevious[endstate] = x + 1
		#print 'x best previous values : ',x,bestprevious[endstate]	

	#print inputline
	best = bestprevious[endstate]
	worsttag1 = []
	for i in range(0,len(inputline)*2) :
		if ((best-2)%(2*taglength)) > taglength-1 :
			thisbest = ((best-2)%taglength)
			worsttag1.append(taglist[thisbest])
		best = bestprevious[best]
	worsttag1.reverse()

	#best = endstate
	#worsttagnodes=[]
	#worsttagnodes.append(best)

	#while(best != 1) :
		#bestid = bestprevious[best]
		#worsttagnodes.append(bestid)
		#best = bestid
	#worsttagnodes.reverse()
	#print worsttagnodes

	#for i in range(0,len(worsttagnodes)-1) :
		#if i%2 == 1:
			#worsttagsequence.append(taglist[(worsttagnodes[i]-2)%taglength])
	#worsttagsequence.reverse()

	#print 'actual taglines : ', taglines[lineno]
	#print 'worst tag previous method :',worsttag1	
	#print 'new worst tag :',worsttagsequence
	#print '-----------------------'

	return worsttag1



def initializewordprobvalues() :
	global wordtagcount
	global tagtagcount	
	global inputlines
	global tagprobmap
	global wordprobmap
	global taglist	
	
	for element1 in wordlist :
		for element2 in taglist :
			key1 = element1 + '_'+element2
			#key2 = element2 + '_' + element1
			#if key1 in wordtagcount :
			wordprobmap[key1] = 0
	tag1 = 'S'	
	for tag2 in taglist :
		key1 = tag1 + '_' + tag2
		#if key1 in tagtagcount :
		tagprobmap[key1] = 0
	tag2 = 'E'
	for tag1 in taglist :
		key1 = tag1 + '_' + tag2
		#if key1 in tagtagcount :
		tagprobmap[key1] = 0

	for tag1 in taglist :
		for tag2 in taglist :
			key1 = tag1 + '_' + tag2
			#if key1 in tagtagcount :
			tagprobmap[key1] = 0

	#print 'len of word prob map',len(wordprobmap)
	#print 'len of tag prob map',len(tagprobmap)

def processfile(filename) :
	global wordlist
	global taglist
	global wordtagcount
	global distinctcount
	global tagtagcount
	global inputlines
	global taglines
	distincttaglist = [[] for index in range(6000)]
	wordtypes = set()
	tagtypes = set()	
		
	linecount = 0
	for inputline in fileinput.input(filename):
		inputtoken = inputline.strip(' ')
		inputtoken = inputline.strip('\r\n')
		inputtoken = inputline.split(' ')
		tag1 = 'S'
		tag2 = ''
		tag = ''
		for token in inputtoken :
			token = token.strip('\r\n')
			if len(token) == 0 :
				continue
			splitword = token.split('_')
			word = splitword[0]
			word = word.strip('\r\n')
			word = word.lower()
			inputlines[linecount].append(word)
			tag = splitword[1]
			tag2 = tag.strip('\r\n')
			taglines[linecount].append(tag2)
			token = word + '_' + tag2
			tag = tag1 + '_' + tag2
			
			if tag not in tagtagcount :
				tagtagcount[tag] = 0

			if word not in wordtypes :
				wordtypes.add(word)
			if tag2 not in tagtypes :
				tagtypes.add(tag2)
			if token not in wordtagcount :
				wordtagcount[token] = 0
				if word not in distinctcount :
					templist = []
					templist.append(tag2)
					distincttaglist = templist
					distinctcount[word] = templist	
				else :
					templist = distinctcount[word]
					templist.append(tag2)
					distinctcount[word] = templist 
			tag1 = tag2
		tag2 = 'E'
		tag = tag1 + '_' + tag2
		if tag not in tagtagcount :
			tagtagcount[tag] = 0
		linecount = linecount + 1

	maxwordcount = 0
	for key in distinctcount :
		if maxwordcount < len(distinctcount[key]) :
			maxwordcount = len(distinctcount[key])
	fileinput.close()
	taglist = list(tagtypes)
	wordlist = list(wordtypes)


def createDecoderLattice(inputline) :
	global tagprobmap
	global startstate
	global endstate
	global taglist
	global wordprobmap
	global taglines
	global wordtagcount
	global tagtagcount

	taglength = len(taglist)
	totalnodes = (len(inputline) * len(taglist) * 2) + 2
	edgecost = []
	firstpart = []
	secondpart = []
	tagprobvalue = 0
	lossvalue = 0
	fvalue = 0.0
	term1 = 0.0

	for i in range(0,2) :
		firstpart = []
		for j in range(0,len(taglist)) :
			if i == 1 :
				key = 'S' + "_" + taglist[j]
				if key in tagtagcount :
					fvalue = 1.0
					term1 = fvalue * tagprobmap[key]
				else :
					term1 = float('-inf')
				firstpart.append(term1)
			else :
				key = taglist[j] + "_" + 'E'
				if key in tagtagcount:
					fvalue = 1.0
					term1 = fvalue * tagprobmap[key]
				else :
					term1 = float('-inf')
				firstpart.append(term1) 				
		edgecost.append(firstpart)
		
	for i in range(2,totalnodes-taglength) :
		stateindex = (i - 2) % (2*taglength)
		tagindex = (i-2)%taglength
		key1 = taglist[tagindex]
		firstpart = []
		secondpart = []
		
		if stateindex < taglength :
			if stateindex == 0 : 
				flag = 0
				for j in range(0,taglength) :
					key = inputline[(i - 2)/(2*taglength)] + '_' + taglist[j]
					if key in wordtagcount :
						flag = 1

			tagindex1 = (i-2)/(2*len(taglist))
			key2 = taglist[tagindex]
			key3 = inputline[tagindex1] + '_' + key2

			if flag == 1 :
				if key3 in wordtagcount :
					fvalue =  1
					secondpart.append(fvalue * wordprobmap[key3])
				else :
					secondpart.append(float('-inf'))
			else :
				fvalue = 0
				secondpart.append(fvalue)
			if stateindex == taglength - 1 :
				flag = 0
		
		else :
			for j in range(0,taglength) :
				tag1 = taglist[(i - 2)%taglength]
				tag3 = taglist[j]
				key3 = tag1 + '_' + tag3
				if key3 in tagprobmap :
					fvalue = 1.0
					firstpart.append(fvalue * tagprobmap[key3])
				else :
					fvalue = 0.0
					firstpart.append(fvalue)
		if stateindex < taglength :
			edgecost.append(secondpart)
		else :		
			edgecost.append(firstpart)
	return edgecost

def decodeTestFile(filename) :
	global testlines	
	processTestFile(filename)
	edgecost = []
	besttagsequence = []
	currentline = []

	for i in range(0,len(testlines)) :
		if len(testlines[i]) > 0 :	
			currentline = [token.lower() for token in testlines[i]]
			edgecost = createDecoderLattice(currentline)
			#print '---------------------------'
			#print testlines[i]
			#print currentline
			#print '--------------------------'
			besttagsequence = calcAlphaValues(currentline,edgecost,-1)
			outputstring = ''
			j = 0
			for element in testlines[i] :
				outputstring = outputstring + element + '_' + besttagsequence[j]
				if j != len(testlines[i])-1 :
					 outputstring = outputstring + ' '
				j = j + 1
			print outputstring
			currentline = []


def processTestFile(filename) :
	global testlines

	linecount = 0
	for inputline in fileinput.input(filename):
		inputtoken = inputline.strip(' ')
		inputtoken = inputline.strip('\r\n')
		inputtoken = inputline.split(' ')
		if len(inputtoken) == 0 :
			continue
		for token in inputtoken :
			token = token.strip('\r\n')
			if len(token) == 0 :
				continue
			testlines[linecount].append(token)
		linecount += 1
	
if __name__ == '__main__' :
	restartcount = 0
	iterationcount = 1
	filename = 'train.tags'	
	
	processfile(filename)
	for i in range(1,len(sys.argv)) :
		if sys.argv[i] == '--!' :
			restartcount = int(sys.argv[i+1])
		elif sys.argv[i] == '--i' :
			iterationcount = int(sys.argv[i+1])
		elif sys.argv[i] == '-HJ' :
			filename = sys.argv[i+1]	

	calcExpectation(restartcount,iterationcount)
	decodeTestFile('test')

	fileinput.close()
