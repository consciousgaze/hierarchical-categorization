import json, pickle

def main():
    # extractBranchProducts(2619525011)
    missingPERorSimilar()
    return


def missingPERorSimilar():
    rlt = []
    noPer = open('ItemsWithoutPER.d', 'w')
    i = 0
    j = 0
    t = 0
    noSim = open('ItemsWithoutSimilar.d', 'w')
    with open("amazon_products.d", "r") as f:
    # with open("valid_products.d", "r") as f:
        for l in f:
            t = t+1
            item = json.loads(l.strip('\x01\n'))['Item']
            asin = item['ASIN']
            pers = item['PrunedEditorialReviews']
            per = ''
            if type(pers) != list:
                pers = [pers]
            for p in pers:
                per += p['Content']
            if per.strip() == '':	       
            	noPer.write(str(asin)+'\n')
            else:
            	i+=1
            if 'SimilarProducts' in item:
            	j+=1
            else:
            	noSim.write(str(asin)+'\n')
    noPer.close()
    noSim.close()
    print 'total:', t
    print 'per:', i
    print 'sim:', j



def asinToPath():
	o = open("asinToPath.d", "w")
	with open("valid_products.d") as f:
		for l in f:
			item = json.loads(l)['Item']
			asin = item['ASIN']
			bnl = item['BrowseNodes']['BrowseNode']
			categories = []
			if type(bnl) != list:
				bnl = [bnl]
			for bn in bnl:
				categories += listAncesters(bn)
			cats = ""
			for name, idx in categories:
				cats += str(idx)+";"
			o.write(str(asin)+'\t'+cats+"\n")
	p=o.close()
	return

def formatCatTree(h, fname):
    rlt = {}
    tmph = dict(h)
    nextBatch = [(-1, tmph)]
    while nextBatch != []:
        tmpNextBatch = []
        for p, h in nextBatch:
            currentNode = int(h['BrowseNodeId'])
            if currentNode not in rlt:
            	rlt[currentNode] = {}
            try:
            	rlt[currentNode]['parent'].append(int(p))
            except:
            	rlt[currentNode]['parent'] = [int(p)]

            children = []
            if 'Children' in h:
                print h['BrowseNodeId']
                for i in h['Children']:
                    children.append(int(i['BrowseNodeId']))
                    tmpNextBatch.append((currentNode, i))
            try:
            	rlt[currentNode]['children']+=children
            except:
            	rlt[currentNode]['children']=children
        nextBatch = tmpNextBatch
    pickle.dump(rlt, open(fname, 'wb'))
    return

def extractBrachCates(b):
    f = open('AmazonHeirarchy.json')
    h = json.loads(f.read())
    f.close()

    total = listCates(h[b])

    total = set(total)
    f = open('AppliancesCats.txt', 'w')
    for t in total:
        f.write(t[0].encode('ascii', errors='ignore')+'\t'+t[1]+'\n')
    f.close()


def extractBranchProducts(branch):
    # appliances = []
    # f = open(fileName)
    # for l in f:
    #     tmp = l
    #     l = l.strip().split('\t')
    #     appliances.append((l[1], int(l[0])))
    # f.close()

    f = open('valid_products.d')
    # o = open('ArtCraftSewing.d', 'w')
    o = open('Applicance.d', 'w')
    productCnt = 0
    for l in f:
        product = json.loads(l.strip())
        write = False
        bnl = product['Item']['BrowseNodes']['BrowseNode']
        if type(bnl) != type([]):
            bnl = [bnl]
        for bn in bnl:
            path = listAncesters(bn)
            # print path
            if int(path[-1][1]) == branch:
                # print 'hit!'
                write = True
                productCnt += 1
        if write:
            o.write(l)
            # print 'write!'
        # print
    o.close()
    f.close()
    print productCnt
    # 8670 for Applicance
    return


def validProducts():
    categories = []
    missingcat = []
    f = open('CategoryList.txt', 'r')
    for l in f:
        l = l.strip().split('\t')
        categories.append((l[0], int(l[1])))
    f.close()

    o = open('valid_products', 'w')
    f = open('amazon_products', 'r')
    nonValidCnt = 0
    noBNCnt = 0
    for l in f:
        write = False
        l = l.strip('\x01\n')
        item = json.loads(l)['Item']
        try:
            bns = item['BrowseNodes']
        except:
            noBNCnt+=1
            continue
        bnl = bns['BrowseNode']
        if type(bnl)!=type([]):
            bnl = [bnl]
        for bn in bnl:
            if (bn['Name'].encode('ascii', errors='ignore'), int(bn['BrowseNodeId'])) in categories:
                write = True
                break
            else:
                missingcat.append((bn['Name'], bn['BrowseNodeId']))
        if write:
            o.write(l.decode('utf-8', errors='ignore').encode('ascii', errors='ignore') + '\n')
        else:
            nonValidCnt += 1

    f.close()
    o.close()
    f = open('log.txt', 'w')
    missingcat = set(missingcat)
    for n, i in missingcat:
        f.write(n.encode('ascii', errors='ignore')+'\t'+str(i)+'\n')
    f.close()
    print nonValidCnt, noBNCnt
          # 3043       # 66

def inconsistancy():
    f = codecs.open('CategoryList.txt', 'r', 'utf-8')
    h = []
    for l in f:
        l = l.strip().split('\t')
        h.append((l[0], int(l[1])))
    f.close()
    h = set(h)

    f = codecs.open('ProductCategories.txt', 'r', 'utf-8')
    p = []
    for l in f:
        l = l.strip().split('\t')
        p.append((l[0], int(l[1])))
    f.close()
    p = set(p)

    u = h | p
    print 'Total number:', len(u)
    f = codecs.open('all.txt', 'w', 'utf-8')
    for n, i in u:
        f.write(n+'\t'+str(i)+'\n')
    f.close()

    d = h - (h & p)
    print 'differ number', len(d)
    f = codecs.open('difference.txt', 'w', 'utf-8')
    for n, i in d:
        f.write(n+'\t'+str(i)+'\n')
    f.close()

def listAllProductCates():
    log = open('log.txt', 'w')
    f = open('amazon_products')
    total = []
    for l in f:
        product = json.loads(l.strip('\x01\n'))
        product  = product['Item']
        try:
            bns = product['BrowseNodes']
        except:
            continue
        bnl = bns['BrowseNode']
        if type(bnl) != type([]):
            bnl = [bnl]
        for bn in bnl:
            node = bn['BrowseNodeId']
            name = bn['Name']
            total += [(name, node)]
            total += listAncesters(bn['Ancestors']['BrowseNode'])

    f.close()
    total = set(total)

    f = open('asciiProductCategories.txt', 'w')
    for t in total:
        tmp = t[0]+'\t'+str(t[1])+'\n'
        f.write(tmp.encode('ascii', errors='ignore'))
    f.close()
    return

def listAncesters(p):
    try:
        name = p['Name']
    except:
        name = ''
    try:
        idx = p['BrowseNodeId']
    except:
        idx = -1
    rlt = [(name, idx)]
    if 'Ancestors' not in p:
        return rlt
    if type(p['Ancestors']) != list:
        tmp = [p['Ancestors']]
    else:
        tmp = p['Ancestors']
    for a in tmp:
        rlt += listAncesters(a['BrowseNode'])
    return rlt

def listAllCates():
    f = open('AmazonHeirarchy.json')
    h = json.loads(f.read())
    f.close()

    total = []
    for cat in h:
        total += listCates(cat)

    total = set(total)
    f = open('CategoryList.txt', 'w')
    for t in total:
        f.write(t[0].encode('ascii', errors='ignore')+'\t'+t[1]+'\n')
    f.close()

def listCates(p):
    rlt = [(p['Name'], p['BrowseNodeId'])]
    if 'Children' not in p:
        return rlt
    for c in p['Children']:
        rlt += listCates(c)
    return rlt



if __name__ == '__main__':
    main()
