#!/usr/bin/env python

import sys
import itertools

try:
    _, testfilename, goldfilename = sys.argv
except:
    sys.stderr.write("usage: evalb.py <test-file> <gold-file>\n")
    sys.exit(1)

m = n = 0
for testline, goldline in itertools.izip(open(testfilename), open(goldfilename)):
    for testtok, goldtok in itertools.izip(testline.split(), goldline.split()):
        testword, testtag = testtok.rsplit('_', 1)
        goldword, goldtag = goldtok.rsplit('_', 1)
        if testword.lower() != goldword.lower():
	    print testword.lower()
            sys.stderr.write("error: words do not match\n")
            sys.exit(1)
        n += 1
        if testtag == goldtag:
            m += 1
	else :
		print testtok,goldtok

print "total words:  ", n
print "correct tags: ", m
print "accuracy:     ", float(m)/n
