import os
import json
import requests
from functools import cmp_to_key
from typing import List, Tuple, Dict, Set
import numpy as np
from empiricalData.D5_FISeqUtil import seqIntersection,taintDeletedNode,taintModifiedNode,taintNode2,addFrequency,sortSimiMapBeanSeqList
import time
from empiricalData.D6_Similarity import mapAPIBySimilarity
from empiricalData.DataBean.BeanAPISeq import BeanAPISeq
from empiricalData.DataBean.BeanAPI import BeanAPI
# diff taint 2
# input: version pair, 每个version的usage list
# v1 usage sequence 1 
# v2 usage sequence 2
# v2 usage sequence 1
# v2 usage sequence 2
# v1_v2 = a
# v2_v1 = b
# v1Andv2 = c
# 两两比较
# output: usage sequence mappings
def invokeJavaDiff(topNiGAVersionPair:Dict[str,List[Tuple[str,str]]],frequentUsageSet:Dict[str,Dict[str,List[List[str]]]]):
    # result:Dict[str,Tuple[str,str]] = {}
    finalResult = {}
    initFinalResultData(finalResult)
    cnt = 0
    for ga in topNiGAVersionPair:
        print(ga)
        print(cnt)
        cnt +=1
        for versionPair in topNiGAVersionPair[ga]:
            # if ga != 'org.jetbrains.kotlin__fdse__kotlin-compiler-embeddable__fdse__32e580':
            #     continue
            v1 = versionPair[0]
            v2 = versionPair[1]
            if v1 not in frequentUsageSet[ga] or v2 not in frequentUsageSet[ga]:
                print(ga)
                print(versionPair)
                continue
            v1UsageList = frequentUsageSet[ga][v1]['FIM_fre']
            # ['usage_seq']
            v2UsageList = frequentUsageSet[ga][v2]['FIM_fre']
            # ['usage_seq']
            postedList = set()
            for seq in v1UsageList:
                for ap in seq['usage_seq']:
                    postedList.add(ap)
            for seq in v2UsageList:
                for ap in seq['usage_seq']:
                    postedList.add(ap)
            gas = ga.split("__fdse__")
            if len(postedList) == 0:
                continue
            trimmedList = []
            trimmedList = trimFDSEPrefix(list(postedList))
            print(versionPair)
            diffJson:Dict[str,List[str]] = postToJarDiffServer(gas[0],gas[1],v1,v2,trimmedList)
            if len(diffJson) == 0 or (len(diffJson['added'])==0 and len(diffJson['deleted'])==0 and len(diffJson['modified'])==0):
                # 完全相同的jar包  
                continue
            ####
            splitABCAndMapping(v1UsageList,v2UsageList,ga,v1,v2,diffJson,finalResult,frequentUsageSet[ga])
            # 做完差集再去查询

    return finalResult

def trimFDSEPrefix(apiList:List[str]):
    ret = []
    for api in apiList:
        data = api.split('__fdse__')
        ret.append(data[-1])
    return ret

def splitABCAndMapping(v1UsageList,v2UsageList,ga,v1,v2,diffJson,finalResult,frequentUsageSetGA):
    # 
    c_v1Andv2,a_v1_v2,b_v2_v1 = seqIntersection(v1UsageList,v2UsageList)
    # if len(a_v1_v2) != 0:
        # print(ga + " " + v1 + " "+ v2)
    # modified diffJson['modified']
    c:List[BeanAPISeq]  = taintAllNodes(c_v1Andv2,diffJson,'c')
    # deleted modified diffJson['modified'] diffJson['deleted']
    a:List[BeanAPISeq]  = taintAllNodes(a_v1_v2,diffJson,'a')
    # added modified  
    b:List[BeanAPISeq]  = taintAllNodes(b_v2_v1,diffJson,'b')
    disPatchType(finalResult,c,'c',ga,v1,v2)
    disPatchType(finalResult,a,'a',ga,v1,v2)
    disPatchType(finalResult,b,'b',ga,v1,v2)

    # A deleted api + mapping

    # finalResult['a_only_modified']
    # finalResult['a_has_deleted']
    # BeanAPISeq 增加 frequency
    addFrequencyToSet(a,frequentUsageSetGA[v1],'v1')
    addFrequencyToSet(b,frequentUsageSetGA[v2],'v2')
    # c 有两组
    addFrequencyToSet(c,frequentUsageSetGA[v1],'v1')
    addFrequencyToSet(c,frequentUsageSetGA[v2],'v2')

    versionPairKey = v1 + "__fdse__" + v2
    # deleted modified mapping
    # todo 
    # beanSeqMapping(finalResult,ga,versionPairKey,'a_has_deleted',a,b,c)
    # beanSeqMapping(finalResult,ga,versionPairKey,'a_only_modified',a,b,c)

    # rank
    sortAndRankBeanList(finalResult,ga,versionPairKey,'a_only_modified')
    sortAndRankBeanList(finalResult,ga,versionPairKey,'a_has_deleted')
    sortAndRankBeanList(finalResult,ga,versionPairKey,'a_all_same')
    sortAndRankBeanList(finalResult,ga,versionPairKey,'c_all_same')
    sortAndRankBeanList(finalResult,ga,versionPairKey,'c_modified')

    # 在这里增加FIM的size (v1,v2)，用来算metrics
    key2 = 'total_FIM_size'
    key = 'a_only_modified'
    setFIMSizeValueToFinalResult(finalResult,key,ga,versionPairKey,key2,v1,v2,frequentUsageSetGA)
    key = 'a_has_deleted'
    setFIMSizeValueToFinalResult(finalResult,key,ga,versionPairKey,key2,v1,v2,frequentUsageSetGA)
    key = 'a_all_same'
    setFIMSizeValueToFinalResult(finalResult,key,ga,versionPairKey,key2,v1,v2,frequentUsageSetGA)
    key = 'c_all_same'
    setFIMSizeValueToFinalResult(finalResult,key,ga,versionPairKey,key2,v1,v2,frequentUsageSetGA)
    key = 'c_modified'
    setFIMSizeValueToFinalResult(finalResult,key,ga,versionPairKey,key2,v1,v2,frequentUsageSetGA)

def setFIMSizeValueToFinalResult(finalResult,key,ga,versionPairKey,key2,v1,v2,frequentUsageSetGA):
    if key in finalResult and ga in finalResult[key]:
        if versionPairKey in finalResult[key][ga]:
            finalResult[key][ga][versionPairKey][key2] = (frequentUsageSetGA[v1][key2],frequentUsageSetGA[v2][key2])

def beanSeqMapping(finalResult,ga,versionPairKey,subListKey,a,b,c):
    if ga in finalResult[subListKey] and versionPairKey in finalResult[subListKey][ga]:
        subDict = finalResult[subListKey][ga][versionPairKey]
        mapAAPIContentMapping(subDict,a,c,b,versionPairKey)
    

def sortAndRankBeanList(finalResult,ga,versionPairKey,subListKey):
    if ga in finalResult[subListKey] and versionPairKey in finalResult[subListKey][ga]:
        subDict = finalResult[subListKey][ga][versionPairKey]
        sortUsageBeanAPISeqListById(subDict)
        sortSimiMapBeanSeqList(subDict)


def mycmpId(x:BeanAPISeq,y:BeanAPISeq):
    idA = x.getId()
    idB = y.getId()
    # asc
    if idA < idB:
        return -1
    else:
        return 1

def sortUsageBeanAPISeqListById(m:Dict):
    li = m['usage']
    res = sorted(li,key=cmp_to_key(mycmpId))
    return res

def disPatchType(finalResult,sequence:List[BeanAPISeq],typpe,ga,v1,v2):
    for seq in sequence:
        changeSet = set()
        beanAPIList = seq.getBeanAPIList()
        for beanAPI in beanAPIList:
            if "" != beanAPI.getChangeType():
                changeSet.add(beanAPI.getChangeType())
        if 'a' == typpe:
            if 'deleted' in changeSet:
                addUsageToResult(finalResult['a_has_deleted'],seq,ga,v1,v2)
            elif 'modified' in changeSet:
                addUsageToResult(finalResult['a_only_modified'],seq,ga,v1,v2)
            else:
                addUsageToResult(finalResult['a_all_same'],seq,ga,v1,v2)
        elif 'b' == typpe:
            if 'added' in changeSet:
                addUsageToResult(finalResult['b_has_added'],seq,ga,v1,v2)
            elif 'modified' in changeSet:
                addUsageToResult(finalResult['b_modified'],seq,ga,v1,v2)
            else:
                addUsageToResult(finalResult['b_same'],seq,ga,v1,v2)

        elif 'c' == typpe:
            if 'modified' in changeSet:
                addUsageToResult(finalResult['c_modified'],seq,ga,v1,v2)
            else:
                addUsageToResult(finalResult['c_all_same'],seq,ga,v1,v2)
    
        
def addUsageToResult(finalResultSub,beanAPISeq:BeanAPISeq,ga,v1,v2):
    if ga not in finalResultSub:
        finalResultSub[ga] = {}
    if v1 + "__fdse__" + v2 not in finalResultSub[ga]:
        finalResultSub[ga][v1 + "__fdse__" + v2] = {}
        finalResultSub[ga][v1 + "__fdse__" + v2]['version_pair'] = v1 + "__fdse__" + v2
        finalResultSub[ga][v1 + "__fdse__" + v2]['usage']:List[BeanAPISeq] = []
    finalResultSub[ga][v1 + "__fdse__" + v2]['usage'].append(beanAPISeq)

def initFinalResultData(finalResult):
    finalResult['c_all_same'] = {}
    finalResult['c_modified'] = {}

    finalResult['a_all_same'] = {}
    finalResult['a_only_modified'] = {}
    finalResult['a_has_deleted'] = {}

    finalResult['b_modified'] = {}
    finalResult['b_same'] = {}
    finalResult['b_has_added'] = {}

# type c: modified
# type a: modified,deleted
# type b: modified,added
def taintAllNodes(apiSetList:List[Set[str]],diffJson,typpe)->List[BeanAPISeq]:
    apiSetListTrans:List[BeanAPISeq] = transDataFormat(apiSetList,typpe)
    # deleted added modified
    cnt1 = 0
    cnt2 = 0
    cnt3 = 0
    if len(diffJson["modified"]) != 0:
        cnt1 = taintNode2(apiSetListTrans,diffJson["modified"],"modified")
    if "a" == typpe and len(diffJson["deleted"]) != 0:
        cnt2 = taintNode2(apiSetListTrans,diffJson["deleted"],"deleted")
    if "b" == typpe and len(diffJson["added"]) != 0:
        cnt3 = taintNode2(apiSetListTrans,diffJson["added"],"added")
    
    return apiSetListTrans

def transDataFormat(apiSetList:List[Set[str]],typpe:str)->List[BeanAPISeq]:
    result = []
    for s in apiSetList:
        beanAPISeq = BeanAPISeq(typpe)
        for api in s:
            beanAPI = BeanAPI(api) 
            beanAPISeq.addBeanAPI(beanAPI)
        result.append(beanAPISeq)
    return result

def mapAAPIContentMapping(finalResultSubGAV,v1_v2:List[BeanAPISeq],v1Andv2:List[BeanAPISeq],v2_v1:List[BeanAPISeq],versionPairKey):
    #### deleted/modified API from a -> 找mapping
    dstAll = []
    for beanSeq in v1Andv2:
        dstAll.append(beanSeq)
    for beanSeq in v2_v1:
        dstAll.append(beanSeq)
    simiResult = mapAPIBySimilarity(finalResultSubGAV,dstAll)
    finalResultSubGAV['simi_map'] = simiResult

def addFrequencyToSet(beanAPISeqList:List[BeanAPISeq],frequentUsageSetGAV,v1Orv2):
    FIM_fre_v = frequentUsageSetGAV['FIM_fre']
    # api调用序列节点增加frequency
    # 在这里增加的usage size 用来算support
    total_usage_size = frequentUsageSetGAV['total_usage_size']
    addFrequency(FIM_fre_v,total_usage_size,beanAPISeqList,v1Orv2)

def sortBeanSeqList(seqList:Dict[str,str]):
    sortBeanAPISeqList(seqList)

# jar Diff
# api name, modified/deleted/added
# keys added/deleted/modified/same
def isOverlap(sequence:List[str],diffJson:Dict[str,List[str]]):
    addedAPI = diffJson['added']
    deletedAPI = diffJson['deleted']
    modifiedAPI = diffJson['modified']
    sameAPI = diffJson['same']
    keySet = set()
    for api in sequence:
        for ad in addedAPI:
            if api == ad:
                return True
        for rm in deletedAPI:
            if api == rm:
                return True
        for md in modifiedAPI:
            if api == md:
                return True
    return False


def postToJarDiffServer(groupId,artifactId,v1,v2,apiUsageList:List[str]):
    postStr = {}
    postStr['groupId'] = groupId
    postStr['artifactId'] = artifactId
    postStr['version1'] = v1
    postStr['version2'] = v2
    postStr['usage_array'] = apiUsageList
    req = requests.post('http://10.176.34.86:18123/jardiff',json=postStr)
    content = req.content
    j = json.loads(content)
    return j
