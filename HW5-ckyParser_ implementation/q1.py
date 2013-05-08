import fileinput

maxbranchfactor = 0
maxlineno = 0
taglist = []
strindex = 0
currentlist = []
trainwords = set()
devwords = set()

def findBranchingFactor(inputstr,lineno) :
	global maxbranchfactor
	global maxlineno
	global strindex
	global taglist
	global currentlist
	global trainwords
	tag = ''
	branchingfactor = 0
	j = strindex
	i = j
	terminalsymbol = ''

	while i < len(inputstr) :
		if inputstr[i] == ')' :
			strindex = strindex + 1
			if terminalsymbol != '' :
				trainwords.add(terminalsymbol.lower())
				return terminalsymbol
			else :
				return tag
		if inputstr[i] == '(' :
			strindex = strindex + 1
			i = i + 1

			while(inputstr[i] != ' '):
				tag += inputstr[i]
				i = i + 1
				strindex = strindex + 1
			
			strindex = strindex + 1
			i = i + 1
			terminalsymbol = findBranchingFactor(inputstr,lineno)
			currentlist.append(tag + '->' + terminalsymbol)
			terminalsymbol = ''
			branchingfactor = branchingfactor + 1
			if branchingfactor >= maxbranchfactor :
				maxbranchfactor = branchingfactor
				maxlineno = lineno
				#taglist = currentlist
			i  = strindex
		else :
			terminalsymbol += inputstr[i]
			strindex = strindex + 1
			i = i + 1
	return currentlist

def processfile(filename) :
	global maxbranchfactor
	global maxlineno
	global strindex	
	global currentlist
	global taglist
	global trainwords
	maxbrachfactor = 0
	maxlineno = 0	
	lineno = 0
	terminalsymbol = ''
	prevmaxbranchfactor = 0

	currentlist = []
	for inputline in fileinput.input(filename) :
		strindex = 0
		currentlist = findBranchingFactor(inputline,lineno)
		lineno = lineno + 1
		if maxbranchfactor > prevmaxbranchfactor :
			taglist = currentlist
		prevmaxbranchfactor = maxbranchfactor
		currentlist = []
	
	print 'Maximum Branch Factor :',maxbranchfactor
	print 'Maximum Line no :',maxlineno
	
	#for element in trainwords :
		#print element	

	print 'Number of unique train words :',len(trainwords)

def processdevfile(filename) :
	global devwords

	for inputline in fileinput.input(filename) :
		inputtokens = inputline.split(' ')
		for token in inputtokens :
			token = token.strip(' ')
			token = token.strip('\n')
			devwords.add(token)
	fileinput.close()	
	
	#print 'Development words'
	#for element in devwords :
		#print element
	print 'Number of dev words : ',len(devwords)


def findUnique() :
	global devwords
	global trainwords
	count = 0

	for element1 in devwords :
		if element1 not in trainwords :
			count = count + 1

	print 'Number of words in dev not in train : ',count

if __name__ == '__main__' :
	processfile('train.trees')
	processdevfile('dev.strings')
	findUnique()
