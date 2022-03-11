from empiricalData.DataBean.BeanAPISeq import BeanAPISeq
from empiricalData.DataBean.BeanAPI import BeanAPI
from functools import cmp_to_key
from typing import List, Tuple, Dict, Set

class SimilarityBase(object):

    def __init__(self):
        pass
    ###
    #
    #  
    #
    ###
    @staticmethod
    def similarityValue(seq:BeanAPISeq,seq2:BeanAPISeq):
        aList = []
        bList = []
        for beanAPI in seq.getBeanAPIList():
            aList.append(beanAPI.getAPIName())
        for beanAPI in seq2.getBeanAPIList():
            bList.append(beanAPI.getAPIName())
        a = set(aList)
        b = set(bList)
        inter = a & b
        return len(inter)*1.0/len(b)

    @staticmethod
    def mycmpSim(x:BeanAPISeq,y:BeanAPISeq):
        # desc
        simA = x[1]
        simB = y[1]
        if simA < simB:
            return 1
        else:
            return -1
    ###
    #
    #  
    #
    ###
    @staticmethod
    def findSimilaryRankDesc(seq:BeanAPISeq,tbl:List[BeanAPISeq]):
        di = {}
        result = {}
        # similarity
        for beanAPISeq in tbl:
            sim = SimilarityBase.similarityValue(seq,beanAPISeq)
            if sim <= 0.000001:
                continue
            result[beanAPISeq] = sim
            # simStr = '%.8f' % sim

        # ranking, new list from result
        ranked = sorted(result.items(),key=cmp_to_key(SimilarityBase.mycmpSim))
        return ranked
