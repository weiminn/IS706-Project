import os

import json

def top200():
    # path ='/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-data/usage-count-21-3-23-top200-all.json'
    path ='/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-28/'
    file = 'usage-count-21-3-27-filterUsage10-all.json'
    path = path + file
    with open(path,'r') as f:
        j = json.load(f)
        print(len(j))
top200()

# 去除了GAV = 1的
def okToDiff():
    # path ='/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-data/topNiGAVersionPair-21-3-23-top200.json'
    path ='/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-28/topNiGAVersionPair-21-3-27-filterUsage10.json'
    with open(path,'r') as f:
        j = json.load(f)
        print(len(j))
# okToDiff()

# 比较的API与Usage交叉，有交集的
def diffHaveDeletedMethod():
    # path ='/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-data/usage_final_result-21-3-23-top200.json'
    path ='/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-28/usage_final_result-21-3-27-filterUsage10.json'
    with open(path,'r') as f:
        j = json.load(f)
        print(len(j['a_has_deleted']))
    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-28/GA-usage-have-deleted-API.json','w') as f:
        json.dump(j['a_has_deleted'],f,indent = 4)
    # 49 个 GA

# diffHaveDeletedMethod()

def saveDistinctDeletedMethods(rootPath,deleted,finalResultDate):
    fexcel = open(rootPath + '/deleted-method-%s.csv' % finalResultDate,'w')
    cntl = 0
    for ga in deleted:
        for version in deleted[ga]:
            isFirst = True
            deletedMethodsMap = deleted[ga][version]
            for method in deletedMethodsMap:
                if isFirst:
                    prefix = ga +"," + version + ","
                    isFirst = False
                else:
                    prefix =  ","  +  ","
                fexcel.write(prefix + method + ', '+ str(deletedMethodsMap[method]) +"\n" )
                cntl +=1
    fexcel.close()
    print(cntl)

def gasHaveDeletedAPI():
    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-28/GA-usage-have-deleted-API.json','r') as f:
        deleted = json.load(f)
    rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-28'
    saveDistinctDeletedMethods(rootPath,deleted,'21-3-23')

# gasHaveDeletedAPI()
def trans(deleted):
    result = {}
    for ga in deleted:
        for version in deleted[ga]:
            usage = deleted[ga][version]['usage']
            deletedMethodsMap = {}
            for item in usage:
                beanAPISeqList = item['apiSeq']
                fv1 = item['frequencyV1']
                for beanAPI in beanAPISeqList:
                    if beanAPI['changeType'] == 'deleted':
                        if beanAPI['api'] not in deletedMethodsMap:
                            deletedMethodsMap[beanAPI['api']] = 0
                        deletedMethodsMap[beanAPI['api']] += fv1
            if ga not in result:
                result[ga] = {}
            result[ga][version] = deletedMethodsMap
    return result

# 需要增量加的excel数据
def transDeletedJson():
    rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-28'
    with open(rootPath + '/GA-usage-have-deleted-API.json','r') as f:
        deleted = json.load(f)
    simpleDeletedDict = trans(deleted)
    with open(rootPath + '/Simple-GA-have-deleted-API.json','w') as f:
        json.dump(simpleDeletedDict,f,indent=4)
            

# transDeletedJson()

def diffExcel():
    rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-28'
    with open(rootPath + '/deleted_result-3-15.json','r') as f:
        original = json.load(f)
    with open(rootPath + '/Simple-GA-have-deleted-API.json','r') as f:
        newGAs = json.load(f)
    cnt = 0
    apiCnt = 0
    newGaDict = {}
    for ga in newGAs:
        if ga not in original:
            cnt +=1
            for vPair in newGAs[ga]:
                apiCnt += len(newGAs[ga][vPair])
            newGaDict[ga] = newGAs[ga]
    for ga in original:
        if ga not in newGAs:
            print('deletion from old: '+ ga)
    print("New GA: "+ str(cnt))
    print("New API: "+ str(apiCnt))
    saveDistinctDeletedMethods(rootPath,newGaDict,'21-3-28-append')

# diffExcel()
# deletion from old: org.apache.tomcat.embed__fdse__tomcat-embed-core__fdse__aba6c6
# deletion from old: com.squareup__fdse__protoparser__fdse__7b70df
# deletion from old: org.jmock__fdse__jmock__fdse__a76d7b
# deletion from old: com.yammer.metrics__fdse__metrics-core__fdse__16c1ec
# deletion from old: org.zeroturnaround__fdse__zt-exec__fdse__3ee488
# deletion from old: com.tencent.angel__fdse__angel-ps-mllib__fdse__32aac1


