import pickle, time, json, aux
from sklearn.naive_bayes import GaussianNB

def main():
    asinWithPaths('ArtCraftSewing')
    # branchName = 'ArtCraftSewing' #'ArtCraftSewing'#'Applicance'
    # asinWithPaths(branchName)
    # perWithPaths(branchName)
    # import multiNB
    # multiNB.extractCatTree(branchName)
    # samples = multiNB.prepareSamples()
    # for cross_validation in range(10):
    #     trainData = []
    #     testData = []
    #     for i in range(len(samples)):
    #         if i%10==cross_validation:
    #             testData.append(samples[i])
    #         else:
    #             trainData.append(samples[i])
    #     print 'sample prepared'
    #     multiNB.train(trainData, branchName)
    #     print 'training finished'
    #     multiNB.predict(1, testData, branchName)
    #     print 'done'
    #     tree = pickle.load(open(branchName+'tree.p', 'rb'))
    #     analyzeRlt(tree, cross_validation, 'per_clean')
    #     print cross_validation, 'done...\n'
    return


# aux functions
def asinWithPaths(branchName):
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
        path = [-path[0]]+path
        return path
    def formatPaths(paths):
        pathStr = ''
        for path in paths:
            for node in path:
                pathStr += str(node)+'>'
            pathStr += ';'
        return pathStr

    # get asin to nodes hash table
    asinHash = dict()
    f = open('../asinToPath.d')
    for l in f:
        tmp = l.split('\t')
        asinHash[tmp[0]] = tmp[1].split(';')[:-1]
    f.close()

    # f = open('ArtCraftSewing.d')
    f = open(branchName + '.d')
    o = open('per_path.txt', 'w')
    noSimCnt = 0
    totalCnt = 0
    for l in f:
        totalCnt+=1
        tmp = json.loads(l)['Item']
        # per = 'dummy '
        per = ''
        if 'Accessories' in tmp:
            accessories = tmp['Accessories']['Accessory']
            for accessory in accessories:
                try:
                    for acc_cat in asinHash[accessory['ASIN']]:
                        per += 'a_'+acc_cat+' '
                except:
                    pass
        if 'SimilarProducts' in tmp:
            similarities = tmp['SimilarProducts']['SimilarProduct']
            for similarity in similarities:
                try:
                    for sim_cat in asinHash[similarity['ASIN']]:
                        per += 's_'+sim_cat+' '
                except:
                    pass
        else:
            noSimCnt+=1
            print tmp['ASIN']
        paths = []
        bnl = tmp['BrowseNodes']['BrowseNode']
        if type(bnl) != list:
            bnl = [bnl]
        for bn in bnl:
            # extract a path
            path = extractPath(bn)
            if path[-1] in rootNodes:
                paths.append(path)

        line = per +'\t'+formatPaths(paths)+'\n'
        o.write(line.encode('ascii', errors='ignore'))
    f.close()
    o.close()
    print noSimCnt, totalCnt

def analyzeRlt(tree, cross_validation, comm):
    def extractPaths(pathStr):
        import multiNB
        rlt = []
        tmp1 = pathStr.split(';')
        for tmp in tmp1[:-1]:
            path = []
            nodes = tmp.split('>')
            for node in nodes[:-1]:
                path.append(int(node))
            if path[-1] == multiNB.superNode:
                rlt.append(path)
        if len(rlt) == 0:
            print 'miss!'
        return rlt
    totalDist = 0
    totalCnt = 0.0
    depth = 0
    layerCnts = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    corrtCnts = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    actulCnts = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    o = open(comm+'_'+str(cross_validation)+'.txt', 'w')
    f = open('result.txt')
    distLog = open('dist_log.txt', 'w')
    for l in f:
        totalCnt += 1
        predict, actual = l.strip().split('\t')
        predict = extractPaths(predict)[0]
        actual = extractPaths(actual)
        rlts = []
        length = len(predict)
        for path in actual:
            hit = 0
            check = True
            if len(path) > depth:
                depth = len(path)
            for j in range(length):
                i = length - j -1
                if not check:
                    break
                try:
                    if predict[i]==path[i]:
                        hit+=1
                    else:
                        check = False
                except:
                    check = False
            rlts.append((hit, path))
        rlts.sort(reverse = True)

        tmp = rlts[0][1][1:]
        predict = predict[1:]

        tmpdist = aux.pathToPathDist(predict, tmp, tree)
        distLog.write(str(tmpdist)+',')
        totalDist += tmpdist
        right = True
        for j in range(9):
            i = -j-1
            # if right:
            #     try:
            #         if predict[i] != tmp[i]:
            #             if i ==-2:
            #                 print predict
            #                 print tmp
            #                 print
            #             right = False
            #             corrtCnts[i]-=1
            #     except:
            #         pass
            #     corrtCnts[i]+=1
            try:
                predictCur = predict[i]
            except:
                predictCur = None
            try:
                tmpCur = tmp[i]
            except:
                tmpCur = None

            if tmpCur !=None or predictCur !=None:
                layerCnts[i] += 1
                if right:
                    if predictCur == tmpCur:
                        corrtCnts[i]+=1
                    else:
                        right = False
        

    for j in range(9):
        i = 8-j
        try:
            o.write('%.5f' % (corrtCnts[i]*1.0/layerCnts[i])+'\t'+\
                    '%3d' % (corrtCnts[i])+'\t'+\
                    '%3d' % (layerCnts[i])+'\n')
        except:
            pass
    o.write('Average distance: %.5f' % (totalDist/totalCnt))
    f.close()
    o.close()
    print depth, totalDist

def perWithPaths(branchName):
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
        path = [-path[0]]+path
        return path
    def formatPaths(paths):
        pathStr = ''
        for path in paths:
            for node in path:
                pathStr += str(node)+'>'
            pathStr += ';'
        return pathStr
    # f = open('ArtCraftSewing.d')
    f = open(branchName + '.d')
    o = open('per_path.txt', 'w')
    for l in f:
        tmp = json.loads(l)['Item']
        # per = 'dummy '
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
