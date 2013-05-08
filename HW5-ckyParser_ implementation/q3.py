import fileinput
import math
from time import time,clock
import sys, fileinput

grammarset = set()
rulecountdict = dict()
ruleprobdict = dict()
ruledict = dict()
terminalsymbolsset = set()
preprocessedstring = []
reverserulelist = dict()
resultantstring = ''
nonterminalset = set()
nonterminalruledict = dict()
devinputstr = []
fout = open("outputfile.parses","w")
fout1 = open("train.grammar","w")
fout2 = open("cky.runtime","w")

def findRules(inputstr,lineno):
	global grammarset
	global terminalsymbolsset
	stateid = 0
	firstlist = []
	taglist = []
	tagstack = []
	taglist.append(firstlist)
	outputtag = ''
	printlist = ''
	terminalsymbol = ''
	i = 0
	global rulecountdict
 
	while(i<len(inputstr)) :
		if inputstr[i] == '(' :
			stateid = stateid + 1
			i = i + 1 
			tag = ''
			while inputstr[i] != ' ' :		
				tag = tag + inputstr[i]
				i = i +1
			i = i + 1
			tagstack.append(tag)
			nonterminalset.add(tag.strip(' '))
			taglist[stateid - 1].append(tag)
			templist = createEmptyList()
			taglist.append(templist)
		elif inputstr[i] == ')' :
			i = i + 1
			printlist = ' '.join(taglist[stateid]) 
			outputtag = tagstack.pop()
			if len(printlist) > 0 :
				outputtag = outputtag.strip(' ')
				printlist = outputtag + ' -> ' + printlist.strip(' ')
				grammarset.add(printlist)
				if printlist in rulecountdict :
					rulecountdict[printlist] += 1.0
				else :
					rulecountdict[printlist] = 1.0
				taglist[stateid] = []
			elif len(terminalsymbol) > 0:
				outputtag = outputtag.strip(' ')
				printlist = outputtag + ' -> ' + terminalsymbol.strip(' ')
				grammarset.add(printlist)
				if printlist in rulecountdict :
					rulecountdict[printlist] += 1.0
				else :
					rulecountdict[printlist] = 1.0
				terminalsymbolsset.add(terminalsymbol.strip(' '))
			printlist = ''
			outputtag = ''
			terminalsymbol = ''
			stateid = stateid - 1
		else :
			terminalsymbol = terminalsymbol + inputstr[i]
			i = i + 1


def createEmptyList() :
	templist = []
	return templist

def findProbRules() :
	global grammarset
	global ruleprobdict
	global rulecountdict
	global reverserulelist
	global fout1
	samplespacecount = dict()
	token = []
	samplecount = 0
	ntlist = []
	
	for element in grammarset :
		token = element.split('->')
		key = token[0].strip(' ')
		if key in samplespacecount :
			samplespacecount[key] += rulecountdict[element]
		else :
			samplespacecount[key] = rulecountdict[element]

	for element in grammarset :
		token = element.split('->')
		key1 = token[0].strip(' ')
		samplecount = samplespacecount[key1]
		ruleprobdict[element] = rulecountdict[element]/samplecount

	for element in ruleprobdict :
		printstring = element + ' # ' + str(ruleprobdict[element]) + '\n'
		fout1.write(printstring)

	for element in ruleprobdict :
		token = element.split(' -> ')
		key = token[1]
		value = token[0] + '#' + str(math.log(ruleprobdict[element]))
		if key not in reverserulelist :
			reverserulelist[key] = []
			reverserulelist[key].append(value)
		else :
			reverserulelist[key].append(value)

	for element in ruleprobdict :
		tokens = element.split(' -> ')
		key = tokens[0].strip(' ')
		value = tokens[1].split('#')
		value = value[0].strip(' ')
		if key not in nonterminalruledict :
			nonterminalruledict[key] = []
			nonterminalruledict[key].append(value)
		else :
			nonterminalruledict[key].append(value)
		
	for element in ruleprobdict :
		ruleprobdict[element] = math.log(ruleprobdict[element])

def processfile(filename) :
	global maxbranchfactor
	global maxlineno
	global strindex	
	global currentlist
	global taglist
	global trainwords
	global ruleprobdict
	global terminalsymbolsset
	global rulecountdict
	global fout1	
	maxbrachfactor = 0
	maxlineno = 0	
	lineno = 0
	terminalsymbol = ''
	prevmaxbranchfactor = 0

	currentlist = []
	for inputline in fileinput.input(filename) :
		strindex = 0
		findRules(inputline,lineno)
	
	findProbRules()
	fout1.close()

####	Process input file
		
def parsedevfile(filename) :
	lineno = 0
	global terminalsymbolsset
	inputtokens = []
	flag = 0
	global preprocessedstring
	global devinputstr
	
	for inputline in fileinput.input(filename) :
		inputline = inputline.strip('\n')
		inputline = inputline.strip(' ')
		devinputstr.append(inputline)		
		inputstr = ''
		inputtokens = inputline.split(' ')
		for word in inputtokens :
			if word in terminalsymbolsset :
				if flag == 0 :
					inputstr = word
					flag = 1
				else :
					inputstr = inputstr + ' ' + word
			else :
				if flag == 0 :
					inputstr = '<unk>'
					flag = 1
				else :
					inputstr = inputstr + ' ' + '<unk>'
		flag = 0
		
		preprocessedstring.append(inputstr)
		lineno = lineno + 1

####	Apply CKY Parsing algorithm

def parseCKY(devinputstr,inputstr,lineno) :
	global reverserulelist
	global fout
	inputlist = inputstr.split(' ')
	strlen = len(inputlist)
	rulelist = []
	counter = 0
	inputtoken = []
	bestindex = []
	bestvalue = []
	sentenceprob = float('-inf')
	global resultantstring
	resultantstring = ''
	global nonterminalset
	global nonterminalruledict
	global fout2

	inputtoken = inputstr.split(' ')	

	for i in range(strlen) :
		bestindex.append([])
		bestvalue.append([])
	
	for j in range(strlen) :
		for k in range(j + 1) :
			bestvalue[j].append(dict())
			bestindex[j].append(dict())

	starttime = time()

	for i in range(strlen) :
		key = inputtoken[i]
		if key in reverserulelist :
			value = reverserulelist[key]
		for element in value :
			elementtoken = element.split('#')
			nonterminal = elementtoken[0].strip(' ')
			prob = float(elementtoken[1])
			bestmap = bestvalue[i][i]

			if nonterminal not in bestmap :
				bestvalue[i][i][nonterminal] = prob
				bestindex[i][i][nonterminal] = (i,i,nonterminal)
			else :
				if prob > bestmap[nonterminal]:	
					bestvalue[i][i][nonterminal] = prob
					bestindex[i][i][nonterminal] = (i,i,nonterminal)

	for i in range(strlen) :
		for j in range(i-1,-1,-1) :
			for nonterminal in nonterminalset :
				for rule in nonterminalruledict[nonterminal] :
					dx = i - 1
					for k in range(i,j,-1) :
						ruletoken = rule.split(' ')
						if len(ruletoken) == 2 :
							firstnonterminal = ruletoken[0].strip(' ')
							secondnonterminal = ruletoken[1].strip(' ')
							bestmap1 = bestvalue[dx][j]
							bestmap2 = bestvalue[i][k]
							if firstnonterminal in bestmap1 and secondnonterminal in bestmap2 :
								prob1 = bestmap1[firstnonterminal]
								prob2 = bestmap2[secondnonterminal]
								crule = nonterminal + ' -> ' + firstnonterminal + ' ' + secondnonterminal
								prob3 = ruleprobdict[crule]
								rprob = prob1 + prob2 + prob3		
								if nonterminal not in bestvalue[i][j] :
									bestvalue[i][j][nonterminal] = rprob
									bestindex[i][j][nonterminal] = (dx,j,firstnonterminal,i,k,secondnonterminal)
								else :
									if rprob > bestvalue[i][j][nonterminal] :
										bestvalue[i][j][nonterminal] = rprob
										bestindex[i][j][nonterminal] = (dx,j,firstnonterminal,i,k,secondnonterminal)
						dx = dx - 1	
	endtime = time()
	timetaken = math.log(endtime - starttime)
	logstrlen = math.log(strlen)
	outputstring = str(logstrlen) + '\t' +str(timetaken) + '\n'
	fout2.write(outputstring)
	
	if 'TOP' in bestvalue[strlen - 1][0] :
		backtuple = bestindex[strlen-1][0]['TOP']
		sentenceprob = bestvalue[strlen - 1][0]['TOP']
	else :
		sentenceprob = float('-inf')
	resultantstring = ''

	if sentenceprob != float('-inf') :
		resultantstring = '(TOP'
		extractTaggedSentence(devinputstr,bestindex,bestvalue,backtuple)
		resultantstring += '\n'
		#resultantstring += ')' + '\n'
	else :
		resultantstring = '(TOP'
		inputlist = devinputstr.split(' ')
		#print inputlist[:strlen-1]
		resultantstring += createdummytree(inputlist[:strlen-1])
		resultantstring += '(PUNC '+ inputlist[strlen-1] + '))' + '\n'

	fout.write(resultantstring)
	#print resultantstring
	return sentenceprob

def createdummytree(inputtokens) :
	result = ''
	if len(inputtokens) <= 1 :
		result = ' (NP' + ' ' + inputtokens[0] + ')'
		return result
	result += ' (NP'
	currentresult = createdummytree(inputtokens[1:])
	#result += currentresult + ' ' +   
	result = result + ' ' + inputtokens[0] + ')' + ' (NP' + ' ' + currentresult + '))'
	return result


def extractTaggedSentence(inputstr,bestindex,bestvalue,backtuple):
	global resultantstring	
	if len(backtuple) == 3 :
		(bi,bj,NT) = backtuple
		token = inputstr.split(' ')
		resultantstring += ' ' + token[bi] + ')'
		return
	else :
		(bi,bj,NT1,si,sj,NT2) = backtuple
		firsttuple = (bi,bj,NT1)
		fbest = bestindex[bi][bj][NT1]
		resultantstring += ' (' + NT1 
		extractTaggedSentence(inputstr,bestindex,bestvalue,fbest)
		secondtuple = (si,sj,NT2)
		sbest = bestindex[si][sj][NT2]
		resultantstring += ' (' + NT2	
		extractTaggedSentence(inputstr,bestindex,bestvalue,sbest) 
	resultantstring += ')'
	return

	
def parse() :
	global preprocessedstring
	global devinputstr
	global fout

	lineno = 0
	zeros = 0
	for inputstr in preprocessedstring :
		prob = parseCKY(devinputstr[lineno],inputstr,lineno)
		lineno = lineno + 1
	fout.close()
	fout.close()			
		
if __name__ == '__main__' :
	testfilename = sys.argv[1 ]
	print testfilename
	processfile('train.trees.pre.unk')
	parsedevfile(testfilename)
	parse()
	print 'Parsed output file name : outputfile.parses' 
