from typing import List, Tuple, Dict,Set
from empiricalData.DataBean.BeanAPISeq import BeanAPISeq
from empiricalData.DataBean.BeanAPI import BeanAPI
from functools import cmp_to_key

def toSet(seqList1:List[List[str]]):
    seqList1Set:List[Set[str]] = []
    for seq in seqList1:
        seqSet1 = set(seq['usage_seq'])
        seqList1Set.append(seqSet1)
    return seqList1Set

# 两个集合做差集和交集
def seqIntersection(seqList1:List[List[str]],seqList2:List[List[str]]):
    seq1Set:List[Set[str]] = toSet(seqList1) 
    seq2Set:List[Set[str]] = toSet(seqList2)
    intersection = []
    seq1_seq2 = []
    seq2_seq1 = []
    tmpEqualSetInSet2 = []
    for subSet in seq1Set:
        found = False
        for subSet2 in seq2Set:
            res = isSetEqual(subSet,subSet2)
            if res:
                found = True
                break
        if found:
            # c
            tmpEqualSetInSet2.append(subSet2)
            intersection.append(subSet)
        else:
            # a
            seq1_seq2.append(subSet)
    for tmpSet in seq2Set:
        if tmpSet not in tmpEqualSetInSet2:
            # b
            seq2_seq1.append(tmpSet)

    return intersection,seq1_seq2,seq2_seq1

def isSetEqual(l1:Set[str],l2:Set[str]):
    if len(l1) != len(l2):
        return False
    isDifferent = False
    for api in l1:
        if api in l2:
            continue
        else:
            isDifferent = True
            break
    
    # isDifferent = False - > equal found subSet = subSet2
    # isDifferent = True - > not equal 
    return not isDifferent



# deleted 的方法加上标注
def taintDeletedNode(seqList:List[List[str]],deletedList:List[str]) -> List[List[Tuple[str,str]]]:
    result,cnt = taintNode(seqList,deletedList,"deleted")
    return result,cnt

def taintModifiedNode(seqList:List[List[str]],deletedList:List[str]) -> List[List[Tuple[str,str]]]:
    result,cnt = taintNode(seqList,deletedList,"modified")
    return result,cnt


def taintNode(seqList:List[List[str]],taintNodes:List[str],typeS:str) -> List[List[Tuple[str,str]]]:
    taintSets = set(taintNodes)
    result:List[List[Tuple[str,str]]] = []
    cnt = 0
    for seq in seqList:
        tmpSet = set(seq)
        intersection = taintSets & tmpSet
        tmpResult = []
        isHave = False
        for s in seq:
            if s in intersection:
                tmpResult.append((s,typeS))
                isHave = True
                cnt +=1
            else:
                tmpResult.append((s,""))
        if isHave:
            result.append(tmpResult)
    return result,cnt
#                                       api,change.type
def taintNode2(seqList:List[BeanAPISeq],taintNodes:List[str],typeS:str):
    taintSets = set(taintNodes)
    cnt = 0
    for seq in seqList:
        beanAPIList:List[BeanAPI] = seq.getBeanAPIList()
        for beanAPI in beanAPIList:
            apiFullInfo = beanAPI.getAPIName()
            data = apiFullInfo.split('__fdse__')
            api = data[-1]
            if api in taintNodes:
                cnt+=1
                beanAPI.setChangeType(typeS)
    return cnt


# @deprecated
def mapAAPIContent(finalResult,v1_v2,ga,v1,v2,v1Andv2,v2_v1):
    tainted_v1_v2List,taintCnt = taintDeletedNode(v1_v2,diffJson['deleted'])
    if taintCnt != 0:
        if ga not in checkDeletedAPI:
            checkDeletedAPI[ga] = {}
        if v1 + "   " + v2 not in checkDeletedAPI[ga]:
            checkDeletedAPI[ga][v1 + "   " + v2] = {}
        checkDeletedAPI[ga][v1 + "   " + v2]['version_pair'] = v1 + "   " + v2
        checkDeletedAPI[ga][v1 + "   " + v2]['usage'] = tainted_v1_v2List
        
        #### deleted API -> 找mapping
        result = mappingDeletedAPI(tainted_v1_v2List,v1Andv2,v2_v1)
        checkDeletedAPI[ga][v1 + "   " + v2]['simi_map'] = result
        ###### end
# @deprecated
# modify的API，统计一下这个序列的frequency信息
def mapCAPIContent(checkModifiedAPI,v1Andv2,frequentUsageSet,ga,v1,v2):
    # v1 v2 都调用并且有modify
    tainted_v1Andv2List, taintCnt2 = taintModifiedNode(v1Andv2,diffJson['modified'])
    if taintCnt2 != 0:
        FIM_fre_v1 = frequentUsageSet[ga][v1]['FIM_fre']
        # tainted 的api调用序列节点增加frequency
        tainted_v1Andv2ListWithFrequency = addFrequency(FIM_fre_v1,tainted_v1Andv2List)
        if ga not in checkModifiedAPI:
            checkModifiedAPI[ga] = {}
        if v1 + "   " + v2 not in checkModifiedAPI[ga]:
            checkModifiedAPI[ga][v1 + "   " + v2] = {}
        checkModifiedAPI[ga][v1 + "   " + v2]['version_pair'] = v1 + "   " + v2
        checkModifiedAPI[ga][v1 + "   " + v2]['usage'] = tainted_v1Andv2ListWithFrequency


def mycmpFre(x:Tuple,y:Tuple):
    beanAPISeqX = x[0]
    simiValueX = x[1]
    beanAPISeqY = y[0]
    simiValueY = y[1]
    idX = beanAPISeqX.getId()
    idY = beanAPISeqY.getId()
    freA = beanAPISeqX.getFrequency()
    freB = beanAPISeqY.getFrequency()
    # desc
    if freA < freB:
        return 1
    else:
        return -1

def queryFIM(FIM_fre,apiList:List[str]):
    fre = 0
    apiListSet = set(apiList)
    for di in FIM_fre:
        seqTbl = di['usage_seq']
        frequency = di['frequency']
        seqTblSet = set(seqTbl)
        if len(apiListSet) == len(seqTblSet) and len(apiListSet & seqTblSet) == len(seqTblSet):
            fre += frequency
        # if len(seqTbl) == len(apiList):
        #     isEqual = True
        #     for i in range(0,len(seqTbl)):
        #         if seqTbl[i] != apiList[i]:
        #             isEqual = False
        #             break
        #     if isEqual:
        #         fre += frequency
    return fre

# sequence 增加frequency
def addFrequency(FIM_fre,totalUsageSize:int, beanAPISeqList:List[BeanAPISeq],v1Orv2):
    result = []
    for beanAPISeq in beanAPISeqList:
        apiList = []
        beanAPIList = beanAPISeq.getBeanAPIList()
        for beanAPI in beanAPIList:
            apiList.append(beanAPI.getAPIName())
        frequency = queryFIM(FIM_fre,apiList)
        if frequency == 0:
            print('ERROR 000000')
        # if beanAPISeq.getFrequency() !=0:
            # print('bean api frenquency not 0--------------')
        if 'v1' == v1Orv2:
            beanAPISeq.setFrequencyV1(frequency)
            beanAPISeq.setTotalUsageSizeV1(totalUsageSize)
        elif 'v2' == v1Orv2:
            beanAPISeq.setFrequencyV2(frequency)
            beanAPISeq.setTotalUsageSizeV2(totalUsageSize)
    

def sortSimiMapBeanSeqList(finalResultGAV:Dict):
    if not 'simi_map' in finalResultGAV:
        return
    simiMap = finalResultGAV['simi_map']
    if simiMap == None or len(simiMap) == 0:
        return
    for entry in simiMap:
        originalSeqId = entry['original_seq_id']
        candidates = entry['dst_seq_map']
        sortedCandidates = sorted(candidates,key=cmp_to_key(mycmpFre))
        entry['dst_seq_map'] = sortedCandidates
    # finalResultGAV['simi_map'] = newList

# seq = ["a","b","c"]
# s1 = []
# s1.append(seq)
# s1.append(["a"])

# seq2 = ["b","c","d"]
# s2 = []
# s2.append(seq2)
# s2.append(["a"])

# res,res2,res3 = seqIntersection(s1,s2)
