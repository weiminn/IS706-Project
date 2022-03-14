from empiricalData.DataBean.BeanAPISeq import BeanAPISeq
from empiricalData.DataBean.BeanAPI import BeanAPI
from functools import cmp_to_key
from typing import List, Tuple, Dict, Set

class Similarity2(object):

    def __init__(self):
        pass
    ###
    #
    #  
    #
    ###
    def similarityValue(self,seq:BeanAPISeq,seq2:BeanAPISeq):
        aList = []
        bList = []
        for beanAPI in seq.getBeanAPIList():
            # if "(" not in beanAPI.getAPIName():
                # continue
            aList.append(beanAPI.getAPIName())
        for beanAPI in seq2.getBeanAPIList():
            # if "(" not in beanAPI.getAPIName():
            #     continue
            bList.append(beanAPI.getAPIName())
        a = set(aList)
        b = set(bList)
        inter = a & b
        if len(b) == 0:
            return 0.0
        return len(inter)*1.0/len(b)

    def mycmpSim(self,x:BeanAPISeq,y:BeanAPISeq):
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
    #  输出的为map.items的列表， List[Tuple[BeanAPISeq,int]]
    ###
    def findSimilaryRankDesc(self,seq:BeanAPISeq,tbl:List[BeanAPISeq]):
        di = {}
        result = {}
        # similarity
        for beanAPISeq in tbl:
            sim = self.similarityValue(seq,beanAPISeq)
            if sim <= 0.000001:
                continue
            result[beanAPISeq] = sim
            # simStr = '%.8f' % sim

        # ranking, new list from result
        ranked = sorted(result.items(),key=cmp_to_key(self.mycmpSim))
        return ranked
