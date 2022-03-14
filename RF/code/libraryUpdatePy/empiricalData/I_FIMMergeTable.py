import os
import json
from typing import List, Tuple, Dict, Set
import xlwt
from empiricalData.D4_jarDiff import postToJarDiffServer
import requests
import numpy as np
from empiricalData import Common
from empiricalData.MyDecoder import MyDecoder
from functools import cmp_to_key
from packaging import version


def initExcel(apis,versions,exl):
    sheet1 = exl.add_sheet(u'sheet1',cell_overwrite_ok=True)
    # v: 2*i-1
    # v1-v2: 2*i-1
    sheet1.write(0,0, str(len(apis))+'*' + str(len(versions)))
    for i in range(0,len(versions)):
        sheet1.write(0,2*i+1,versions[i])
        if i != len(versions)-1:
            sheet1.write(0,2*i+2,versions[i] + "--" + versions[i+1])
    for i in range(0,len(apis)):
        sheet1.write(i+1,0,apis[i])
    return sheet1
    
#                       without ret                         without ret             with ret
def fillExcelDiffInfo(diffInfo:Dict[str,List[str]],column,queryServerAPIs,wtSheet,apiListMap):
    added = diffInfo['added']
    deleted = diffInfo['deleted']
    modified = diffInfo['modified']
    for api in queryServerAPIs:
        apiFullName = None
        for key in apiListMap.keys():
            data = key.split('__fdse__')
            if data[-1] == api:
                apiFullName = key
        if apiFullName == None:
            continue
        row = apiListMap[apiFullName] + 1
        if api in added:
            # print('add!')
            wtSheet.write(row,column,"added")
        if api in deleted:
            # print('add!')
            wtSheet.write(row,column,"deleted")
        if api in modified:
            # print('add!')
            wtSheet.write(row,column,"modified")

# ga的所有version的频繁API的集合
#                                     ga       version
def getAPIListFromFIM(gaHash,FIM:Dict[str,Dict[str,List[str]]]):
    apiSet = set()
    for version in FIM[gaHash]:
        seqList = FIM[gaHash][version]['FIM_fre']
        for seq in seqList:
            usageList = seq['usage_seq']
            for api in usageList:
                apiSet.add(api)
    return list(apiSet)

def postAPIExistanceInfo(gaHash,v1,apiListAll):
    data = gaHash.split('__fdse__')
    postStr = {}
    postStr['groupId'] = data[0]
    postStr['artifactId'] = data[1]
    postStr['version'] = v1
    postStr['usage_array'] = apiListAll
    req = requests.post('http://10.176.34.86:18123/apiexistence',json=postStr)
    content = req.content
    # json list
    j = json.loads(content)
    return j

def fillAPIExistanceInfo(existAPIs,sheet,versionIndex,apiListMap, matrix):
    filledRows = set()
    column = versionIndex * 2 + 1
    for api in existAPIs:
        row = apiListMap[api] + 1
        sheet.write(row,column,"exist")
        matrix[row][column] = 1
        filledRows.add(row)
    for i in range(1,len(apiListMap)+1):
        if i not in filledRows:
            sheet.write(i,column,"NA")


def versionrankasc(x,y):
    v1 = x
    v2 = y
    v1 = v1.replace('-android','')
    v1 = v1.replace('-jre','')
    v2 = v2.replace('-android','')
    v2 = v2.replace('-jre','')
    if version.parse(v1) > version.parse(v2):
        return 1
    else:
        return -1

def buildTable(usageCountOverviewDate,fimDate,usageCountOverview):
    with open(Common.FIM_FILE % fimDate,'r') as f:
        fim = json.load(f)
    for entry in usageCountOverview:
        gaHash = entry[0]
        usageList = entry[1]
        if usageList == None or len(usageList) <=1:
            continue
        outputPath = Common.ROOT_PATH + 'output/jar_diff/' + gaHash
        excelPath = outputPath + '/Diff-table-%s.xls' % gaHash
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        # if os.path.exists(excelPath):
        #     continue
        apiListAll = getAPIListFromFIM(gaHash, fim)
        versionList = []
        apiListAll = sorted(apiListAll)
        for usageItem in usageList:
            version = usageItem.version
            versionList.append(version)
        versionList = sorted(versionList, key=cmp_to_key(versionrankasc))
        wt = xlwt.Workbook()
        sheet1 = initExcel(apiListAll, versionList,wt)

        apiListMap = {}
        for i in range(0,len(apiListAll)):
            apiListMap[apiListAll[i]] = i
        # 填diff信息
        matrix = np.zeros((len(apiListAll)+1, 2 * len(versionList)))

        for i in range(0,len(versionList)):
            v1 = versionList[i]
            existAPIs = postAPIExistanceInfo(gaHash,v1,apiListAll)
            fillAPIExistanceInfo(existAPIs,sheet1,i,apiListMap,matrix)

        for i in range(0,len(versionList)-1):
            v1 = versionList[i]
            v2 = versionList[i+1]
            queryServerAPIs = []
            columnV1 = 2*i + 1
            columnV2 = 2*i + 3
            for api in apiListAll:
                data = api.split('__fdse__')
                # row = apiListMap[api] + 1
                # if matrix[row][columnV1] == 0 or matrix[row][columnV2] == 0:
                queryServerAPIs.append(data[-1])
            gaHashData = gaHash.split('__fdse__')
            diffJson:Dict[str,List[str]] = postToJarDiffServer(gaHashData[0],gaHashData[1],v1,v2,queryServerAPIs)
            if len(diffJson) == 0 or (len(diffJson['added'])==0 and len(diffJson['deleted'])==0 and len(diffJson['modified'])==0):
                # 完全相同的jar包  
                continue
            fillExcelDiffInfo(diffJson,2*i+2,queryServerAPIs,sheet1,apiListMap)

        print(excelPath)
        wt.save(excelPath)
        # todo inner class existance
        # break

# /home/hadoop/dfs/data/Workspace/LibraryUpdate/output/jar_diff/com.google.protobuf__fdse__protobuf-java__fdse__e9ee72/Diff-table.xls


def buildTableAll(usageCountOverviewDate,fimDate):
    with open(Common.USAGE_COUNT_OVERVIEW % usageCountOverviewDate,'r') as f:
        s = json.load(f)
        deco = MyDecoder()
        usageCountOverview = deco.decodeCountOverview(s)
    buildTable(usageCountOverviewDate,fimDate,usageCountOverview)


def buildTablePartial(usageCountOverviewDate,fimDate,finalResultDate):
    with open(Common.USAGE_COUNT_OVERVIEW_ALL % usageCountOverviewDate,'r') as f:
        s = json.load(f)
        deco = MyDecoder()
        usageCountOverview = deco.decodeCountOverview(s)
    key = 'a_has_deleted'
    with open(Common.FINAL_RESULT % finalResultDate,'r') as f:
        finalResult = json.load(f)
        deleted = finalResult[key]
    newResult = []
    for entry in usageCountOverview:
        gaHash = entry[0]
        if gaHash in deleted:
            newResult.append((gaHash,entry[1]))
    buildTable(usageCountOverviewDate,fimDate,newResult)


# buildTablePartial('21-1-28','21-1-28','21-1-28')

