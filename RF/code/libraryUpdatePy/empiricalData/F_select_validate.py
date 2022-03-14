import os
from typing import List, Tuple, Dict
import json
import sys
from empiricalData import Common

def filterNullMap(deleted):
    gaVersionCnt = 0
    usageCnt = 0
    simiMapCnt = 0
    gaVersionSet = set()
    newResult = {}
    gaVersion = []
    for ga in deleted:
        for version in deleted[ga]:
            gaVersionCnt +=1
            usage = deleted[ga][version]['usage']
            # simi_map = deleted[ga][version]['simi_map']
            # simi_map2 = []
            # for item in simi_map:
            #     dstSeqMap = item['dst_seq_map']
            #     if not (dstSeqMap == None or len(dstSeqMap) == 0):
            #         simiMapCnt +=1
            #         gaVersionSet.add(ga +"__fdse__" + version)
            #         simi_map2.append(item)
            # deleted[ga][version]['simi_map'] = simi_map2
            # if len(simi_map2) == 0:
            if len(usage)<=0:
                gaVersion.append((ga,version))
            if len(usage)!=0:
                usageCnt += len(usage)
    for gaversion in gaVersion:
        deleted[gaversion[0]].pop(gaversion[1])
    deletedGA = []
    for ga in deleted:
        if len(deleted[ga]) == 0:
            deletedGA.append(ga)
    for ga in deletedGA:
        deleted.pop(ga)

    # print("Usage total: %d(GAV) %d(UsageCnt)" % (gaVersionCnt,usageCnt))     
    # print("Valid Map total: %d(GAV) %d(UsageCnt)" % (len(gaVersionSet),simiMapCnt))     
    return deleted

def saveDistinctDeletedMethods(rootPath,deleted,finalResultDate):
    fexcel = open(Common.FINAL_RESULT_DELETED_EXCEL % finalResultDate,'w')
    cntl = 0
    for ga in deleted:
        for version in deleted[ga]:
            isFirst = True
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
            # deletedMethodsList = list(deletedMethods)
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


def notIn(j,keys):
    tmp = []
    for key in keys:
        tmp.append(key[0])
    for gahash in j:
        if gahash not in tmp:
            print(gahash)
# a_has_deleted 
# a_only_modified 
# a_all_same
#  
# b_has_added 
# b_modified 
# b_same 
#  
# c_modified 
# c_all_same
def generateGroundTruthRaw(finalResultDate):
    rootPath = Common.ROOT_DATA_PATH
    key = 'a_has_deleted'
    with open(Common.FINAL_RESULT % finalResultDate,'r') as f:
        finalResult = json.load(f)
        deleted = finalResult[key]
    # deletedFilteredResult = filterNullMap(deleted)
    # excel GA:35
    # TH 10, GA:38 需要补3个
    print(len(deleted))
    saveDistinctDeletedMethods(rootPath,deleted,finalResultDate)
    # with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/verification/deleted_result-3-15.json','r') as f:
    #     j2 = json.load(f)
    # print(len(j2))
    # print('a')
    # bdeletedFilteredResult = filterNullMap(bdeleted)
    # 这个调用用来整理 ground truth
    # for key in filteredResult:
    #     a = key.split('__fdse__')
    #     print(a[0] + '__fdse__' + a[1])
    # newFile = Common.FINAL_RESULT_A_DELETED % (key,finalResultDate)
    # with open(newFile,'w') as f:
    #     json.dump(deletedFilteredResult,f,indent=4)


# getSubsetOfFinalResult()
        

def query(s):
    data = s.split('__fdse__')
    groupId = data[0]
    artifactId = data[1]
    # version = v
    rootPath = Common.ROOT_DATA_PATH

    with open(rootPath + 'usage-db-21-1-14.json','r') as f:
        usageDb:Dict[str,Dict[str,Dict[str,Dict[str,List[Tuple[str,List[str]]]]]]]  = json.load(f)
    # with open(rootPath + 'usage-overview-21-1-14-filter.json','r') as f:
    #     usage:Dict[str,Dict[str,List[List[str]]]]  = json.load(f)
    with open(rootPath + 'usage-overview-FIM-21-1-25-filter.json','r') as f:
        usageFIM:Dict[str,Dict[str,Dict[str,List[List[str]]]]] = json.load(f)
    # for i in usage:
    #     print(i)
    # usageData = usage[s]

    usageFIMData = usageFIM[s]
    usageDbData = []
    for projectFile in usageDb:
        for fileName in usageDb[projectFile]:
            for jarName in usageDb[projectFile][fileName]:
                if s in jarName:
                    spot =  usageDb[projectFile][fileName][jarName]
                    newSpot = {}
                    for methodName in spot:
                        spotEntry = {}
                        invocationList = spot[methodName]
                        spotEntry['project'] = projectFile 
                        spotEntry['fileName'] = fileName
                        spotEntry['jar_name'] = jarName
                        spotEntry['metohd_call'] = (methodName,invocationList)
                        newSpot[methodName] = spotEntry

                    usageDbData.append(newSpot)

    with open(rootPath + '/temp-db-usage-21-1-25.json','w') as f:
        json.dump(usageDbData,f,indent=4)
    # with open(rootPath +  '/temp-usage-21-1-14.json','w') as f:
    #     json.dump(usageData,f,indent=4)
    with open(rootPath + '/temp-usage-FIM-21-1-25.json','w') as f:
        json.dump(usageFIMData,f,indent=4)
    

# args  = sys.argv
# if len(args) ==2:
#     # query("com.google.guava__fdse__guava__fdse__a1e0af")
#     query(args[-1])
# query("org.json__fdse__json__fdse__3d7bbb")

# /home/hadoop/dfs/data/Workspace/LibraryUpdate/projects_extra/85_3000/repository
# /home/hadoop/dfs/data/Workspace/projects_9_19/projects_git

