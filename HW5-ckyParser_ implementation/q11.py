import fileinput

maxbranchfactor = 0
maxlineno = 0
taglist = []
strindex = 0
currentlist = []
trainwords = set()
devwords = set()
tagstack = []

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
	flag = 0
	currentrule = ''

	while i < len(inputstr) :
		if inputstr[i] == ')' :
			strindex = strindex + 1
			flag = 2
			#print currentrule
			if terminalsymbol != '' :
				return ''
			else :
				return tagstack.pop()

		if inputstr[i] == '(' :
			strindex = strindex + 1
			i = i + 1
			tag = ''
			while(inputstr[i] != ' '):
				tag += inputstr[i]
				i = i + 1
				strindex = strindex + 1
			tagstack.append(tag)
			if flag == 0 :
				currentrule += tag + '->'
				flag = 1
			strindex = strindex + 1
			i = i + 1
			tag = ''
			newtag = findBranchingFactor(inputstr,lineno)
			if newtag != '' :
				currentrule += ' ' + newtag
				print currentrule
			#if flag == 2 :	
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
	#print currentrule
	return currentrule

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

