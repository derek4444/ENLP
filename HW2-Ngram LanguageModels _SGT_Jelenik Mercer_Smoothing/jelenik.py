import fileinput
import sys
import math

epsilon = '*e*'
newline = '\r\n'
unigramcountmap = dict()
unigramprobmap = dict()
totalunigramcount = 0
startstate = 1
finalstate = 0

def unigramcalc() :
	calcunigramcount()
	calcunigramprob()	
	writeunigramfsa()

####	Calculate the count of unigram terms

def calcunigramcount() :
	global unigramcountmap
	global totalunigramcount

	for inputline in fileinput.input('TRAIN') :
		inputline = inputline.strip('\r\n')
		inputline = inputline.strip(' ')
		if len(inputline) == 0 :
			continue
		unigramcountmap['E'] = 0.0
		for character in inputline :
			if character == ' ' :
				continue
			if character in unigramcountmap :
				unigramcountmap[character] = unigramcountmap[character] + 1.0
			else :
				unigramcountmap[character] = 1.0
			totalunigramcount += 1.0
		unigramcountmap['E'] += 1.0
		totalunigramcount += 1.0
	fileinput.close()


####	Calculate the unigram probability value for the elements in given vocabulary

def calcunigramprob() :
	global unigramcountmap
	global totalunigramcount
	global unigramprobmap

	for key in unigramcountmap :
		unigramprobmap[key] = unigramcountmap[key]/totalunigramcount

####	Writing the output in the format accepted by Carmel

def writeunigramfsa() :
	global finalstate
	global startstate
	global newline
	global unigramprobmap
	global unigramcountmap
	global totalunigramcount
	global epsilon

	outputfile = open('unigram_j.wfsa','w')
	outputstring = '%s%s' % (finalstate,newline)
	outputfile.write(outputstring)

	for key in unigramprobmap :
		unigramprobmap[key] = unigramcountmap[key]/totalunigramcount
		outputstring = '(%s (%s %s %s %s))%s' % (startstate,startstate,epsilon,key,unigramprobmap[key],newline)
		outputfile.write(outputstring)
		print key,unigramcountmap[key],unigramprobmap[key]

	endcount = unigramcountmap['E']
	outputstring = '(%s (%s %s %s %s))%s' % (startstate,finalstate,epsilon,epsilon,endcount/totalunigramcount,newline)
	outputfile.write(outputstring)
	outputfile.close()

if __name__ == '__main__' :
	unigramcalc()
 	
