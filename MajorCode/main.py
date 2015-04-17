import pickle, time, json
from sklearn.naive_bayes import GaussianNB

def main():
    # perWithPaths()
    import multiNB
    # multiNB.extractCatTree('all')
    samples = multiNB.prepareSamples()
    trainData = []
    testData = []
    totalNum = len(samples)
    for i in range(totalNum):
        if i%10 == 0:
            testData.append(samples[i])
        else:
            trainData.append(samples[i])
    print 'sample prepared'
    multiNB.train(trainData, 'all')
    print 'training finished'
    multiNB.predict(1, testData, 'all')
    print 'done'
    analyzeRlt()
    return


# aux functions
def extractPaths(pathStr):
    rlt = []
    tmp1 = pathStr.split(';')
    for tmp in tmp1[:-1]:
        path = []
        nodes = tmp.split('>')
        for node in nodes[:-1]:
            path.append(int(node))
        if path[-1] ==0:
            rlt.append(path)
    if len(rlt) == 0:
        print 'miss!'
    return rlt

def analyzeRlt():
    depth = 0
    layerCnts = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    corrtCnts = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    o = open('tmp.txt', 'w')
    f = open('result.txt')
    for l in f:
        predict, actual = l.strip().split('\t')
        predict = extractPaths(predict)[0]
        actual = extractPaths(actual)
        rlts = []
        length = len(predict)
        for path in actual:
            hit = 0
            check = True
            for j in range(length):
                i = length - j -1
                if not check:
                    continue
                try:
                    if predict[i]==path[i]:
                        hit+=1
                    else:
                        check = False
                except:
                    check = False
            rlts.append((float(hit)/length, path))
        rlts.sort(reverse = True)

        tmp = rlts[0][1]
        if len(tmp) > depth:
            depth = len(tmp)
        right = True
        for j in range(9):
            i = -j-1
            if right:
                try:
                    if predict[i] != tmp[i]:
                        right = False
                        corrtCnts[i]-=1
                except:
                    pass
                corrtCnts[i]+=1
            layerCnts[i] += 1
        

    for j in range(9):
        i = 8-j
        o.write(str(corrtCnts[i]*1.0/layerCnts[i])+'\t'+str(corrtCnts[i])+'\t'+str(layerCnts[i])+'\n')
    f.close()
    o.close()

def perWithPaths():
    def extractPath(bn):
        path = []
        while(True):
            path.append(bn['BrowseNodeId'])
            try:
                # if type(bn['Ancestors']) == list:  # Ancestors are always dict
                #     print 'Ouch!!'
                bn = bn['Ancestors']['BrowseNode']
            except:
                break
        return path
    def formatPaths(paths):
        pathStr = ''
        for path in paths:
            for node in path:
                pathStr += str(node)+'>'
            pathStr += ';'
        return pathStr
    f = open('../valid_products.d')
    o = open('per_path.d', 'w')
    for l in f:
        tmp = json.loads(l)['Item']
        per = ''
        pers = tmp['PrunedEditorialReviews']
        if type(pers) != list:
            pers = [pers]
        for p in pers:
            per += ' ' + p['Content']
        paths = []
        bnl = tmp['BrowseNodes']['BrowseNode']
        if type(bnl) != list:
            bnl = [bnl]
        for bn in bnl:
            # extract a path
            path = extractPath(bn)
            if path[-1] in rootNodes:
                path.append(0)
                paths.append(path)

        line = per +'\t'+formatPaths(paths)+'\n'
        o.write(line.encode('ascii', errors='ignore'))
    f.close()
    o.close()


# root nodes
rootNodes = [
2619525011,
2617941011,
15684181,
165796011,
3760911,
283155,
5174,
4991425011,
2625373011,
172282,
16310101,
3760901,
228013,
133140011,
1055398,
2972638011,
599858,
10272111,
2350149011,
11091801,
1064954,
229534,
3375251,
165793011,
468642,
]

# test functions
def depthCnt():
    ctree = pickle.load(open('ApplianceTree.p', 'rb'))
    lvl = [2619525011]
    depth = 0
    f = open('log.txt', 'w')
    while lvl!=[]:
        tmplvl = []
        for node in lvl:
            if ctree[node]['children'] != []:
                f.write(str(node)+'\t')
            for child in ctree[node]['children']:
                tmplvl.append(child)
        f.write('\n')
        print depth
        depth += 1
        lvl = tmplvl

if __name__ == '__main__':
    main()
