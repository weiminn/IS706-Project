import os
import json
import requests

import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib
from matplotlib.font_manager import FontProperties
import FontSizeAll
import matplotlib as mpl
from empiricalData.D_genApiUsageSequence import trimAPI


def postToJarDiffServer(groupId,artifactId,v1,v2,isAllDiffAPI,usageArray):
    postStr = {}
    postStr['groupId'] = groupId
    postStr['artifactId'] = artifactId
    postStr['version1'] = v1
    postStr['version2'] = v2
    postStr['usage_array'] = usageArray
    postStr['all_diff_api'] = isAllDiffAPI
    req = requests.post('http://10.176.34.86:18123/jardiff',json=postStr)
    content = req.content
    j = json.loads(content)
    return j

def fireReq(gaHash,vPair):
    data = gaHash.split('__fdse__')
    groupId = data[0]
    artifactId = data[1]
    v0 = vPair[0]
    v1 = vPair[1]
    diffJson = postToJarDiffServer(groupId,artifactId,v0,v1,True,None)
    if len(diffJson) == 0:
        return None
    deletedClass = diffJson['deleted_classes']
    deletedEntryInClass = diffJson['undeleted_class_deleted_items']
    noDelClass = len(deletedClass)
    noDelField = 0
    noDelMethod = 0
    noDelMethodInDelClass = 0
    for item in deletedClass:
        noDelMethodInDelClass += len(item['deleted_method_in_class'])
    for item in deletedEntryInClass:
        t1 = len(item['deleted_fields_in_class'])
        t2 = len(item['deleted_method_in_class'])
        noDelField += t1
        noDelMethod += t2
    
    return (noDelClass,noDelMethodInDelClass,noDelMethod,noDelField)

def calAver(li):
    lenLi = len(li)
    if lenLi == 0:
        return None
    # class
    s1 = 0
    # method in del class
    s2 = 0
    # method 
    s3 = 0
    # field
    s4 = 0
    # sum
    s5 = 0
    for item in li:
        s1 += item[0]
        s2 += item[1]
        s3 += item[2]
        s4 += item[3] 
        s5 += item[1] + item[2]
    
    aver1 = s1/lenLi
    aver2 = s2/lenLi
    aver3 = s3/lenLi
    aver4 = s4/lenLi
    averSum = s5/lenLi
    res = {}
    res['aver_class'] = aver1
    res['aver_method_in_class'] = aver2
    res['aver_method'] = aver3
    res['aver_field'] = aver4
    res['aver_sum'] = averSum
    return res

def run():
    path = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-data'
    top200VersionPairPath = path + '/topNiGAVersionPair-21-4-19-top200.json'
    with open(top200VersionPairPath,'r') as f:
        j = json.load(f)
    result = {}
    result['major'] = []
    result['minor'] = []
    result['micro'] = []
    cnt = 0
    vPairCnt = 0
    for gaHash in j:
        major = j[gaHash]['major'] 
        cnt +=1
        print('ga: %s cnt: %d vPair processed: %d' %(gaHash,cnt,vPairCnt))
        for vPair in major:
            diffAPINum = fireReq(gaHash,vPair)
            vPairCnt+=1
            if diffAPINum == None:
                continue
            result['major'].append(diffAPINum)
        minor = j[gaHash]['minor'] 
        for vPair in minor:
            diffAPINum = fireReq(gaHash,vPair)
            vPairCnt+=1
            if diffAPINum == None:
                continue
            result['minor'].append(diffAPINum)
        micro = j[gaHash]['micro']
        for vPair in micro:
            diffAPINum = fireReq(gaHash,vPair)
            vPairCnt+=1
            if diffAPINum == None:
                continue
            result['micro'].append(diffAPINum)
    result2 = {}
    resDict = calAver(result['major'])
    result2['major'] = resDict
    resDict = calAver(result['minor'])
    result2['minor'] = resDict
    resDict = calAver(result['micro'])
    result2['micro'] = resDict
    with open(path+'/empirical-bar-4-19.json','w') as f:
        json.dump(result2,f,indent=4)
    
# run()


################### Run usage
usageDB = None

def queryUsage(gah,version):
    global usageDB 
    if usageDB == None:
        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-data/usage-db-21-1-14.json','r') as f:
            j = json.load(f)
            usageDB = j
    apiUsageListAll = set()
    for proj in usageDB:
        for file in usageDB[proj]:
            for lib in usageDB[proj][file]:
                d = lib.split('__fdse__')
                gaHash1 = '%s__fdse__%s__fdse__%s' %(d[0],d[1],d[2])
                if gaHash1 != gah:
                    continue
                if version != d[3]:
                    continue
                for method in usageDB[proj][file][lib]:
                    data = usageDB[proj][file][lib][method]
                    for tup in data:
                        line = tup[0]
                        usageAPIList = tup[1]
                        for api in usageAPIList:
                            methodShort = trimAPI(api)
                            dataMethod = methodShort.split('__fdse__')
                            apiUsageListAll.add(dataMethod[-1])
    return list(apiUsageListAll)
    

def fireReq2(gaHash,vPair):
    data = gaHash.split('__fdse__')
    groupId = data[0]
    artifactId = data[1]
    v0 = vPair[0]
    v1 = vPair[1]
    usageAPIs = queryUsage(gaHash,v0)
    print('usage: %d' % len(usageAPIs))
    l1 = len(usageAPIs)
    diffJson = postToJarDiffServer(groupId,artifactId,v0,v1,False,usageAPIs)
    if len(diffJson) == 0 or len(diffJson['deleted']) == 0:
        return (l1,0)
    l2 = len(diffJson['deleted']) 
    print('deleted: %d' % l2)
    return (l1,l2)

def calAver2(li):
    lenLi = len(li)
    if lenLi == 0:
        return None
    # aver api usage
    s1 = 0
    # aver api usage deleted
    s2 = 0
    for item in li:
        s1 += item[0]
        s2 += item[1]
    aver1 = s1/lenLi
    aver2 = s2/lenLi
    res = {}
    res['aver_api_usage'] = aver1
    res['aver_api_usage_deleted'] = aver2
    res['sum_api_usage'] = s1
    res['sum_api_usage_deleted'] = s2
    return res

def run2():
    path = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-data'
    top200VersionPairPath = path + '/topNiGAVersionPair-21-3-23-top200-empirical.json'
    with open(top200VersionPairPath,'r') as f:
        j = json.load(f)
    result = {}
    result['major'] = []
    result['minor'] = []
    result['micro'] = []
    for gaHash in j:
        major = j[gaHash]['major'] 
        for vPair in major:
            diffAPINum = fireReq2(gaHash,vPair)
            if diffAPINum == None:
                continue
            result['major'].append(diffAPINum)
        minor = j[gaHash]['minor'] 
        for vPair in minor:
            diffAPINum = fireReq2(gaHash,vPair)
            if diffAPINum == None:
                continue
            result['minor'].append(diffAPINum)
        micro = j[gaHash]['micro']
        for vPair in micro:
            diffAPINum = fireReq2(gaHash,vPair)
            if diffAPINum == None:
                continue
            result['micro'].append(diffAPINum)
    result2 = {}
    resDict = calAver2(result['major'])
    result2['major'] = resDict
    resDict = calAver2(result['minor'])
    result2['minor'] = resDict
    resDict = calAver2(result['micro'])
    result2['micro'] = resDict
    with open(path+'/empirical-bar-usage-4-17.json','w') as f:
        json.dump(result2,f,indent=4)
  
# run2()

