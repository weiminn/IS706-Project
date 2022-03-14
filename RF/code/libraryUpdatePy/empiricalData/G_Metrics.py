
from typing import List, Tuple, Dict, Set
from empiricalData.DataBean.BeanAPISeq import BeanAPISeq
from empiricalData.DataBean.BeanAPI import BeanAPI
import sys
from empiricalData.MetricResult import MethodMetric,MetricResult

class Metrics(object):

    ## FIM拿到的结果分成了5个部分
    ## a_only_modified c_modified a_has_deleted a_all_same c_all_same

    def __init__(self):
        pass

    #                                 key      GA       Version 'version_pair'
    #                                                            'usage'
    # finalResult[key][ga][version]['usage']:List[BeanAPISeq]
    #
    def metrics(self,finalResult:Dict[str,Dict[str,Dict[str,Dict]]]):
        gavSum = self.allGAs(finalResult)
        metricResult = {}
        for gav in gavSum:
            data = gav.split("__fdsefdse__")
            ga = data[0]
            vpair = data[1]
            total_FIM_size:Tuple[int,int] = self.getTotalFIMSize(finalResult,ga,vpair)
            modifiedAPIAndBeanAPISeqMap: Dict[str,List[BeanAPISeq]] = self.getModifiedAPIsDistinct(finalResult,ga,vpair)
            mr = MetricResult(ga,vpair)
            for modifiedAPI in modifiedAPIAndBeanAPISeqMap:
                beanAPISeqsWithModifiedAPI = modifiedAPIAndBeanAPISeqMap[modifiedAPI]
                m2 = len(beanAPISeqsWithModifiedAPI) / (total_FIM_size[0] + total_FIM_size[1])
                support = 0.0
                for beanAPISeq in beanAPISeqsWithModifiedAPI:
                    support += beanAPISeq.getSupport()
                m3 = support / len(beanAPISeqsWithModifiedAPI)
                minSupport, maxSupport = self.getMinMaxSupport(beanAPISeqsWithModifiedAPI)
                m4 = self.getOffset(minSupport,maxSupport,m3)
                mm = MethodMetric(modifiedAPI)
                mm.setM(m2,m3,m4)
                mr.addMethodMetric(mm)
            if not ga in metricResult:
                metricResult[ga] = {}
            if not vpair in metricResult[ga]:
                metricResult[ga][vpair] = mr
        return metricResult
        
    def getOffset(self,minS,maxS,m):
        if (maxS-minS) < 0.0001:
            return 0.0
        return (m-minS)/(maxS-minS)

    def getTotalFIMSize(self,finalResult,ga,vpair):
        key = 'a_only_modified'
        if key in finalResult and ga in finalResult[key] and vpair in finalResult[key][ga]:
            return finalResult[key][ga][vpair]['total_FIM_size']
        key = 'c_modified'
        if key in finalResult and ga in finalResult[key] and vpair in finalResult[key][ga]:
            return finalResult[key][ga][vpair]['total_FIM_size']
        key = 'a_has_deleted'
        if key in finalResult and ga in finalResult[key] and vpair in finalResult[key][ga]:
            return finalResult[key][ga][vpair]['total_FIM_size']
        return 0.0

    def getMinMaxSupport(self,beanAPISeqsWithModifiedAPI:List[BeanAPISeq]):
        maxV = sys.float_info.max #最大值
        minV = - sys.float_info.max #最小值
        max = minV
        min = maxV
        for beanAPISeq in beanAPISeqsWithModifiedAPI:
            s = beanAPISeq.getSupport()*1.0
            if s > max:
                max = s
            if s < min:
                min = s
        return min,max

    


    def getModifiedAPIsDistinct(self,finalResult,ga,v) -> Dict[str,BeanAPISeq]:
        result:Dict[str,List[BeanAPISeq]] = {}
        key = 'a_only_modified'
        self.getModifiedAPIsDistinctOne(finalResult,ga,v,result,key)
        key = 'c_modified'
        self.getModifiedAPIsDistinctOne(finalResult,ga,v,result,key)
        key = 'a_has_deleted'
        self.getModifiedAPIsDistinctOne(finalResult,ga,v,result,key)

        return result
    
    def getModifiedAPIsDistinctOne(self,finalResult,ga,v,result:Dict[str,List[BeanAPISeq]],key):
        if key in finalResult and ga in finalResult[key] and v in finalResult[key][ga]:
            beanAPISeqList = finalResult[key][ga][v]['usage']
            for beanAPISeq in beanAPISeqList:
                beanAPIList =  beanAPISeq.getBeanAPIList()
                for beanAPI in beanAPIList:
                    if "modified" == beanAPI.getChangeType():
                        if beanAPI.getAPIName() not in result:
                            result[beanAPI.getAPIName()] = []
                        if beanAPISeq not in result[beanAPI.getAPIName()]:
                            result[beanAPI.getAPIName()].append(beanAPISeq)

    def allGAs(self,finalResult):
        aOnlyModified = finalResult['a_only_modified']
        cModified = finalResult['c_modified']
        aHaveDeleted = finalResult['a_has_deleted'] 
        gaSet = set()
        for ga in aOnlyModified:
            for v in aOnlyModified[ga]:
                gaSet.add(ga+"__fdsefdse__"+v)
        for ga in cModified:
            for v in cModified[ga]:
                gaSet.add(ga+"__fdsefdse__"+v)
        for ga in aHaveDeleted:
            for v in aHaveDeleted[ga]:
                gaSet.add(ga+"__fdsefdse__"+v)
        return list(gaSet)

