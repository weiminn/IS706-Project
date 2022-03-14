import os
import json
from typing import List, Tuple, Dict, Set

def isContainV1(lines):
    gt = [
        "newInputStreamSupplier",
        "newInputStreamSupplier",
        "newReaderSupplier",
        "newOutputStreamSupplier",
        "newInputStreamSupplier",
        "setThreadPool",
        "setSoftMinEvictableIdleTimeMillis",
        "setMinEvictableIdleTimeMillis",
        "setMaxIdle",
        "setTimeBetweenEvictionRunsMillis",
        "setNumTestsPerEvictionRun",
        "setTestWhileIdle",
        "setTestOnBorrow",
        "setMaxActive",
        "setMaxWait",
        "setTestOnReturn",
        "setWhenExhaustedAction",
        "setMinIdle",
        "socketAddress",
        "build",
        "trustManager",
        "forClient",
        "put",
        "addAccept",
        "iterator",
        "getDocument",
        "floatToPrefixCoded",
        "doubleToPrefixCoded",
        "maxDoc",
        "setIntValue",
        "setLongValue",
        "setDoubleValue",
        "setFloatValue",
        "getFieldable",
        "size",
        "get",
        "setFilter",
        "hits",
        "failed",
        "lat",
        "distance",
        "gte",
        "bottomRight",
        "gt",
        "settingsBuilder",
        "topLeft",
        "setIgnoreConflicts",
        "lt",
        "add",
        "add",
        "lte",
        "lon",
        "getType",
        "getId",
        "nodeBuilder",
        "settings",
        "isCreated",
        "getIndex",
        "getIndex",
        "isFound",
        "getType",
        "setExtraSource",
        "getId",
        "setRefresh",
        "settingsBuilder",
        "hits",
        "nodeBuilder",
        "loadConfigSettings",
        "settings",
        "admin",
        "setFilter",
        "order",
        "failed",
        "settingsBuilder"]
    res = []
    for line in lines:
        isIn = False
        for g in gt:
            if g in line:
                isIn = True
                break
        if isIn:
            res.append(line)
    return res

def isContainV2(lines):
    gt = [
        "asByteSource",
        "wrap ",
        "asCharSource",
        "Server",
        "setMaxTotal",
        "setMaxIdle",
        "newClientContext",
        "newClientContext",
        "TopScoreDocCollector",
        "TopDocs",
        "floatToSortableInt",
        "doubleToSortableLong",
        "NumericDocValuesField",
        "getField",
        "select",
        "getHits",
        "hits",
        "isFailed",
        "lat",
        "distance",
        "gte",
        "bottomRight",
        "gt",
        "builder",
        "topLeft",
        "lt",
        "lte",
        "lon",
        "status",
        "builder",
        "getHits",
        "Node",
        "setQuery",
        "isFailed",
        "builder"
    ]

    res = []
    for line in lines:
        isIn = False
        for g in gt:
            if g in line:
                isIn = True
                break
        if isIn:
            res.append(line)
    return res




def run():
    path = '/home/hadoop/dfs/data/Workspace/ws/fileDiffFinalResult.json'
    with open(path,'r') as f:
        j:List[str] = json.load(f)
    cnt = 0
    #        list
    res = []
    for d in j:
        # d: Dict
        # 
        projectName = d['projectName']
        # List
        print(projectName)
        codeChanges:List[str] = d['codeChanges']
        # 
        newnewDict = {}
        newList = []
        for entry in codeChanges:
            # print(entry)
            changedCodes:Dict[str] =  entry[projectName]['changedCodes']
            parentCommit = entry[projectName]['parentCommitId']
            currCommitId = entry[projectName]['currCommitId']
            newParentDict = {}
            newDict = {}
            for file in changedCodes:
                added:List[str] = changedCodes[file]['added']
                deleted:List[str] = changedCodes[file]['deleted']
                v1 = isContainV1(deleted)
                v2 = isContainV2(added)
                if len(v1) !=0 and len(v2) !=0:
                    data = {}
                    data['added'] = v1
                    data['deleted'] = v2
                    newDict[file] = data
            newParentDict['currCommitId'] = currCommitId
            newParentDict['parentCommitId'] = parentCommit
            newParentDict['changedCodes'] = newDict
            newList.append(newParentDict)
        newnewDict['projectName'] = projectName
        newnewDict['codeChanges'] = newList
        res.append(newnewDict)
    path2 = '/home/hadoop/dfs/data/Workspace/ws/fileDiffFinalResult-gt-filter.json'
    with open(path2,'w') as f:
        json.dump(res,f,indent=4)


run()