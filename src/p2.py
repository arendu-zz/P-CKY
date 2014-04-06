'''
Created on Apr 7, 2013

@author: arenduchintala
'''
import math,os,json
import itertools
from pprint import pprint

def parse(probabilities, lookup, sentence):
    prob = {}
    backpointer = {}
    pi = {}
    for idx, word in enumerate(sentence):
        j = idx+1
        pi[1,j] = []
        if (lookup.has_key(word)):
            rules = lookup[word]
        else:
            rules = lookup['_RARE_']
        for rule in rules:
            p = probabilities[rule]
            rhs = rule[0]
            #result = (on_false, on_true)[condition]
            if not prob.has_key((1,j,rhs)):
                prob[1,j,rhs] = p
                backpointer[1,j,rhs] =[rhs,word]
                listRHS = pi[1,j] 
                listRHS.append(rhs)
                print str(1),j, 'adding', rhs, '->', rule[1],'from', word
                pi[1,j] = listRHS;
            elif p > prob[1,j,rhs] : 
                prob[1,j,rhs] = p
                backpointer[1,j,rhs] =[rhs,word]
                #update the backpointer also in full version
 
    
    for i in range(2,len(sentence)+1):
        for j in range(1,len(sentence)-i+2):
            pi[i,j] = []
            for k in range(1, i):
                lhs1 = pi[k,j]
                lhs2 = pi[i-k,j+k]
                pairs = list(itertools.product(lhs1,lhs2))
                for pair in pairs:
                    if( lookup.has_key(pair)):
                        #print lookup[pair]
                        for rule in lookup[pair]:
                            rhs = rule[0]
                            p = probabilities[rule] + prob[(k,j,pair[0])] + prob[i-k,j+k,pair[1]]
                            bp = list([rhs,backpointer[(k,j,pair[0])],backpointer[i-k,j+k,pair[1]]])
                            if not prob.has_key((i,j,rhs)):
                                prob[i,j,rhs] = p
                                backpointer[i,j,rhs] = bp
                                listRHS = pi[i,j]
                                listRHS.append(rhs)
                                print i,j, 'adding', rhs, '->', pair[0],',',pair[1],'from', k,j, 'and', int(i-k), int(j+k)
                                print i,j , 'adding bp' , bp
                                pi[i,j] = listRHS
                            if  p > prob[i,j,rhs] : 
                                prob[i,j,rhs] = p
                                backpointer[i,j,rhs] = bp
                                listRHS = pi[i,j]
                                print i,j, 'replacing', rhs, '->', pair[0],',',pair[1],'from', k,j, 'and', int(i-k), int(j+k)
                                print i,j, 'replacing bp', bp
                                pi[i,j] = listRHS
    
    endRHS = filter(lambda x: x in ['S','SBARQ'],pi[len(sentence),1] )
    maxp = float('-inf')
    maxbp = None
    for endrhs in endRHS:
        if prob[len(sentence),1,endrhs] > maxp:
            maxp =  prob[len(sentence),1,endrhs]
            maxbp = backpointer[len(sentence),1,endrhs]
            
    return maxbp

def getCountEstimates(counts):
    nonTerminal = {} 
    rules = {}
    ruleLogProb = {}
    lookup  = {}

    for line in counts:
        items = line.strip().split(' ')
        if items[1] == 'NONTERMINAL':
            if nonTerminal.has_key(items[2]):
                nonTerminal[items[2]]+=int(items[0])
            else:
                nonTerminal[items[2]] = int(items[0])
        elif items[1] == 'UNARYRULE':
            #3 UNARYRULE NOUN musical            
            if rules.has_key((items[2],items[3])):
                rules[(items[2], items[3])] += int(items[0])
            else:
                rules[(items[2], items[3])] = int(items[0])
            if  lookup.has_key(items[3]):
                tups = lookup[items[3]] 
                tups.append((items[2],items[3]))
                lookup[items[3]]  = tups
            else:
                lookup[items[3]]  = [(items[2],items[3])]
            
        elif items[1] == 'BINARYRULE':
            if rules.has_key((items[2],items[3],items[4])):
                rules[(items[2], items[3], items[4])] += int(items[0])
            else:
                rules[(items[2], items[3], items[4])] = int(items[0])
            if lookup.has_key((items[3],items[4])):
                tup = lookup[(items[3],items[4])]
                tup.append((items[2], items[3], items[4]))
            else:
                lookup[(items[3], items[4])] = [(items[2], items[3], items[4])]
    
    for rule,ruleCount in rules.items():
        print rule, ruleCount, '/', nonTerminal[rule[0]]
        ruleLogProb[rule] = math.log(float(ruleCount)/float(nonTerminal[rule[0]]))
    return (ruleLogProb, lookup)

if __name__ == '__main__':
    counts = open('../assignment/parse_train.counts.out','r').read().strip().split(os.linesep)
    (probabilities, lookup) = getCountEstimates(counts)
    #test
    #lines = open('../assignment/parse_test.dat','r').readlines()
    #writer = open('../assignment/parse_test.p2.out','w')
    #dev
    lines = open('../assignment/parse_dev.dat','r').readlines()
    writer = open('../data/dev.out','w')
    for line in lines:
        mbp = parse(probabilities, lookup, line.strip().split(' '))
        writer.write(json.dumps(mbp) +os.linesep);
    writer.flush()
    writer.close()
os.system('python ../assignment/eval_parser.py ../assignment/parse_dev.key ../data/dev.out')