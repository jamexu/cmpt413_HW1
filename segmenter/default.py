
import sys, codecs, optparse, os, math, decimal, numpy


optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()

class Pdist(dict):
    "A probability distribution estimated from counts in datafile."

    def __init__(self, filename, sep='\t', N=None, missingfn=None):
        self.maxlen = 0
        for line in file(filename):
            (key, freq) = line.split(sep)
            try:
                utf8key = unicode(key, 'utf-8')
            except:
                raise ValueError("Unexpected error %s" % (sys.exc_info()[0]))
            self[utf8key] = self.get(utf8key, 0) + int(freq)
            self.maxlen = max(len(utf8key), self.maxlen)
        self.N = float(N or sum(self.itervalues()))
        self.missingfn = missingfn or (lambda k, N: 1./N)

    def __call__(self, key):
        if key in self: return float(self[key])/float(self.N)
        #else: return self.missingfn(key, self.N)
        elif len(key) == 1: return self.missingfn(key, self.N)
        else: return None

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
    base = Memo(1, None, "")

    # do the first entry manually
    memos[0] = Memo(bigram_arg_max([line[0]],None), base, line[0])

    for i in range(1, len(line)):
        best_word = ""
        best_pred = None
        best_value = None
        for j in range(max(0,i-2),i+1):
            characters=[]
            if j==i:
                characters.append(line[i])
            else:
                characters= line[j:i+1]

            combined_word=''
            for r in characters:
                combined_word=combined_word+r

            if j==0:
                pred=base
            else:
                pred=memos[j-1]
            #value = arg_max(word_arr, pred)
            #value =bigram_arg_max(word_arr, pred)
            value =bigram_arg_max(combined_word, pred)
            if value > best_value or best_value == None:
                best_word = combined_word
                best_pred = pred
                best_value = value
        memos[i] = Memo(best_value, best_pred, best_word)

    return memos[-1].get_array()


Pw1  = Pdist(opts.counts1w)
N=sum(Pw1.values())
L=len(Pw1)
Pw2 = Pdist(opts.counts2w)
N2=sum(Pw2.values())
L2=len(Pw2)





# dummy function to test things out

# the real function should calculate the probability of this segmentation using
# word: a string representing that last word in the current segmentation
# pred: (short for predecessor) an object representing all previous words in this segmentation
#       You can assume that this has already been calculated
#       pred.word is the previous word in the segmentation (use for calculating with bigrams)
#       pred.value is the probability of all previous words in this segmentation


def bigram_arg_max(word,pred):
    if pred==None:
        return float(Bigram_Jelinek(word,None))
    if pred.value==1:
        return float(Bigram_Jelinek(word,None))
    else:
        arr=[]
        givenword=pred.word
        arr.append(givenword)
        nextword = word
        arr.append(nextword)
        return Bigram_Jelinek(word,pred)+pred.value



# Jelinek_smoothing
# Takes an array of words and recursively calculate the interpolated probability

def Bigram_Jelinek(word,pred):

    unigram_count=float(get_uni_count(word))
    unigram_prob= float(0.999999999)*unigram_count/float(N) +float(0.0000000001)*(float(1)/float(N))
    if pred==None:
        return math.log(unigram_prob,2)

    bigram_count=float(get_bi_count(word,pred))
    unigram_log_prob= math.log(unigram_prob,2)
    if bigram_count!=0:
        bigram_prob=math.log(float(bigram_count)/float(N2),2)-pred.value
        return numpy.logaddexp2(math.log(0.7,2)+bigram_prob,math.log(0.3,2)+unigram_log_prob)
    else:
        return math.log(float(0.3)*unigram_prob,2)


def get_bi_count(word,pred):
    bigram=pred.word+unicode(" ",'utf-8')+word
    if bigram in Pw2:
        #print "/n"+"Found"+"/n"
        return Pw2.get(bigram)
    else:
        return 0


def get_uni_count(word):
    if word in Pw1:
        return Pw1.get(word)
    else:
        return 0





old = sys.stdout
sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)
# ignoring the dictionary provided in opts.counts
with open(opts.input) as f:
    for line in f:
        utf8line = unicode(line.strip(), 'utf-8')
        output = [i for i in utf8line]  # segmentation is one word per character in the input
        result= memo_segmenter(output)
        print " ".join(result)

        #print " ".join(output)
sys.stdout = old
