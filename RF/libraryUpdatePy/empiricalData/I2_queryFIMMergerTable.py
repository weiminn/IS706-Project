import os
import json
import xlrd
from typing import List, Tuple, Dict, Set
from libraryUpdatePy.empiricalData.DataBean.BeanAPISeq import BeanAPISeq
from libraryUpdatePy.empiricalData.DataBean.BeanAPI import BeanAPI
from libraryUpdatePy.empiricalData import  Common

def borrowFIMFromOtherVersions(gaHash,FIM,versionAPIList:Dict[str,Set[str]]):
    result = {}
    for version in versionAPIList:
        # FIM[gaHash][version]
        if version not in FIM[gaHash]:
            continue
        fimUsage = FIM[gaHash][version]['FIM_fre']
        usageSize = FIM[gaHash][version]['total_usage_size']
        fimSize = FIM[gaHash][version]['total_FIM_size']
        okAPIList = versionAPIList[version]
        for seq in fimUsage:
            isOk = True
            apiList = seq['usage_seq']
            frequency = seq['frequency']
            for api in apiList:
                if api not in okAPIList:
                    isOk = False
                    break
            if isOk:
                tup = tuple(apiList)
                if not tup in result:
                    result[tup] = 0
                result[tup] += frequency  

    return result

def queryTableNeighborVersionsSameAPI(apiListVersionV0Have,versionV0Index,versionSize,sheet):
    result:Dict[str,List[str]] = {}
    for api in apiListVersionV0Have:
        rowId = apiListVersionV0Have[api]
        columnid = versionV0Index*2 + 1
        right = versionV0Index
        # 往右走
        for right in range(versionV0Index,versionSize-1):
            data = sheet.cell(rowId,2*right+2).value
            nextVersionId = sheet.cell(0,2*right+3).value
            if data =='same' or data == '':
                if api not in result:
                    result[api] = []
                result[api].append(nextVersionId)
            else:
                break
        left = 0
        # 往左走
        for left in range(0, right-1):
            data = sheet.cell(rowId,2*left+2).value
            nextVersionId = sheet.cell(0,2*left+3).value
            if data =='same' or data == '':
                if api not in result:
                    result[api] = []
                result[api].append(nextVersionId)
            else:
                break
    return result

def transformedDict(apiListVersion:Dict[str,List[str]]):
    result = {}
    for api in apiListVersion:
        for version in apiListVersion[api]:
            if not version in result:
                result[version] = set()
            if api not in result[version]:
                result[version].add(api)
    return result

def queryTableHaveAPI(rowSize, columnId, sheet):
    apiDict = {}
    for i in range(0, rowSize):
        #                 row start from 1
        data = sheet.cell(i+1,columnId).value
        api = sheet.cell(i+1,0).value
        if data == 'exist':
            apiDict[api] = i+1
    return apiDict

def querySheet(sheet, version, versionNum):
    for i in range(0,versionNum):
        data = sheet.cell(0,2*i+1).value
        if data == version:
            # version 的index
            return i 
    return None

def createBeanAPISeq(data):
    res = []
    for apiTup in data:
        fre = data[apiTup]
        beanAPISeq = BeanAPISeq('c')
        for api in apiTup:
            beanApi = BeanAPI(api)
            beanAPISeq.addBeanAPI(beanApi)
        beanAPISeq.setFrequencyV1(fre)
        res.append(beanAPISeq)
    return res
                    
def queryTable(versionV0, FIM, gaHash):
    rootPath =  Common.ROOT_PATH + 'output/'
    # print('excel: ' + rootPath + 'jar_diff/%s/Diff-table-%s.xls' % (gaHash,gaHash))
    rw = xlrd.open_workbook(rootPath + 'jar_diff/%s/Diff-table-%s.xls' % (gaHash,gaHash))
    sheet1 = rw.sheet_by_index(0)
    data = sheet1.cell(0,0).value.split('*')
    apiNum = int(data[0])
    versionNum = int(data[1])
    # 这个版本的v0 index
    # print("APINum: %d" % apiNum)
    # print("VersionNum: %d" % versionNum)
    
    versionV0Index = querySheet(sheet1, versionV0, versionNum)
    if versionV0Index == None:
        print(gaHash)
        print(versionV0)
        return
    # 
    # print("Version index: %d" % versionV0Index)   
    # A = v0版本在table上exist的API            
    #                                                           column
    apiListVersionV0Have:Dict[str,int] = queryTableHaveAPI(apiNum,2*versionV0Index+1,sheet1)
    # print("v0 API list: %d" % len(apiListVersionV0Have))
    # B = “v0版本在table上exist的API“ 在临近version上相同的version list
    #                         apiName, same versions
    apiListVersionRange:Dict[str,List[str]] = queryTableNeighborVersionsSameAPI(apiListVersionV0Have,versionV0Index,versionNum,sheet1)
    # print("Neighboring version: %d" % len(apiListVersionRange))
    # 转换B的key value格式
    # #                   key:version v:Set<API>
    versionAPIList:Dict[str,Set[str]] =  transformedDict(apiListVersionRange)
    # print("versionAPIList: %d" % len(versionAPIList))
    # print(versionAPIList)
    allFIMs:Dict[Tuple[str,int]] = borrowFIMFromOtherVersions(gaHash,FIM,versionAPIList)
    beanAPISeqList:List[BeanAPISeq] =  createBeanAPISeq(allFIMs)
    # print(len(beanAPISeqList))
    return beanAPISeqList

def testMergeTable():
    rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/'
    fim = '2020-data/usage-overview-FIM-21-1-20-filter.json'
    with open(rootPath + fim,'r') as f:
        j = json.load(f)
    gaHash = 'com.google.guava__fdse__guava__fdse__a1e0af'
    v0 = '18.0'
    print(len(j[gaHash][v0]['FIM_fre']['usage_seq']))
    fim2:List[BeanAPISeq] = queryTable(v0,j,gaHash)
    
    
# testMergeTable()



