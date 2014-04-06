'''
Created on Apr 6, 2013

@author: arenduchintala
'''

import json,os,re

wordCounts = {}
rareWords = []
replacedRareWordTreeStrs = []


def replaceRareLeaves(tree, rareWords):
    stack = []
    stack.append(tree)
    while len(stack) > 0:
        subtree = stack.pop(0)
        if len(subtree) == 3:
            for j in range(1,len(subtree)):
                stack.append(subtree[j])
        else:
            if subtree[1] in rareWords:
                subtree[1] = '_RARE_'

    
def getleaves(tree):
    stack = []
    leaves = []
    stack.append(tree)
    while len(stack) > 0:
        subtree = stack.pop(0)
        if len(subtree) == 3:
            for j in range(1,len(subtree)):
                stack.append(subtree[j])
        else:
            leaves.append(subtree[1])
    return leaves

if __name__ == "__main__":
    trees= open('../assignment/parse_train_vert.dat','r').readlines()
    for treeStr in trees:
        tree = json.loads(treeStr)
        words = getleaves(tree)
        for wrd in  getleaves(tree):
            if wordCounts.has_key(wrd):
                wordCounts[wrd]+=1
            else:
                wordCounts[wrd] =1
    
    for k,v in wordCounts.items():
        if (v < 5):
            rareWords.append(k)
    
    
    for treeStr in trees:
        tree = json.loads(treeStr)
        replaceRareLeaves(tree, rareWords)
        rareTreeStr = json.dumps(tree)
        replacedRareWordTreeStrs.append(rareTreeStr)
    
    rareTreeWriter = open('../data/parse_train_vert.rare','w')
    replacedTrainingTree = '\n'.join(replacedRareWordTreeStrs)
    rareTreeWriter.write(replacedTrainingTree)
    rareTreeWriter.flush()
    rareTreeWriter.close()
    
    '''
    running tree cfg counter
    '''
    os.system('python ../assignment/count_cfg_freq.py ../data/parse_train_vert.rare > ../assignment/parse_train_vert.counts.out')
    
