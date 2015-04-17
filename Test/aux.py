

def nodeToPathDist(node, path, tree):
    '''
        Computes the distance from a node to a path.
        The total distance is: (shortest steps to get to the path)*2
                               + distance from the intersection node to the end
    '''

    current = [node]
    dist = 0
    while current != []:
        nextCurrent = []
        hit = False
        hitNode = None
        for n in current:
            if n in path:
                hit = True
                hitNode = n
                break
            nextCurrent += tree[n]['parents']
            # nextCurrent += tree[n]['children'] # TODO: is it proper to include children?
        if hit:
            nextCurrent = []
        else:
            dist+=1
        current = nextCurrent
    dist *= 2
    dist += path.index(hitNode)
    return dist

def pathToPathDist(path_predicted, path_actual, tree):
    '''
        Returns the distance of two pathes.
        The distance is defined as following:
            for each modificaiton made for the path_predicted to become path_actual
            the distance from the node to be modified to the path_actual will be added
            to the path distance
    '''
    dist = 0
    length = max(len(path_predicted), len(path_actual))
    actualL = len(path_actual)
    for i in range(length):
        try:
            p = path_predicted[i]
            try:
                if p == path_actual[i]:
                    p = None
            except:
                pass 
        except:
            p = path_actual[i]
        if p!=None:
            dist += nodeToPathDist(p, path_actual, tree)
    return dist
