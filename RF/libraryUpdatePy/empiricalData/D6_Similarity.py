from typing import List, Tuple, Dict, Set
from empiricalData.DataBean.BeanAPISeq import BeanAPISeq
from empiricalData.DataBean.BeanAPI import BeanAPI
from functools import cmp_to_key
from empiricalData.SimilarityBase import SimilarityBase
from empiricalData.Similarity2 import Similarity2
###
#
#  
#   切换相似度比较方法
###
simiInstance = None

def mapAPIBySimilarity(src:Dict[str,List[BeanAPISeq]],dst_all:List[BeanAPISeq]):
    global simiInstance
    if simiInstance == None:
        simiInstance = Similarity2()
    if len(src['usage']) == 0:
        return
    result = []
    for beanAPISeq in src['usage']:
        # rankedResult = SimilarityBase.findSimilaryRankDesc(beanAPISeq,dst_all)
        rankedResult = simiInstance.findSimilaryRankDesc(beanAPISeq,dst_all)
        simiMap = {}
        simiMap['original_seq_id'] = beanAPISeq.getId()
        simiMap['dst_seq_map'] = rankedResult
        result.append(simiMap)
    return result
