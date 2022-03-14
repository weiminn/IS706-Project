import os
import json
from empiricalData.D_genApiUsageSequence import genSequence
from empiricalData.B_genGavs import getDepByProjJson
from empiricalData.D2_UsageSelection import topUsageSelection2,topUsagePairSelection,getCorrespondingGAVUsage
from typing import List, Tuple, Dict
from empiricalData.D3_FPTree_Python3 import runFIM
from empiricalData.D4_jarDiff import invokeJavaDiff
from empiricalData.MyEncoder import MyEncoder
from empiricalData.MyDecoder import MyDecoder
from empiricalData.G_Metrics import Metrics
from empiricalData import FIMStatistics
from empiricalData import Common
from empiricalData.DataBean.DependencyDB import DependencyDB
from empiricalData.DataBean.APIUsageDB import APIUsageDB
from empiricalData.DataBean.RankedDependencyUsage import RankedDependencyUsage,GAVUsage
from empiricalData.F_select_validate import generateGroundTruthRaw
from empiricalData.I_FIMMergeTable import buildTableAll,buildTablePartial
dbData = '21-1-14'
regenerate = False
# date = '21-3-23'
date = '21-4-19-all'
# date = '21-1-28'
# resultDate = '21-1-28'
resultDate = '21-4-19-all'

# start 0
def genDB():
    FIMFile = Common.FIM_FILE % date
    rankedGA = Common.RANKEDGA % date
    # if not regenerate and os.path.exists(FIMFile) and os.path.exists(rankedGA):
    #     return None,None

    depDbName:str = Common.DEP_DB_PATH % dbData 
    usageDbName:str = Common.USAGE_DB_PATH % dbData
    dependencyDB = getDepByProjJson(depDbName,regenerate)
    #            project ->file -> jarName -> method -> List[api usage sequence tuple]
    #                                           tuple = Tuple[line number, List[lib api]]
    usageDB = genSequence(usageDbName, regenerate)
    return dependencyDB,usageDB

# selection 1
def selectionGAV(depDb:Dict[str,List[str]] ,usageDb:Dict[str,Dict[str,Dict[str,Dict[str,List[Tuple[str,List[str]]]]]]]): 
    filePath = Common.USAGE_COUNT_OVERVIEW % date
    # cache
    # if not regenerate and os.path.exists(filePath):
    #     with open(filePath,'r') as f:
    #         j = json.load(f)
    #         decoder = MyDecoder()
    #         res = decoder.decodeCountOverview(j)
    #         return res
    #                                ga           version depCnt, APICnt
    # List[Tuple[str,List[GAVUsage]]]
    GAVersionAndAPICount,COUNTALL = topUsageSelection2(depDb,usageDb)
    with open(Common.USAGE_COUNT_OVERVIEW % date,'w') as f:
        encoder = MyEncoder(indent=4)
        s = encoder.encode(GAVersionAndAPICount)
        f.write(s)
    with open(Common.USAGE_COUNT_OVERVIEW_ALL % date,'w') as f:
        encoder = MyEncoder(indent=4)
        s = encoder.encode(COUNTALL)
        f.write(s)
    return GAVersionAndAPICount



def selectionGAVPair(rankedGAVersionAndAPICount:List[Tuple[str,List[GAVUsage]]]):
    
    # cache
    # if not regenerate and os.path.exists(filePath):
    #     with open(filePath,'r') as f:
    #         res = json.load(f)
    #     return res
        #                    ga                v1,v2
    topNiGAVersionPair:Dict[str,List[Tuple[str,str]]] = topUsagePairSelection(rankedGAVersionAndAPICount)
    filePath = Common.RANKEDGAVPair % date
    with open(filePath, 'w') as f:
        encoder = MyEncoder(indent=4)
        s = encoder.encode(topNiGAVersionPair)
        f.write(s)
    return topNiGAVersionPair

# input: usage sequence
# output: frequent usage set
def FIM(rankedGAVersionAndAPICount:List[Tuple[str,List[GAVUsage]]],usageDb):
    # return freqeuent usage set
    # return:
    # ga version usageset
    # Dict[str,Dict[str,List[str]]]
    fimPath = Common.FIM_FILE % date

    # if not regenerate and os.path.exists(fimPath):
    # #     json.dump(temp,f,indent=4)
    #     with open(fimPath, 'r') as f:
    #         res = json.load(f)
    #     return res

    result:Dict[str,Dict[str,List[str]]] = {}
    # temp = {}
    for tup in rankedGAVersionAndAPICount:
        gaHash = tup[0]
        gavUsageList = tup[1]
        if gaHash not in result:
            result[gaHash] = {}
        for gavUsage in gavUsageList:
            version = gavUsage.version
            data = gaHash.split('__fdse__')
            g = data[0]
            a = data[1]
            usageList:List[List[str]] = getCorrespondingGAVUsage(g,a,version,usageDb)
            # temp[ga][version] = usageList
            FIM_result,FIM_result_fre = runFIM(usageList,None,0)
            result[gaHash][version] = {}
            # result[ga][version]['FIM'] = FIM_result
            result[gaHash][version]['FIM_fre'] = FIM_result_fre
            result[gaHash][version]['total_usage_size'] = len(usageList)
            result[gaHash][version]['total_FIM_size'] = len(FIM_result)
    # with open(rootPath + '/2020-data/usage-overview-%s.json' % date,'w') as f:
    #     json.dump(temp,f,indent=4)
    with open(fimPath, 'w') as f:
        json.dump(result,f,indent=4)
    return result



def m():
    print('genDB')
    depDb,usageDb = genDB()
    print('selection')
    #  排序的GAV version pair
    rankedGAVersionAndAPICount = selectionGAV(depDb,usageDb)
    # # 这一步会重新生成
    # # selection todo 需要增加version pair
    topNiGAVersionPair = selectionGAVPair(rankedGAVersionAndAPICount)

    # # rankedGAVersionAndAPICount ,topNiGAVersionPair = selection(rootPath,depDb,usageDb)
    # print('FIM...')
    # frequentUsageSet:Dict[str,Dict[List[str]]] = FIM(rankedGAVersionAndAPICount,usageDb)
    # FIMStatistics.fimStatistics(frequentUsageSet)

    
# m()

def m2():
    print('invokeJavaDiff...')
    # with open(Common.FIM_FILE % date, 'r') as f:
    with open(Common.FIM_FILE % "21-3-23", 'r') as f:
        fimDb = json.load(f)
    with open(Common.RANKEDGAVPair % date, 'r') as f:
        topNiGAVersionPair = json.load(f)
        # 246
    print(len(topNiGAVersionPair))
    # with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/verification/deleted_result-3-15.json','r') as f:
    #     j2 = json.load(f)
    # for item in j2:
    #     if item not in topNiGAVersionPair:
    #         print(item)

    finalResult = invokeJavaDiff(topNiGAVersionPair,fimDb)
    with open(Common.FINAL_RESULT % resultDate,'w') as f:
        encoder = MyEncoder(indent=4)
        ss = encoder.encode(finalResult)
        f.write(ss)
    # generateGroundTruthRaw(resultDate)


    # # 71768
    # # 71822

# m2()

#  finalResult['a_has_deleted'][<ga>][<version>]['usage'] = List[BeanAPISeq]
#                                                ['simi_map']['original_seq_id']
#                                                ['simi_map']['dst_seq_map']
#  finalResult['a_only_modified']
#  finalResult['c_all_same']
#  finalResult['c_modified']
#  finalResult['a_all_same']


