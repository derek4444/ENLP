import fileinput
import operator


wordtypes = set()
tagtypes = set()
wordtagcount = dict()
distinctcount = dict()
tagtagcount = dict()
wordtypes1 = set()

####	Find Basic Word Tag Statistics

def processfile(filename) :
	global wordtypes
	global tagtypes
	global wordtagcount
	global distinctcount
	global tagtagcount
	distincttaglist = [[] for index in range(6000)]
			
	print 'inside processing file',filename
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
			wordtypes1.add(word)
			word = word.lower()
			tag = splitword[1]
			tag2 = tag.strip('\r\n')
			token = word + '_' + tag2
			tag = tag1 + '_' + tag2
			
			if tag in tagtagcount :
				tagtagcount[tag] += 1
			else :
				tagtagcount[tag] = 1

			if word not in wordtypes :
				wordtypes.add(word)
			if tag2 not in tagtypes :
				tagtypes.add(tag2)
			if token not in wordtagcount :
				wordtagcount[token] = 1
				if word not in distinctcount :
					templist = []
					templist.append(tag2)
					distincttaglist = templist
					distinctcount[word] = templist	
				else :
					templist = distinctcount[word]
					templist.append(tag2)
					distinctcount[word] = templist 
			else :
				wordtagcount[token] += 1
			tag1 = tag2
		tag2 = 'E'
		tag = tag1 + '_' + tag2

		if tag not in tagtagcount :
			tagtagcount[tag] = 1
		else :
			tagtagcount[tag] += 1
		wordtagcount

	#for tag in tagtypes:
		#print tag

	#for tag in tagtagcount :
		#print tag,tagtagcount[tag]
	
	#print 'word types : ', len(wordtypes)
	#print 'tag types : ', len(tagtypes)
	maxwordcount = 0
	for key in distinctcount :
		if maxwordcount < len(distinctcount[key]) :
			maxwordcount = len(distinctcount[key])
	print 'maxwordcount : ' ,maxwordcount
	print 'number of words : ',len(wordtypes)
	print 'number of tags : ',len(tagtypes)
	print 'number of words : ',len(distinctcount)
	print 'number of word types - case insensitive :',len(wordtypes1)

	for element in distinctcount :
		if len(distinctcount[element]) == maxwordcount :
			print element,distinctcount[element]

	fileinput.close()


if __name__ == '__main__' :
	print 'inside main'	
	processfile("train.tags")
	
		
