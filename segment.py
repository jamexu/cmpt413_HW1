#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, codecs, optparse, os, heapq, math
from collections import defaultdict

def opt_parser():
    optparser = optparse.OptionParser()
    optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
    optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
    optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
    (opts, _) = optparser.parse_args()
    return opts

# Imports counts1w file into a Python dictionary using the word as key and count as value
# Also sums the total number of word counts in order to generate probability
class unigram_pdist(object):
    # Create a python dictionary to store unigram counts and keep track of total word counts
    def __init__(self, unigram_file):
        self.counts1w_dist = {}
	self.word_sum = 0
        self.import_unigram(unigram_file)
        
        # an array of punctuation, which will always be its own word
        # TODO: the data files include special quotation marks and periods, add them to the array
        self.punctuation = ['.', ',', '(', ')']

    # Create a python dictionary to store unigram  counts and keep track of total word counts
    def import_unigram(self, input_file):
        for line in open(input_file):
            key = unicode(line.split("\t")[0], 'utf-8')
            value = float(line.split("\t")[1])
            self.counts1w_dist[key] = value
            self.word_sum += value

    def get_probability(self, word):
        if self.counts1w_dist.get(word):
            return (self.counts1w_dist.get(word))/self.word_sum
        # if the string is blank, this should have no effect on the probability
        # (this will occur at the beginning of the line)
        elif word == "":
            return 1
        # if we recognize a word as a punctuation mark, we want it to be a hole word
        elif word in self.punctuation:
            return 1
        # TODO: I do not know what I am doing here, someone who is looking at smoothing should change this
        else:
            return 0.0/(self.word_sum * len(word))


# Class for bigram pdist.  Can it be implemented similarly to unigram?
class bigram_pdist(object):
    def __init__(self, bigram_file):
	self.counts2w_dist = {}
	self.phrase_sum = 0
	self.import_unigram(unigram_file)
	self.punctuation = ['.',',','(',')']
	self.d = defaultdict(int)

    def import_bigram(self,input_file):
	word1 = line.split(" ")[0].strip()
	word2 = line.split(" ")[1].split("\t")[0].strip()
	count = float(line.split(" ")[1].split("\t")[1].strip())
	self.counts2w_dist[key1 + " " + key2] = count
	self.phrase_sum += count
	# d stores the counts of how many phrases had frequency one, two, etc. (for smoothing)
	self.d[count] += 1
        '''
        if parsing bigram file, word1 and word2 seperated by one space, count is separated by a tab
        '''
    def get_probability_bigram(self, word):
	# note: word refers to the two word phrase in bigrams
	#implementing good-turing smoothing to calc probability
        if self.counts2w_dist.get(word):
	    temp_prob = self.counts2w_dist.get(word)
	    rNplusone = self.d.get(temp_prob) + 1
	    if rNplusone == 0
		'''
		need to derive line-of-best-fit equation from self.d and use it to find rNplusone
		'''
            return ((temp_prob + 1)*(rNplusone)/ self.d.get(temp_prob))/self.phrase_sum
        # if the string is blank, this should have no effect on the probability
        # (this will occur at the beginning of the line)
        elif word == "":
            return 1
        # if we recognize a word as a punctuation mark, we want it to be a hole word
        elif word in self.punctuation:
            return 1
        # TODO: I do not know what I am doing here, someone who is looking at smoothing should change this
        else:


for k,v in dict.iteritems():
	print k,v
# will return an array of strings
# representing the segmentation of the input line 
# which maximizes the return value of the function arg_max

# It will fill a L-long 1-dimensional array (where L is the length of line)
# with Memo objects which contain a P value and a pointer to a predecessor
# such that the ith entry will be the best possible P value for a the string from 0 to i
class Memo():

    def __init__(self, value, pred, word):
        self.value = value
        self.pred = pred
        self.word = word

    def get_array(self):
        if self.pred == None:
            return []
        array = self.pred.get_array()
        array.append(self.word)
        return array


def memo_segmenter(line, pdist):
    memos = [None for i in range(len(line) + 1)]
    base = Memo(1, None, "")

    # do the first entries manually
    memos[0] = base
    memos[1] = Memo(pdist.get_probability(line[0]), base, line[0])

    for i in range(2, len(line) + 1):
        best_word = ""
        best_pred = None
        best_value = None
        for j in range(max(0, i - 10), i):
            word = line[j:i]
            pred = memos[j]
            value = arg_max(word, pred, pdist)
            if value > best_value or best_value == None:
                best_word = word
                best_pred = pred
                best_value = value
        memos[i] = Memo(best_value, best_pred, best_word)

    return memos[-1].get_array()


# dummy function to test things out

# the real function should calculate the probability of this segmentation using
# word: a string representing that last word in the current segmentation
# pred: (short for predecessor) an object representing all previous words in this segmentation
#       You can assume that this has already been calculated
#       pred.word is the previous word in the segmentation (use for calculating with bigrams)
#       pred.value is the probability of all previous words in this segmentation
def arg_max(word, pred, pdist):
    # conditional probability: P(a and b) / P(a) for bigrams
    # counts2w_dist[] should give combined prob of a and b 
    # counts1w_dist.get() would give prob of a
    return (pdist.counts2w_dist[pred.word+" "+word])/pdist.counts1w_dist.get(word)

# MAIN FUNCTION STARTS HERE
if __name__ == "__main__":

    # these lines are necessary to pass the chinese characters into stdout (which is how we use score-segment.py)
    old = sys.stdout
    sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)

    # get commandline arguments
    args = opt_parser()
    with open(args.input) as in_file:
        uni_pdist = unigram_pdist(args.counts1w)

        # count is used only for looking at the output of the first few lines
        count = 0

        for line in in_file:
            res = memo_segmenter(unicode(line.strip(), 'utf-8'), uni_pdist)
            print " ".join(res)

            # to have it run through all the lines, comment out the next line
            #count += 1

            # set this number for how many lines you want to print out
            if count >= 6:
                break
       
    # reseting stdout
    sys.stdout = old
'''
    # Execute depending on which segmenter model
    if args.counts1w:
        uni_pdist = unigram_pdist(path)
    elif args.counts2w:
        pass
'''


