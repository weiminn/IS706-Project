import os
import json

def recur(step,fimsAll,cochange):
    if step == 0:
        return cochange
    cochangeNext = set()
    for seq in fimsAll:
        isStartNode = False
        for api in seq:
            if api in cochange:
                isStartNode = True
                break
        if not isStartNode:
            continue
        for api in seq:
            # if api == 'int__fdse__org.apache.lucene.util.NumericUtils.BUF_SIZE_LONG':
                # print('a')
            if api not in cochange:
                cochangeNext.add(api)
    cochangeNext2 = recur(step-1,fimsAll,cochangeNext)
    res = set()
    for api in cochangeNext2:
        res.add(api)
    for api in cochangeNext:
        res.add(api)
    for api in cochange:
        res.add(api)
    return res
    

def extend(fimv0,fimsAll,apiV0,apiVx,step):
    cochange1 = []
    for seq in fimv0:
        isStartNode = False
        for api in seq:
            data = api.split('__fdse__')
            if data[-1] == apiV0:
                isStartNode = True
                break
        if not isStartNode:
            continue
        for api in seq:
            data = api.split('__fdse__')
            if data[-1] == apiV0:
                continue
            cochange1.append(api)  
    cochange1 = set(cochange1)
    cochangeFinal = recur(step-1,fimsAll,cochange1)
    isFound = False
    for api in cochangeFinal:
        data = api.split('__fdse__')
        if data[-1] == apiVx:
            isFound = True
            break
    print(len(cochangeFinal))
    return isFound


def run(gaHash,v0,apiV0,apiVx):
    rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate'
    with open(rootPath  + '/2020-data/usage-overview-FIM-21-1-14-filter.json','r') as f:
        j = json.load(f)
    with open(rootPath + '/2020-data/rankedGAVersionAndAPICount-topNiGAVersionPair-21-1-14-filter.json','r') as f:
        rankedGAVersionAndAPICount = json.load(f)['rankedGAVersionAndAPICount']
    
    cnt = 0
    vCandidate = []
    isCandidate = False
    for versionTup in rankedGAVersionAndAPICount[gaHash]:
        version = versionTup[0]
        if version == v0:
            isCandidate = True
        if isCandidate:
            vCandidate.append(version)
    subFIM = j[gaHash]
    fimV0 = j[gaHash][v0]['FIM']
    fimsAll = []
    for v in vCandidate:
        fim = j[gaHash][v]['FIM']
        for seq in fim:
            fimsAll.append(seq)
    step = 2
    flag = extend(fimV0,fimsAll,apiV0,apiVx,step)
    print(flag)

# 测试graph的方法跳几跳能到答案
# 测试recall
gaHash = 'org.elasticsearch__fdse__elasticsearch__fdse__29148e'
v0 = '0.20.6'
apiV0 = 'org.elasticsearch.action.search.SearchRequestBuilder.setFilter(FilterBuilder)'
apiVx = 'org.elasticsearch.action.search.SearchRequestBuilder.setQuery(QueryBuilder)'
run(gaHash,v0,apiV0,apiVx)



