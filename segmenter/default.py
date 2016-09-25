
import sys, codecs, optparse, os, math, decimal


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
        for j in range(max(0,i-5),i+1):
            characters=[]
            if j==i:
                characters.append(line[i])
            else:
                characters= line[j:i+1]
            combined_word=''
            for r in characters:
                combined_word=combined_word+r[::-1]
            word_arr=[]
            word_arr.append(combined_word)
            if j==0:
                pred=base
            else:
                pred=memos[j-1]
            #value = arg_max(word_arr, pred)
            value =bigram_arg_max(word_arr, pred)
            if value > best_value or best_value == None:
                best_word = combined_word
                best_pred = pred
                best_value = value
        memos[i] = Memo(best_value, best_pred, best_word)

    return memos[-1].get_array()


Pw1  = Pdist(opts.counts1w)
N=sum(Pw1.values())
print N
L=len(Pw1)
Pw2 = Pdist(opts.counts2w)
N2=sum(Pw2.values())
L2=len(Pw2)
print N2




# dummy function to test things out

# the real function should calculate the probability of this segmentation using
# word: a string representing that last word in the current segmentation
# pred: (short for predecessor) an object representing all previous words in this segmentation
#       You can assume that this has already been calculated
#       pred.word is the previous word in the segmentation (use for calculating with bigrams)
#       pred.value is the probability of all previous words in this segmentation

def arg_max(word, pred):
    if pred==None:
        return Jelinek(word)
    if pred.value==1:
        return Jelinek(word)
    else:
        p=pred.value
        return (Jelinek(word)+p)


def bigram_arg_max(word,pred):
    if pred==None:
        return Jelinek(word,pred)
    if pred.value==1:
        return Jelinek(word,pred)
    else:
        arr=[]
        givenword=pred.word
        arr.append(givenword)
        nextword = word[0]
        arr.append(nextword)
        return Jelinek(arr,pred)




# Jelinek_smoothing
# Takes an array of words and recursively calculate the interpolated probability
def Jelinek(arr,pred):

    if len(arr)==1:
        p=math.log10(0.5*float(get_count(arr))/float(N) +0.5*(float(1)/float(N)))
        return math.log10(0.9999999999*float(get_count(arr))/float(N) +0.0000000001*(float(1)/float(N)))

    elif len(arr)==2:
        wi = []
        wi.append(arr[1])
        prob = math.log10(0.9999999999*(float(get_count(arr))/float(N2)/float(pow(10,pred.value)))+0.0000000001*float(pow(10,Jelinek(wi,None))))
        return prob





# finds the count of a word
def get_count(arr):
    if len(arr)==1:
        if arr[0] in Pw1.keys():
            return Pw1.get(arr[0])
        else:
            return 0
    elif len(arr)==2:
        for i in arr:
            bigram=" ".join(arr)
        if bigram in Pw2.keys():
            return Pw2.get(bigram)
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
