import os
import json
from libraryUpdatePy.empiricalData import Common
from libraryUpdatePy.empiricalData.I2_queryFIMMergerTable import queryTable
from libraryUpdatePy.empiricalData.MyEncoder import MyEncoder

def dumpAPIRawDbBundle(usageDb,gah):
    result = {}
    for project in usageDb:
        for fileName in usageDb[project]:
            for jarName in usageDb[project][fileName]:
                data = jarName.split('/')
                data2 = data[0].split('__fdse__')
                gaHash = '%s__fdse__%s__fdse__%s' % (data2[0],data2[1],data2[2])
                version = data2[3]
                # print(gaHash)
                if not (gaHash == gah):
                    continue
                if version not in result:
                    result[version] = []
                newSpot = {}
                methodList = usageDb[project][fileName][jarName]
                # dump to files
                newSpot['method_list'] = methodList
                newSpot['fileName'] = fileName
                newSpot['project'] = project
                result[version].append(newSpot)
    resultPathPrefix = Common.DELETED_VALIDATION_PATH + gah + '/usage_raw/'
    if not os.path.exists(resultPathPrefix):
        os.makedirs(resultPathPrefix)
    resultPath = resultPathPrefix + 'bundled-version.json'
    with open(resultPath,'w') as f:
        json.dump(result,f,indent=4)


def dumpAPIRawDb(usageDb,gah,v):
    result = []
    for project in usageDb:
        for fileName in usageDb[project]:
            for jarName in usageDb[project][fileName]:
                data = jarName.split('/')
                data2 = data[0].split('__fdse__')
                gaHash = '%s__fdse__%s__fdse__%s' % (data2[0],data2[1],data2[2])
                version = data2[3]
                # print(gaHash)
                if not (gaHash == gah and version == v):
                    continue
                newSpot = {}
                methodList = usageDb[project][fileName][jarName]
                # dump to files
                newSpot['method_list'] = methodList
                newSpot['fileName'] = fileName
                newSpot['project'] = project
                result.append(newSpot)
    resultPathPrefix = Common.DELETED_VALIDATION_PATH + gah + '/usage_raw/'
    if not os.path.exists(resultPathPrefix):
        os.makedirs(resultPathPrefix)
    resultPath = resultPathPrefix + v + '.json'
    with open(resultPath,'w') as f:
        json.dump(result,f,indent=4)
        



def dumpFIMDbRaw(FIMDb,gah,v):
    result = FIMDb[gah][v]
    resultPathPrefix = Common.DELETED_VALIDATION_PATH + gah + '/fim_raw/'
    if not os.path.exists(resultPathPrefix):
        os.makedirs(resultPathPrefix)
    resultPath = resultPathPrefix + v + '.json'
    with open(resultPath,'w') as f:
        json.dump(result,f,indent=4)


def dumpFIMDbMerged(FIMDb,gah,v,versionpair):
    result = queryTable(v,FIMDb,gah)

    resultPathPrefix = Common.DELETED_VALIDATION_PATH + gah + '/fim_merge/%s/' % versionpair 
    if not os.path.exists(resultPathPrefix):
        os.makedirs(resultPathPrefix)
    resultPath = resultPathPrefix + v + '.json'
    with open(resultPath,'w') as f:
        en = MyEncoder(indent=4)
        s = en.encode(result)
        f.write(s)


# 针对ground truth分拆成几个json文件 ，人工验证是否能有mapped method
def dumpUsage():
    # read deleted method json
    # ga - version pair - deleted method
    # read usage db
    with open(Common.USAGE_DB_PATH % '21-1-14','r') as f:
        usageDb = json.load(f)
    with open(Common.FIM_FILE % '21-1-28','r') as f:
        FIMDb = json.load(f) 
    with open(Common.DELETED_METHOD_GROUND_TRUTH % '1-28','r') as f:
        gt = json.load(f)

    #                               jarName = junit__fdse__junit-dep__fdse__2a5a4e__fdse__4.8.2__fdse__jar/junit-dep-4.8.2.jar
    #            project ->file -> jarName -> method -> List[api usage sequence tuple]
    #                                           tuple = Tuple[line number, List[lib api]]
    for gaHash in gt:

        dumpAPIRawDbBundle(usageDb,gaHash)
        continue
        for versionpair in gt[gaHash]:
            data = versionpair.split('__fdse__')
            v0 = data[0]
            v1 = data[1]
            print(gaHash)
            for entry in gt[gaHash][versionpair]:
                srcMethod = entry['src']
                dstMethods = entry['dst']
                # mappingValue = gt[gaHash][versionpair][methodKey]
                # methodKey and value
                dumpAPIRawDb(usageDb,gaHash,v0)
                dumpAPIRawDb(usageDb,gaHash,v1)
                dumpFIMDbRaw(FIMDb,gaHash,v0)
                dumpFIMDbRaw(FIMDb,gaHash,v1)
                dumpFIMDbMerged(FIMDb,gaHash,v1,versionpair)



#############################################################

def isDstMethodsExistsInUsage(gaHash,v1,dstMethods):
    resultPathPrefix = Common.DELETED_VALIDATION_PATH + gaHash + '/usage_raw/'
    resultPath = resultPathPrefix + v1 + '.json'
    with open(resultPath,'r') as f:
        j = json.load(f)
    for entry in j:
        methodList = entry['method_list']
        for invokeMethodKey in methodList:
            apiList = methodList[invokeMethodKey]
            for lineList in apiList:
                loc = lineList[0]
                apiList2 = lineList[1]
                for api in apiList2:
                    data = api.split('__fdse__')
                    shortApi = data[-1]
                    if shortApi in dstMethods:
                        return 1
    return 0


def isDstMethodsExistsInOtherUsage(gaHash,dstMethods):
    resultPathPrefix = Common.DELETED_VALIDATION_PATH + gaHash + '/usage_raw/'
    resultPath = resultPathPrefix + 'bundled-version.json'
    with open(resultPath,'r') as f:
        j = json.load(f)
    for version in j:
        item = j[version]
        for entry in item:
            methodList = entry['method_list']
            for invokeMethodKey in methodList:
                apiList = methodList[invokeMethodKey]
                for lineList in apiList:
                    loc = lineList[0]
                    apiList2 = lineList[1]
                    for api in apiList2:
                        data = api.split('__fdse__')
                        shortApi = data[-1]
                        if shortApi in dstMethods:
                            return 1
    return 0


def isDstMethodsExistsInFIM(gaHash,v1,dstMethods):
    resultPathPrefix = Common.DELETED_VALIDATION_PATH + gaHash + '/fim_raw/'
    resultPath = resultPathPrefix + v1 + '.json'
    with open(resultPath,'r') as f:
        j = json.load(f)
    fimFre = j['FIM_fre']
    for entry in fimFre:
        seq = entry['usage_seq']
        for api in seq:
            data = api.split('__fdse__')
            apiShort = data[-1]
            if apiShort in dstMethods:
                return 1
    return 0
    # 

def isDstMethodsExistsInFIMMerge(gaHash,versionpair,v1,dstMethods):
    resultPathPrefix = Common.DELETED_VALIDATION_PATH + gaHash + '/fim_merge/%s/' % versionpair 
    resultPath = resultPathPrefix + v1 + '.json'
    with open(resultPath,'r') as f:
        j = json.load(f)
    for entry in j:
        apiSeq = entry['apiSeq']
        for apiD in apiSeq:
            apiName = apiD['api']
            data = apiName.split('__fdse__')
            apiShort = data[-1]
            if apiShort in dstMethods:
                return 1
    return 0


def saveToFilteredGt(result,gaHash, versionpair, entry):
    if gaHash not in result:
        result[gaHash] = {}
    if versionpair not in result[gaHash]:
        result[gaHash][versionpair] = []
    result[gaHash][versionpair].append(entry)

