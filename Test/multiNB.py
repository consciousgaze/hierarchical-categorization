import pickle, time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
superNode = 2617941011

def extractPaths(pathStr):
    rlt = []
    tmp1 = pathStr.split(';')
    for tmp in tmp1[:-1]:
        path = []
        nodes = tmp.split('>')
        for node in nodes[:-1]:
            path.append(int(node))
        if path[-1] == superNode:
            rlt.append(path)
    if len(rlt) == 0:
        print 'miss!'
    return rlt

def extractCatTree(branchName):
    '''
        requires a txt file where the actual paths of each product is specified
    '''
    catTree = {}
    f = open('per_path.txt')
    for l in f:
        try:
            catLists = l.strip().split('\t')[1]
        except:
            continue
        paths = extractPaths(catLists)
        for path in paths:
            for i in range(len(path)):
                node = path[i]
                if node not in catTree:
                    catTree[node] = {'children':[], 'parents':[]}
                if i != 0:
                        catTree[node]['children'].append(path[i-1])
                if i!=len(path)-1:
                        catTree[node]['parents'].append(path[i+1])
    for node in catTree:
        tmp = {'parents':list(set(catTree[node]['parents'])),
               'children':list(set(catTree[node]['children']))}
        catTree[node] = tmp
        
    pickle.dump(catTree, open(branchName+'Tree.p', 'wb'))


def prepareSamples():
    samples = []
    f = open('per_path.txt')
    for l in f:
        tmp = l.strip().split('\t')
        content = tmp[0]
        try:
            paths = extractPaths(tmp[1])
        except:
            continue
        samples.append((content, paths))
    f.close()
    return samples

def train(samples, branchName):
    '''
        requires a htree which is a dictionary of nodes that 
        specifies each node's children and parents
    '''

    htree = pickle.load(open(branchName+'Tree.p', 'rb'))
    totalNodes = []
    clfs = dict()

    emptyNodeCnt = 0
    nonLeafNodeCnt = 0
    for node in htree:
        X = []
        y = []
        for content, paths in samples:
            for path in paths:
                totalNodes += path
                try:
                    idx = path.index(node)
                    if idx == 0:
                        raise 'Hit Node!'
                    else:
                        X.append(content)
                        y.append(path[idx-1])
                except:
                    pass
        if htree[node]['children']!=[]:
            nonLeafNodeCnt += 1
            if len(X) == 0:
                emptyNodeCnt += 1
                # print node, 0, 0
        if len(X) > 0:
            if len(X) != len(y):
                print "weird!!"
            clfs[node] =  Pipeline([('vect', CountVectorizer()),
                                    ('tfidf', TfidfTransformer()),
                                    ('clf', MultinomialNB())])
            clfs[node].fit(X, y)
            # print node, len(X), len(y)
    totalNodes = set(totalNodes)
    print 'there are %d nodes appeard in the samples.' % len(totalNodes)
    print 'Among all the %d non-leaf nodes in the hierarchical tree, %d nodes are empty.' % (nonLeafNodeCnt, emptyNodeCnt)
    pickle.dump(clfs, open(branchName+'CLFs.p', 'wb'))

    return

def predict(K, test, branchName):
    def formatPath(path):
        pathStr = ''
        for node in path:
            pathStr+=str(node)+'>'
        return pathStr
    # kbeam search
    '''
        requires a htree which is a dictionary specifies each
        node's children and parents
        requires a classifier dictionary
        state for each sample: {candidate paths:score}
        upon updating: expand each candidate path, trim
    '''
    # initialize
    htree = pickle.load(open(branchName+'Tree.p', 'rb'))
    pending = dict()
    samples = dict() # state of each sample is stored in a dict
    idx = 0
    for content, paths in test:
        # each sample is stored as content, K-paths with their score, expanded paths
        samples[idx] =[None, [(1, [superNode])], []]
        try:
            pending[superNode].append(idx)
        except:
            pending[superNode]=[idx]
        idx += 1
    clfs = pickle.load(open(branchName+'CLFs.p', 'rb'))


    currentLayer = [superNode]
    while currentLayer != []:
        nextLayer = []
        for node in currentLayer:
            if node not in clfs: # reaches an end
                # print 'skip', node
                continue
            # gather X
            X = []
            for idx in pending[node]:
                X.append(test[idx][0])
            # predict
            rlts = clfs[node].predict_log_proba(X)
            # expand
            classes = clfs[node].steps[-1][1].classes_
            sampleCnt = 0
            for idx in pending[node]:
                for path in samples[idx][1]:
                    if path[1][0] == node:
                        for clsIdx in range(len(classes)):
                            samples[idx][2].append((path[0]+rlts[sampleCnt][clsIdx],
                                                  [classes[clsIdx]]+path[1]))
                sampleCnt += 1
            # clear pending node
            pending[node] = []
        # trim each sample
        for idx in samples:
            if len(samples[idx][2]) == 0:
                continue
            tmp = list(sorted(samples[idx][2], reverse=True))
            samples[idx][1] = tmp[:K+1]
            for score, path in samples[idx][1]:
                try:
                    pending[path[0]].append(idx) # prepar pending node
                except:
                    pending[path[0]]=[idx]
                nextLayer.append(path[0]) # prepare next layer
            samples[idx][2] = []
        # goto next layer
        currentLayer = list(set(nextLayer))
        # print currentLayer

    f = open('result.txt', 'w')
    for idx in samples:
        path = sorted(samples[idx][1])[-1][1]
        actual = ''
        for p in test[idx][1]:
            actual += formatPath(p)+';'
        f.write(formatPath(path)+';\t'+actual+'\n')
    f.close()
    return






