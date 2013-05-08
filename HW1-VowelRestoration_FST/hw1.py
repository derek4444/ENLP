import fileinput

forwardarray = []
reversearray = []
commonreversesuffixmap = dict()
commonreversesuffixlist = []
statearray = []
reversestatearray = []
stateindex = 2
startstate = 1
firstword = True
finalstate = 0
newline = "\r\n"
epsilon = "*e*"
underscore = "_"
prefixendindex = []
findex = 0
currentprefixendindex = 0
vowels = set(['a','e','i','o','u','A','E','I','O','U'])
outputset = set()

fileinput.close()

outputfile = open('english.fsa', 'w')
outputfile1 = open('remove-vowelsq5uncomposed.fst','w')

print 'PREFIX PROCESSING for creating the FSA and FST'

#########	Matching prefixes of words in the vocabulary and construct a trie of words
#########	Words which has common prefixes share same states in the trie

for inputline in fileinput.input("vocab") :
    stateset = set()
    statelist = []
    currentline = inputline.strip("\r\n")
    currentline = currentline.strip(" ")
    inputtoken = currentline.split(" ")

    if firstword == True :
        firstword = False
        forwardarray.append(inputtoken)
        statelist.append(startstate)
        
        for x in range(0,len(inputtoken)) :
            stateindex += 1
            statelist.append(stateindex)
        statearray.append(statelist)
        prefixendindex.append(len(inputtoken))        
        continue

    forwardarrayindex = len(forwardarray)-1
    forwardarray.append(inputtoken)
    findex = 0
          
    lastindex = len(forwardarray[forwardarrayindex])

    statelist.append(startstate)
    
    for firstindex in range(0,lastindex) :
        if(forwardarray[forwardarrayindex][firstindex] != inputtoken[firstindex]) :
            break
        statelist.append(statearray[forwardarrayindex][firstindex+1])        
        findex = findex + 1

    currentprefixendindex = findex
    prefixendindex.append(findex)

    if(prefixendindex[forwardarrayindex] < currentprefixendindex):
        prefixendindex[forwardarrayindex] = currentprefixendindex        
        
    for x in range(findex,len(inputtoken)) :
        stateindex += 1
        statelist.append(stateindex)
    statearray.append(statelist)
    

for index in range(0,len(prefixendindex)) :
    templist = []
    if len(forwardarray[index]) > prefixendindex[index] :
        templist = forwardarray[index][prefixendindex[index]:len(forwardarray[index])]
        templist.reverse()
        tempelement = "".join(templist)
        commonreversesuffixlist.append(tempelement)  

tempmap = dict()
for element in commonreversesuffixlist :
    tempmap[element] = 1

temparray = []

for key in tempmap :
    temparray.append(key)

temparray.sort()

commonreversesuffixlist = []

for element in temparray :
    liststring = []
    for character in element :
        liststring.append(character)    
    commonreversesuffixlist.append(liststring)

#------------------------------------------------------------- Suffix processing ------------------------------------------------------

print 'SUFFIX PROCESSING for creating FSA and FST'

#########	Matching suffixes of words in the vocabulary and construct a trie of words
#########	Words which has common suffixes share same states in the trie

firstword = True
reversearray = []

for inputtoken in commonreversesuffixlist :
    statelist = []

    if firstword == True :
        firstword = False
        reversearray.append(inputtoken)
                
        for x in range(0,len(inputtoken)) :
            stateindex += 1
            statelist.append(stateindex)
            
        reversestatearray.append(statelist)        
        continue

    reversearrayindex = len(reversearray)-1

    reversearray.append(inputtoken)
    findex = 0
       
    lastindex = len(reversearray[reversearrayindex])
    
    for firstindex in range(0,lastindex) :
        if(reversearray[reversearrayindex][firstindex] != inputtoken[firstindex]) :
            break
        statelist.append(reversestatearray[reversearrayindex][firstindex])        
        findex = findex + 1

    for x in range(findex,len(inputtoken)) :
        stateindex += 1
        statelist.append(stateindex)                
    
    reversestatearray.append(statelist)

for element in reversestatearray :
    element.reverse()

for index in range(0,len(commonreversesuffixlist)) :
    suffix = commonreversesuffixlist[index]
    suffix.reverse()
    currenttuple = tuple(suffix)
    commonreversesuffixmap[currenttuple] = reversestatearray[index]

for index in range(0,len(statearray)) :
    prefixindex = prefixendindex[index]
    wordlength = len(forwardarray[index])
    currentlist = forwardarray[index][prefixindex:wordlength]
    currenttuple = tuple(currentlist)
    if(prefixindex<wordlength) :
        statearray[index][prefixindex+1:wordlength+1] = commonreversesuffixmap[currenttuple]
        statearray[index].append(finalstate)
        forwardarray[index].append(epsilon)
    else :
        forwardarray[index].append(epsilon)
        statearray[index].append(finalstate)

#########	Writing the output trie in the format accepted by carmel

outputstring = "%s%s" % (finalstate,newline)
outputfile.write(outputstring)
outputfile1.write(outputstring)

lastindex = 0

for wordindex in range(0,len(forwardarray)) :
    for letterindex in range(0,len(forwardarray[wordindex])-1) :
        outputstring = "(%s (%s \"%s\"))" % (statearray[wordindex][letterindex],statearray[wordindex][letterindex+1],forwardarray[wordindex][letterindex])
        lastindex += 1
        if outputstring not in outputset :
            outputfile.write(outputstring)
            outputfile.write(newline)        
            if forwardarray[wordindex][letterindex] in vowels :
                outputstring1 = "(%s (%s \"%s\" %s))" % (statearray[wordindex][letterindex],statearray[wordindex][letterindex+1],forwardarray[wordindex][letterindex],epsilon)
            else :
                outputstring1 = "(%s (%s \"%s\" \"%s\"))" % (statearray[wordindex][letterindex],statearray[wordindex][letterindex+1],forwardarray[wordindex][letterindex],forwardarray[wordindex][letterindex])
            outputfile1.write(outputstring1)
            outputfile1.write(newline)
        outputset.add(outputstring)
    outputstring = "(%s (%s %s))" % (statearray[wordindex][lastindex],statearray[wordindex][lastindex+1],forwardarray[wordindex][lastindex])
    if outputstring not in outputset :
        outputfile.write(outputstring)
        outputfile.write(newline)
        outputfile1.write(outputstring)
        outputfile1.write(newline)
    outputset.add(outputstring)
    lastindex = 0

outputstring = "(%s (%s \"%s\"))" % (finalstate,startstate,underscore)
outputfile.write(outputstring)
outputfile.write(newline)

outputstring1 = "(%s (%s \"%s\" \"%s\"))" % (finalstate,startstate,underscore,underscore)
outputfile1.write(outputstring1)
outputfile1.write(newline)

outputfile.close()
fileinput.close()
outputfile1.close()

#--------------------------------------------- End of FSA and FST -------------------------------------------------------------#

#---------------------------------------------- Probabilistic FST Training for reconstructing vowels --------------------

print 'Calculating probability values from training data'

alphabets = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','\'']
wordcountmap = dict()
lettercountmap = dict()
forwardmap = dict()
reversemap = dict()
forwardprobmap = dict()
reverseprobmap = dict()
firstcountmap = dict()
firstcountprobmap = dict()
endcountmap = dict()
endcountprobmap = dict()
suffixcountmap = dict()
suffixcountprobmap = dict()
ngramcountmap = dict()
ngramprobmap = dict()
tokenwordprob = dict()

outputset2 = set()
definiteprobvalue = 1.0
totalwordcount = 0.0

forwardmapvalue = [[0.0]*27 for index in range(27)]
reversemapvalue = [[0.0]*27 for index in range(27)]
forwardmapprobvalue = [[0.0]*27 for index in range(27)]
reversemapprobvalue = [[0.0]*27 for index in range(27)]

for letter1 in alphabets :
    for letter2 in alphabets :
        key = letter1 + letter2
        suffixcountprobmap[key] = 0.0
        suffixcountmap[key] = 0.0
        
outputfile3 = open("english.wfsa","w")
outputfile4 = open("remove-vowelsq6.wfst","w")

for element in alphabets :
    firstcountmap[element] = 0.0
    firstcountprobmap[element] = 0.0
    endcountmap[element] = 0.0
    endcountprobmap[element] = 0.0

for inputline in fileinput.input("strings") :
    inputline = inputline.strip(" ")
    inputline = inputline.strip("\r\n")
    inputtoken = inputline.split(" \"_\" ")
    
    for index in range(0,len(inputtoken)) :
        currentstring = "".join(inputtoken[index])
        currentstring = currentstring.strip(" ")
        currentstring = currentstring.strip("\"")
        inputtoken[index] = currentstring.split("\" \"")
        tokenkey = "".join(inputtoken[index])
        
        if tokenkey in wordcountmap :
            wordcountmap[tokenkey] += 1
        else :
            wordcountmap[tokenkey] = 1

#------------------------------------------------------------ N-gram conditional probability calculation with additive smoothing----------------------------------------------#


print 'Calculating N-GRAM Conditional probability'

for element in wordcountmap :
    totalwordcount = totalwordcount + wordcountmap[element]
    for index in range(0,len(element)) :
        key = element[0:index+1]
        if key in ngramcountmap.keys() :
            ngramcountmap[key] += 1.0 * wordcountmap[element]
        else :
            ngramcountmap[key] = 1.0 * wordcountmap[element]


for element in alphabets :
    if element in wordcountmap :
        tokenwordprob[element] = (wordcountmap[element] *1000 + 1)/(totalwordcount * 1000 + totalwordcount) 
    else :
        tokenwordprob[element] =  1/(totalwordcount * 1000 + totalwordcount)
         

for element in ngramcountmap :
    if len(element) == 1 :
        if element not in ngramprobmap.keys() :
            if element in wordcountmap : 
                ngramprobmap[element] = tokenwordprob[element] * (ngramcountmap[element] * 10000 + wordcountmap[element])/(totalwordcount * 10000 + totalwordcount)
            else :
                ngramprobmap[element] = tokenwordprob[element] * (ngramcountmap[element] * 10000 + 1)/(totalwordcount * 10000 + totalwordcount)
    else :
        if element not in ngramprobmap.keys() :
            if element in wordcountmap :
                ngramprobmap[element] =(ngramcountmap[element] * 10000 + wordcountmap[element]*1000)/(ngramcountmap[element[0:len(element)-1]] * 10000 + totalwordcount)
            else :
                ngramprobmap[element] =(ngramcountmap[element] * 10000 + 1)/(ngramcountmap[element[0:len(element)-1]] * 10000 + totalwordcount)
index = 0

for element in alphabets :
    forwardmap[element] = forwardmapvalue[index]
    reversemap[element] = reversemapvalue[index]
    forwardprobmap[element] = forwardmapprobvalue[index]
    reverseprobmap[element] = reversemapprobvalue[index]
    lettercountmap[element] = 0
    index = index + 1

#------------------------------------------------------------------- 2-gram model --------------------------------------------------

for key in wordcountmap :
    totalwordcount = totalwordcount + wordcountmap[key]
    for index in range(0,len(key)) :
        letterindex = alphabets.index(key[index])
        lettercountmap[key[index]] = lettercountmap[key[index]] + (1 * wordcountmap[key])

        if index != 0 :
            previousletterindex = alphabets.index(key[index-1])
            reversemapvalue[letterindex][previousletterindex] = reversemapvalue[letterindex][previousletterindex] + (1.0 * wordcountmap[key])
        else :
            firstcountmap[key[index]] = firstcountmap[key[index]] + (1.0 * wordcountmap[key])

        if index == len(key) - 1 :
            previousletter = key[index-1]
            currentletter = key[index]
            suffix = previousletter + currentletter
            if suffix in suffixcountmap.keys() :
                suffixcountmap[suffix] = suffixcountmap[suffix] + wordcountmap[key] * 1.0
            else :
                suffixcountmap[suffix] = 1.0 * wordcountmap[key]
                
        if(index != len(key)-1) :
            nextletterindex = alphabets.index(key[index+1])
            forwardmapvalue[letterindex][nextletterindex] = forwardmapvalue[letterindex][nextletterindex] + (1.0 * wordcountmap[key])
        else :
            endcountmap[key[index]] = endcountmap[key[index]] + (1.0 * wordcountmap[key])


for element in suffixcountmap :
    suffixcountprobmap[element] = (suffixcountmap[element]*100 + 1)/(totalwordcount * 100 + 1)

for element in alphabets :
    index = alphabets.index(element)
    for nextindex in range(0,27) :        
        firstcountprobmap[element] =  (firstcountmap[element]*1000 + 1)/(totalwordcount * 1000 + totalwordcount)
        forwardmapprobvalue[index][nextindex] = (forwardmapvalue[index][nextindex]*1000 + 1)/(lettercountmap[element]*1000 + totalwordcount)
        reversemapprobvalue[nextindex][index] = (reversemapvalue[nextindex][index]*1000 + 1)/(lettercountmap[element]*1000 + totalwordcount)
        endcountprobmap[element] = (endcountmap[element]*1000 + 1)/(totalwordcount * 1000 + totalwordcount)


#---------------------------------- Weighted FST calculation ---------------------------------------------------------- 


print 'Creating WEIGHTED FST output'

outputstring = "%s%s" % (finalstate,newline)
outputfile3.write(outputstring)
outputfile4.write(outputstring)

lastindex = 0
previousletterindex = 0
endprob = 0.0
token = ''

for wordindex in range(0,len(forwardarray)) :
    for letterindex in range(0,len(forwardarray[wordindex])-1) :
        currentletter = forwardarray[wordindex][letterindex]
        if currentletter in alphabets :
            currentletterindex = alphabets.index(currentletter)
        else :
            currentletterindex = 25
       
##        if letterindex == 0 :
##            transitionprob = firstcountprobmap[currentletter]
##        else :
##            transitionprob = reversemapprobvalue[currentletterindex][previousletterindex]

        token = "".join(forwardarray[wordindex][0:letterindex+1])
        if token in ngramprobmap:
            transitionprob = ngramprobmap[token]
        else :
            transitionprob = 1/(totalwordcount * 1000 + totalwordcount)

        transitionprob = "%s" % (transitionprob)
        previousletterindex = currentletterindex
        
        outputstring = "(%s (%s \"%s\" %s))" % (statearray[wordindex][letterindex],statearray[wordindex][letterindex+1],forwardarray[wordindex][letterindex],transitionprob)
        lastindex += 1
        if outputstring not in outputset2 :
            outputfile3.write(outputstring)
            outputfile3.write(newline)        
            if forwardarray[wordindex][letterindex] in vowels :
                outputstring1 = "(%s (%s \"%s\" %s %s))" % (statearray[wordindex][letterindex],statearray[wordindex][letterindex+1],forwardarray[wordindex][letterindex],epsilon,transitionprob)
            else :
                outputstring1 = "(%s (%s \"%s\" \"%s\" %s))" % (statearray[wordindex][letterindex],statearray[wordindex][letterindex+1],forwardarray[wordindex][letterindex],forwardarray[wordindex][letterindex],transitionprob)
            outputfile4.write(outputstring1)
            outputfile4.write(newline)
        outputset2.add(outputstring)

    if len(forwardarray[wordindex])-1 > (prefixendindex[wordindex]) :    
        endprob = endcountprobmap[alphabets[previousletterindex]]
    else :
        if token in wordcountmap :
            endprob = (wordcountmap[token] *1000 +1)/(totalwordcount*1000 + totalwordcount)
        else :
            endprob = (1)/(totalwordcount*1000 + totalwordcount)        

    #endcountprobmap[alphabets[previousletterindex]]
        
    outputstring = "(%s (%s %s %s))" % (statearray[wordindex][lastindex],statearray[wordindex][lastindex+1],forwardarray[wordindex][lastindex],endprob)
    if outputstring not in outputset2 :
        outputfile3.write(outputstring)
        outputfile3.write(newline)
        outputfile4.write(outputstring)
        outputfile4.write(newline)
    outputset2.add(outputstring)
    lastindex = 0
    previousletterindex = 0

outputstring = "(%s (%s \"%s\" \"%s\"))" % (finalstate,startstate,underscore,definiteprobvalue)
outputfile3.write(outputstring)
outputfile3.write(newline)

outputstring1 = "(%s (%s \"%s\" \"%s\" %s))" % (finalstate,startstate,underscore,underscore,definiteprobvalue)
outputfile4.write(outputstring1)
outputfile4.write(newline)

outputfile3.close()
outputfile4.close()
fileinput.close()

print 'END OF PROCESSING'

print 'Names of output files : english.fsa remove-vowelsq5uncomposed.fst remove-vowelsq6.wfst'


