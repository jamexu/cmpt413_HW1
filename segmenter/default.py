
import sys, codecs, optparse, os, math, decimal
import itertools

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


Pw  = Pdist(opts.counts1w)

N=sum(Pw.values())
L=len(Pw)

# The smoothing is not correctly implemented yet
def log_prob(word_seq_code):
    if word_seq_code in Pw.keys():

        f1=float(0.1+Pw.get(word_seq_code))
        f2=float(0.1*L+N)

        p= math.log10((f1)/(f2))

        return p
    else:
        f2=float(0.1*L+N)
        p = math.log10(0.1/f2)
        return p



#for i in opts.counts1w
#this is just to test if log_prob works
#log_prob(u'\u53bf\u957f')


old = sys.stdout
sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)
# ignoring the dictionary provided in opts.counts


def segment(Dict,break_index,prob_memo): #Dict is dictionary of character sequence in utf-8

    if (len(Dict)==0):
        return 1

    min_id = min (Dict.keys())  # this finds the index of the first character
    max_id = max (Dict.keys())


    #Memoization
    if prob_memo[min_id]<0:
        return prob_memo[min_id]


    #Base cases
    if (len(Dict)==1):
            prob_memo[max_id]=log_prob(Dict[max_id])
            return log_prob(Dict[max_id])


    limit=min(3,len(Dict)) # this sets the word length limit
    prob = -10000
    dict_for_prob={}

    for k in range(0,limit):
        d1={}
        d2={}
        for j in Dict.keys():
            if j<=min_id+k:
                d1[j]=Dict[j]
            else:
                d2[j]=Dict[j]

        # To find the probability of sequence of characters, combine each characters into a word
        word=''
        for r in d1.keys():
            word=word+d1[r][::-1]


        p=log_prob(word)+segment(d2,break_index,prob_memo)
        dict_for_prob[k]=p

        if p>prob:
            prob=p

    a=dict_for_prob[0]
    break_k =0
    for i in dict_for_prob.keys():
        if dict_for_prob[i]>a:
            a=dict_for_prob[i]
            break_k =i
    break_index[min_id+break_k]=-1

    prob_memo[min_id]=prob

    return prob




with open(opts.input) as f:
    for line in f:
        utf8line = unicode(line.strip(), 'utf-8')



        dict ={}    # Dictionary of characters in a line. Keys are the positions of characters
        prob_memo={}  #Dictionary for memoization of segment function. Keys are positions of cahracters
        break_index={} #Dict of initial values 0's. Keys are positions of Characters. Change the value of key i to -1 if character position i and j need to be separated


        j=0
        for i in utf8line:
            dict[j]=i
            prob_memo[j]=0
            break_index[j]=0
            j=j+1


        segment(dict,break_index,prob_memo)

        result=[]
        for i in dict.keys():
            if break_index[i]==-1:
                result.append(dict[i]+" ")
            else:
                result.append(dict[i])

        print "".join(result)

        #output = [i for i in utf8line]  # segmentation is one word per character in the input
        #print " ".join(output)
sys.stdout = old
