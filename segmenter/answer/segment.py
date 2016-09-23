#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, codecs, optparse, os, heapq, math

def opt_parser():
    optparser = optparse.OptionParser()
    optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('../data', 'count_1w.txt'), help="unigram counts")
    optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('../data', 'count_2w.txt'), help="bigram counts")
    optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('../data', 'input'), help="input file to segment")
    (opts, _) = optparser.parse_args()
    return opts

# Imports counts1w file into a Python dictionary using the word as key and count as value
# Also sums the total number of word counts in order to generate probability
class unigram_pdist(object):
    # Create a python dictionary to store unigram counts and keep track of total word counts
    def __init__(self, unigram_counts):
        self.counts1w_dist = {}
        self.word_sum = 0
        self.import_unigram(unigram_counts)

    # Create a python dictionary to store unigram counts and keep track of total word counts
    def import_unigram(self, input_file):
        for line in open(input_file):
            key = unicode(line.split("\t")[0], 'utf-8')
            value = float(line.split("\t")[1])
            self.counts1w_dist[key] = value
            self.word_sum += value



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


def memo_segmenter(line):
    memos = [None for i in range(len(line))]
    base = Memo(1, None, "beginning")

    # do the first entry manually
    memos[0] = Memo(arg_max([line[0]]), base, line[0])

    for i in range(1, len(line)):
        best_word = ""
        best_pred = None
        best_value = None
        for j in range(i):
            word = line[j+1:i+1]
            pred = memos[j]
            value = arg_max(word, pred)
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
def arg_max(word, pred):
    return 1

# MAIN FUNCTION STARTS HERE
if __name__ == "__main__":
    # get commandline arguments
    args = opt_parser()
    # Execute depending on which segmenter model
    if args.counts1w:
        uni_pdist = unigram_pdist(path)
    elif args.counts2w:
        pass


