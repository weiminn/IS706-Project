import os
import json
from functools import cmp_to_key
from typing import List, Tuple, Dict
from packaging import version
import random
from empiricalData import F_filtered_jar

from empiricalData.DataBean.RankedDependencyUsage import RankedDependencyUsage
from empiricalData.DataBean.RankedDependencyUsage import GAVUsage
from empiricalData.DataBean.APIUsageDB import APIUsageDB
from empiricalData.F2_appendVersionPair import appendVersionPair,appendVersionPairFromJson
from empiricalData.DataBean.DependencyDB import DependencyDB
# public
# input: depdb, usagedb
# output: top n ga's m usage version
# outputformat: dict: ga->list<version>

def topUsageSelection(depDb:Dict[str,List[str]] ,usageDb:Dict[str,Dict[str,Dict[str,Dict[str,List[Tuple[str,List[str]]]]]]],n:int,m:int):
    pass
    # # rank version 的usage 数量
    # #                 gaHash      version,number
    # # 选择合适的ga
    # gaVersionMap:Dict[str,List[Tuple[str,int]]] = rerankDepDb(depDb)
    #
    # # 按照version使用的数量，rank GA
    # rankedGAVersionMapList:List[Tuple[str,List[Tuple[str,int]]]] = rerankGA(gaVersionMap)
    # # 过滤junit等
    # rankedGAVersionMapList = filterUnwantedGA(rankedGAVersionMapList)
    #
    # if n <= len(rankedGAVersionMapList):
    #     rankedGAVersionMapList = rankedGAVersionMapList[0:n]
    # # ==================
    # # top 100 GA
    # ### 过滤一部分version
    # rankedGAVersionMapListTopVersion = {}
    # for entry in rankedGAVersionMapList:
    #     versionList = entry[1]
    #     jarName = entry[0]
    #     if m <= len(versionList):
    #         rankedGAVersionMapListTopVersion[jarName] = versionList[0:m]
    #     else:
    #         rankedGAVersionMapListTopVersion[jarName] = versionList
    # # 过滤 end
    # # 统计usage 数量，按照API usage过滤一部分
    # #                    ga    version usageCnt
    # gavUsageCount:Dict[str,Dict[str,int]] = countAPIUsageNumber(usageDb)
    # #  按照ga使用频次，得到对应的usage的count
    # #                            gaHash      version,depNum,apiNum
    # rankedGaVersionWithUsage:Dict[str,List[Tuple[str,int,int]]]= gavUsageCountRankByRankedGa(gavUsageCount,rankedGAVersionMapListTopVersion)
    # return rankedGaVersionWithUsage
def notIn(j,keys):
    tmp = []
    for key in keys:
        tmp.append(key[0])
    for gahash in j:
        if gahash not in tmp:
            print(gahash)

def topUsageSelection2(depDb: DependencyDB ,usageDb:APIUsageDB):

    # ########################
    # rank version 的usage 数量
    # dependency 的数量
    #                 gaHash      version,number
    depVersionCount:Dict[str,Dict[str,int]] = depDb.depByLibVersionUsageDesc()
    print("gaHash dep: %d" % len(depVersionCount))
    # 统计usage 数量，按照API usage过滤一部分
    #                            ga    version usageCnt
    apiUsageVersionCount:Dict[str,Dict[str,int]] =  usageDb.countAPIUsageNumber()
    # merge dep + api 
    #  这一步过滤了没有api usage的ga version
    mergedUsage: RankedDependencyUsage = mergeDepAPIUsage(depVersionCount,apiUsageVersionCount)
    print("merge num: %d" % len(mergedUsage.usage))
    # filterUnwantedGA(mergedUsage)
    res:List[Tuple[str,List[GAVUsage]]] = mergedUsage.rankByAPIUsageNumber()
    # notIn(j2,tempRes)
    # 过滤了低usage的情况
    th =10
    res2:List[Tuple[str,List[GAVUsage]]] = mergedUsage.filterLowAPIUsage(res,th)
    print("filter %d: %d" % (th,len(res2)))
    return res2,res

      

#
# public
# 
# input: top n,m usage version
# output: top n usage pair 
# Dict[gahash,List[Tuple[v0,v1]]]
def topUsagePairSelection(rankedGAVersionAndAPICount:List[Tuple[str,List[GAVUsage]]]):

    # 去除为0 的调用
    result:Dict[str,List[Tuple[str,str]]] = {}
    usageLt1Cnt = 0
    print('top selection raw: '+ str(len(rankedGAVersionAndAPICount)))
    top200Cnt = 0
    top200LibraryUsageVersion = 0
    for tup in rankedGAVersionAndAPICount:
        gaHash = tup[0]
        gavUsageList = tup[1]
        if len(gavUsageList)<=1:
            usageLt1Cnt +=1
            continue
        newGavUsageList =  sorted(gavUsageList, key=cmp_to_key(mycmpVersionTup))
        top200LibraryUsageVersion +=len(newGavUsageList)
        # select pair
        versionPairList:List[Tuple[str,str]] = genVersionDiffPair(newGavUsageList)
        if versionPairList != None:
            result[gaHash] = versionPairList
        # select pair 2
        # versionPairList:List[Tuple[str,str]] = genVersionDiffPairByMajorMinorPath(newGavUsageList)
        # if versionPairList != None:
        #     top200Cnt+=1
        #     result[gaHash] = versionPairList
        #     if top200Cnt == 200:
        #         break
    print('top200 usage version:%d' %top200LibraryUsageVersion)
    print("Version<=1: %d" % usageLt1Cnt)
    print('top remove gav usage<=1: '+ str(len(result)))
    # manually append
    # appendVersionPair(result)
    # appendVersionPairFromJson(result)
    return result


# public
# 拿到对应gav的usage sequence 列表

# project ->file -> jarName -> method -> api usage sequence
def getCorrespondingGAVUsage(g,a,v,apiUsageDB:Dict[str,Dict[str,Dict[str,Dict[str,List[Tuple[str,List[str]]]]]]]):
    gav = g + "__fdse__" + a + "__fdse__" + v
    sequenceUsage = []
    usageDb = apiUsageDB.usageDB
    for projectName in usageDb:
        for fileName in usageDb[projectName]:
            for jarName in usageDb[projectName][fileName]:
                gahv = jarName.split("__fdse__")
                if gahv[0] == g and gahv[1] == a and gahv[3] == v:
                    for methodName in usageDb[projectName][fileName][jarName]:
                        listEntry = []
                        mlist:List[Tuple[str,List[str]]] = usageDb[projectName][fileName][jarName][methodName]
                        for entry in mlist:
                            loc = entry[0]
                            apiListofL = entry[1]
                            for api in apiListofL:
                                listEntry.append(api)
                        sequenceUsage.append(listEntry)
    return sequenceUsage


############################ dependency rank ############################ 



def mycmp(x,y):
    valuex = x[1]
    valuey = y[1]
    sumx = 0
    sumy = 0
    for version in valuex:
        sumx+= version[1]
    for version in valuey:
        sumy+= version[1]
    if sumx < sumy:
        return 1
    else:
        return -1

## key ga, value dict<version,number>
def rerankGA(gaVersionMap):
    # gaList = list(gaVersionMap.items())
    # gaList.sort(key=cmp_to_key(mycmp))
    gaVersionMapList = sorted(gaVersionMap.items(), key=cmp_to_key(mycmp))
    return gaVersionMapList

def filterUnwantedGA(rankedGAVersionMapList:RankedDependencyUsage):
    keys = []
    for gaHash in rankedGAVersionMapList.usage.keys():
        if gaHash in F_filtered_jar.filterGA:
            keys.append(gaHash)
    for gaHash in keys:
        rankedGAVersionMapList.usage.pop(gaHash)


############################ dependency rank  end  ############################ 

############################ api usage rank  ############################ 


                
def mergeDepAPIUsage(depVersionCount:Dict[str,Dict[str,int]],apiUsageVersionCount:Dict[str,Dict[str,int]]):
    # mergeDepUsageAndAPIUsage:Dict[str,List[Tuple[str,int,int]]] = {}
    mergedUsage:RankedDependencyUsage = RankedDependencyUsage()
    for gaHash in apiUsageVersionCount:
        versionDict = apiUsageVersionCount[gaHash]
        gavUsageList:List[GAVUsage] = []
        for version in versionDict:
            apiuUsageNum = versionDict[version]
            if gaHash in depVersionCount and version in depVersionCount[gaHash]:
                depNum = depVersionCount[gaHash][version]
                item = GAVUsage(gaHash,version,depNum,apiuUsageNum)
                gavUsageList.append(item)
            else:
                # 抽不出API的lib
                item = GAVUsage(gaHash,version,-1,apiuUsageNum)
                gavUsageList.append(item)
        # mergeDepUsageAndAPIUsage [ga] = newList
        mergedUsage.setGAHashAndUsageMapping(gaHash, gavUsageList)
    return mergedUsage


############################ api usage rank end  ############################ 

############################ version pair selection  ############################ 

def mycmpVersionTup(x:GAVUsage,y:GAVUsage):
    v1 = x.version
    v2 = y.version
    v1 = v1.replace('-android','')
    v1 = v1.replace('-jre','')
    v2 = v2.replace('-android','')
    v2 = v2.replace('-jre','')
    if version.parse(v1) > version.parse(v2):
        return 1
    else:
        return -1

# def selectTopNVersion(versionMapList):
#     # 默认全选 按照usage 数量去除一部分
#     # if len(versionMapList) > 0:
#         # versionMapList = versionMapList[0:0]
#     versionList = []
#     for item in versionMapList:
#         versionList.append(item[0])
#     versionList.sort(key=cmp_to_key(mycmp))
#     return versionList

def genVersionDiffPair(gavUsageList:List[GAVUsage]):
    #todo
    # version gap = 1,2,4,5,10,
    # version gap = head and tail
    # 
    if len(gavUsageList) <=1:
        return None
    result:List[Tuple[str,str]] = []
    for i in range(0,len(gavUsageList)-1):
        result.append((gavUsageList[i].version,gavUsageList[i+1].version))
    if len(gavUsageList)>2:
        result.append((gavUsageList[0].version, gavUsageList[-1].version))
    if len(gavUsageList)>=3:
        majorD = {}
        for gavUsage in gavUsageList:
            parsedV = version.parse(gavUsage.version)
            if not hasattr(parsedV, 'major'):
                continue
            if parsedV.major not in majorD:
                majorD[parsedV.major] = []
            majorD[parsedV.major].append(gavUsage.version)
        keys = sorted(majorD.keys())
        for i in range(0,len(keys)-1):
            t = (majorD[keys[i]][0],majorD[keys[i+1]][0])
            if t not in result:
                result.append(t)
        if len(majorD)>2:
            t = (majorD[keys[0]][0],majorD[keys[-1]][0])
            if t not in result:
                result.append(t)
    return result


def randomSelectVersion(minorDict):
    gavUsage = []
    for minor in minorDict:
        for item in minorDict[minor]:
            gavUsage.append(item[1])
    index = random.randint(0,len(gavUsage)-1)
    return gavUsage[index]

def randomSelectVersionMicro(microDict):
    gavUsage = []
    for item in microDict:
        gavUsage.append(item[1])
    index = random.randint(0,len(gavUsage)-1)
    return gavUsage[index]

def randomSelectTwoRandomVersion(microDict):
    if len(microDict)<=1:
        return None,None
    index1 = random.randint(0,len(microDict)-2)
    index2 = random.randint(index1+1,len(microDict)-1)
    return microDict[index1],microDict[index2]


def genVersionDiffPairByMajorMinorPath(gavUsageList:List[GAVUsage]):
    #todo
    # version gap = 1,2,4,5,10,
    # version gap = head and tail
    #
    if len(gavUsageList) <=1:
        return None
    result:Dict[List[Tuple[str,str]]] = {}
    result['major'] = []
    result['minor'] = []
    result['micro'] = []
    treeVersion = {}
    for gavUsage in gavUsageList:
        parsedV = version.parse(gavUsage.version)
        if not hasattr(parsedV, 'major'):
            continue
        if parsedV.major not in treeVersion:
            treeVersion[parsedV.major] = {}
        if not hasattr(parsedV, 'minor'):
            continue
        if parsedV.minor not in treeVersion[parsedV.major]:
            treeVersion[parsedV.major][parsedV.minor] = []
        if not hasattr(parsedV, 'micro'):
            continue
        treeVersion[parsedV.major][parsedV.minor].append((parsedV.micro,gavUsage.version))
    majorKeys = sorted(treeVersion.keys())
    if len(majorKeys)>=2:
        majorRand = random.randint(0,len(majorKeys)-2)
        i = majorRand
        # for i in range(0,len(majorKeys)-1):
        majorKeyv0 = majorKeys[i]
        majorKeyv1 = majorKeys[i+1]
        rand1 = randomSelectVersion(treeVersion[majorKeyv0])
        rand2 = randomSelectVersion(treeVersion[majorKeyv1])
        t = (rand1,rand2)
        result['major'].append(t)
    for majorKey in majorKeys:
        minors = treeVersion[majorKey]
        minorKeys = sorted(minors.keys())
        if len(minors) <= 1:
            continue
        for ii in range(0,len(minorKeys)-1):
            # minorRand = random.randint(0,len(minorKeys)-2)
            minorRand = ii
            minorKeyv0 = minorKeys[minorRand]
            minorKeyv1 = minorKeys[minorRand+1]
            rand1 = randomSelectVersionMicro(treeVersion[majorKey][minorKeyv0])
            rand2 = randomSelectVersionMicro(treeVersion[majorKey][minorKeyv1])
            t = (rand1,rand2)
            result['minor'].append(t)
    for majorKey in majorKeys:
        minors = treeVersion[majorKey]
        minorKeys = sorted(minors.keys())
        for minor in minorKeys:
            # minorRand = random.randint(0,len(minorKeys)-1)
            # minorKeyRand = minorKeys[minorRand]
            minorKeyRand = minor
            usageList = []
            for item in treeVersion[majorKey][minorKeyRand]:
                usageList.append(item[1])
            if len(usageList)<=1:
                continue
            for jj in range(0,len(usageList)-1):
                a = usageList[jj]
                b = usageList[jj+1]
                t = (a,b)
                result['micro'].append(t)

    return result
############################ version pair selection end ############################



