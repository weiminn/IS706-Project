import os
import json
from libraryUpdatePy.empiricalData.I2_queryFIMMergerTable import queryTable
from typing import List, Tuple, Dict, Set
from libraryUpdatePy.empiricalData.MyDecoder import MyDecoder
from libraryUpdatePy.empiricalData.SimilarityMatrix import SimilarityMatrix
from libraryUpdatePy.empiricalData.DataBean.BeanAPISeq import BeanAPISeq
from libraryUpdatePy.empiricalData.MyEncoder import MyEncoder

def getDeletedMethodSeq(seqList,deletedMethod):
    deletedSeq = []
    for seq in seqList:
        apiSeq = seq['apiSeq']
        isHave = False
        for api in apiSeq:
            data = api['api'].split('__fdse__')
            if data[-1] == deletedMethod:
                isHave = True
                break
        deletedSeq.append(seq)
    return deletedSeq

def readV0FIM(finalResult,versionPair,gaHash):
    deleted = finalResult['a_has_deleted']
    if not gaHash in deleted:
        return None
    if not versionPair in deleted[gaHash]:
        return None
    usage = deleted[gaHash][versionPair]['usage']
    return usage

def isBeanSeqEqual(a,b):
    aList = a.getBeanAPIList()
    aSet = set()
    bList = b.getBeanAPIList()
    bSet = set()
    for beanAPI in aList:
        aSet.add(beanAPI.getAPIName())
    for beanAPI in bList:
        bSet.add(beanAPI.getAPIName())
    if len(aSet) == len(bSet):
        if len(aSet & bSet) == len(bSet):
            return True
    return False


def mergeFIMs(a:List[BeanAPISeq],b:List[BeanAPISeq]):
    # todo
    res = []
    for i in a:
        res.append(i)
    di = {}
    for seq in a:
        ha = seq.hashCode()
        if not ha in di:
            di[ha] = seq
    for beanAPISeqB in b:
        isSame = False
        sameBean = None
        ha2 = beanAPISeqB.hashCode()
        if ha2 in di:
            sameBean  = di[ha2]
            sameBean.setFrequencyV1(sameBean.getFrequencyV1() + beanAPISeqB.getFrequencyV1())
        else:
            res.append(beanAPISeqB)
    return res

def readV1FIM(FIMDb,v1,gaHash):
    # FIMDb[gaHash][v1]
    usageSeq = FIMDb[gaHash][v1]['FIM_fre']
    decoder = MyDecoder()
    original = []
    for s in usageSeq:
        beanAPISeq = decoder.decodeToSeqBeanListFIM(s)
        original.append(beanAPISeq)
    addedFIMs:List[BeanAPISeq] = queryTable(v1,FIMDb,gaHash)
    mergedSeqList = mergeFIMs(original,addedFIMs)
    print("V1 FIM len: %d" % len(mergedSeqList))
    return mergedSeqList


def saveObj(rootPath,result,gaHash):
    tmpV0 = {}
    tmpV1 = {}
    for versionPair in result:
        v0 = result[versionPair]['v0']
        v1 = result[versionPair]['v1']
        tmpV0[versionPair] = v0
        tmpV1[versionPair] = v1
    with open(rootPath + '%s-v0.json' % gaHash,'w') as f:
        encoder = MyEncoder(indent=4)
        ss = encoder.encode(tmpV0)
        f.write(ss)
    with open(rootPath + '%s-v1.json' % gaHash,'w') as f:
        encoder = MyEncoder(indent=4)
        ss = encoder.encode(tmpV1)
        f.write(ss)


def run():
    # read map
    rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/'
    mapPath = '2020-data/deleted_method_validation-1-20.json'
    finalResult = '2020-data/usage_final_result-21-1-20-filter.json'
    FIMDb = '2020-data/usage-overview-FIM-21-1-20-filter.json'
    with open(rootPath + mapPath, 'r') as f:
        mapJson = json.load(f)
    with open(rootPath + finalResult,'r') as f:
        finalResult = json.load(f)
    with open(rootPath + FIMDb,'r') as f:
        FIMDb = json.load(f)
    decoder = MyDecoder()
    
    for gahash in mapJson:
        print(gahash)
        debugResult = {}
        for versionPair in mapJson[gahash]:
            print(versionPair)
            value = mapJson[gahash][versionPair]
            if not (gahash in finalResult['a_has_deleted'] and versionPair in finalResult['a_has_deleted'][gahash]):
                print('XXXXX')
                continue
            dataV = versionPair.split('__fdse__')
            v0 = dataV[0]
            v1 = dataV[1]
            v0FIMSeqList = readV0FIM(finalResult,versionPair,gahash)
            # fim[ga][version]['FIM'] ,[ga][version]['FIM_fre']
            totalUsageSize = FIMDb[gahash][v1]['total_usage_size']
            totalFIMSize = FIMDb[gahash][v1]['total_FIM_size']
            # [ga][version]['total_usage_size'],  [ga][version]['total_FIM_size'] 
            v1FIMSeqBeanList:List[BeanAPISeq] = readV1FIM(FIMDb,v1,gahash)  

            if not versionPair in debugResult:
                debugResult[versionPair] = {}
            debugResult[versionPair]['v1'] = v1FIMSeqBeanList

            for deletedMethod in value:
                mappedMethod = value[deletedMethod]
                v0FIMDeletedMethodSeqStr:List[str] = getDeletedMethodSeq(v0FIMSeqList,deletedMethod)
                v0FIMDeletedMethodSeqBean:List[BeanAPISeq] =  decoder.decodeToSeqBeanList(v0FIMDeletedMethodSeqStr)
                gTruth = []
                for i in range(0,len(v1FIMSeqBeanList)):
                    seq = v1FIMSeqBeanList[i]
                    beanAPIList = seq.getBeanAPIList()
                    for beanAPI in beanAPIList:
                        name = beanAPI.getAPIName()
                        if mappedMethod in name:
                            gTruth.append(len(v0FIMDeletedMethodSeqBean) + i)
                print(deletedMethod)
                if len(gTruth) == 0:
                    print('Cannot found truth')
                    # print(gTruth)
                if 'v0' not in debugResult[versionPair]:
                    debugResult[versionPair]['v0'] = {}
                if 'deleted_method' not in debugResult[versionPair]['v0']:
                    debugResult[versionPair]['v0']['deleted_method'] = []
                debugResult[versionPair]['v0']['deleted_method'].append(deletedMethod)
                if 'FIM' not in debugResult[versionPair]['v0']:
                    debugResult[versionPair]['v0']['FIM'] = []
                debugResult[versionPair]['v0']['FIM'].append(v0FIMDeletedMethodSeqBean)

        saveObj(rootPath +'2020-data/deleted_method_validation/',debugResult, gahash)
                # simi = SimilarityMatrix()
                # # # mapping seq 粒度
                # print('buildMatrix')
                # simi.buildMatrix(v0FIMDeletedMethodSeqBean,v1FIMSeqBeanList,deletedMethod)
                # print('queryMat')
                # listOfRankedPaths,disList = simi.queryMat()
                # print('getIndex')
                # index = simi.getIndex(listOfRankedPaths,disList,mappedMethod)
                # print(index)
                # org.jsoup.select.Elements.get(int) 自己匹配自己    
                # org.elasticsearch.action.bulk.BulkItemResponse.failed()
                # redis.clients.jedis.JedisPoolConfig.setMaxActive(int)

run()

# org.apache.lucene__fdse__lucene-core__fdse__b441e2
#     3.6.2__fdse__4.0.0
#     org.apache.lucene.util.NumericUtils.floatToPrefixCoded(float)
#     Cannot found truth
#     org.apache.lucene.util.NumericUtils.doubleToPrefixCoded(double)
#     Cannot found truth
#     org.apache.lucene.document.NumericField.setIntValue(int)
#     Cannot found truth
#     org.apache.lucene.document.NumericField.setLongValue(long)
#     org.apache.lucene.document.NumericField.setDoubleValue(double)
#     Cannot found truth
# org.jsoup__fdse__jsoup__fdse__a363ec
# 1.7.2__fdse__1.13.1
#     org.jsoup.select.Elements.get(int)
#     Cannot found truth
# org.elasticsearch__fdse__elasticsearch__fdse__29148e
#     0.20.6__fdse__1.2.1
#     V1 FIM len: 603
#     org.elasticsearch.action.search.SearchResponse.hits()
#     org.elasticsearch.action.bulk.BulkItemResponse.failed()
#     1.5.1__fdse__2.0.0
#     V1 FIM len: 562
#     org.elasticsearch.common.settings.Settings.settingsBuilder()
# 0.20.6__fdse__5.1.1
#     org.elasticsearch.action.bulk.BulkItemResponse.failed()
#     Cannot found truth
# redis.clients__fdse__jedis__fdse__8ce424
#     2.2.1__fdse__3.3.0
#     redis.clients.jedis.JedisPoolConfig.setMaxActive(int)
#     Cannot found truth