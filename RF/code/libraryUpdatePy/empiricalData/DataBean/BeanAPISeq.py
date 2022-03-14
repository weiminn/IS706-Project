from typing import List, Tuple, Dict, Set
from empiricalData.DataBean import BeanAPI
import json

cnt = 0

class BeanAPISeq():

    def __init__(self,abcType):
        global cnt
        self.id = cnt
        self.apiSeq:List[BeanAPI] = []
        self.abc = abcType
        self.frequencyV1 = 0
        self.frequencyV2 = 0
        self.totalFrequencySizeV1 = 0
        self.totalFrequencySizeV2 = 0
        cnt+=1
    
    def setId(self,idd):
        self.id = idd

    def getSupport(self):
        #todo 
        s1 = 1.0 * self.frequencyV1/self.totalFrequencySizeV1
        s2 = 1.0 * self.frequencyV2/self.totalFrequencySizeV1
        return (s1+s2)/2

    def setTotalUsageSizeV1(self,total):
        self.totalFrequencySizeV1 = total
    
    def setTotalUsageSizeV2(self,total):
        self.totalFrequencySizeV2 = total

    def getTotalUsageSizeV1(self):
        return self.totalFrequencySizeV1

    def getTotalUsageSizeV2(self):
        return self.totalFrequencySizeV2
    
    def getId(self):
        return self.id
    
    def addBeanAPI(self,beanAPI:BeanAPI):
        self.apiSeq.append(beanAPI)

    def getBeanAPIList(self):
        return self.apiSeq
    
    def setFrequencyV1(self,fre):
        self.frequencyV1 = fre
    
    def setFrequencyV2(self,fre):
        self.frequencyV2 = fre

    def getFrequencyV1(self):
        return self.frequencyV1
    
    def getFrequency(self):
        return self.frequencyV1 + self.frequencyV2
    
    def getFrequencyV2(self):
        return self.frequencyV2
    
    def  __str__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr

    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr

    def hashCode(self):
        apiList = []
        for beanAPI in self.apiSeq:
            apiList.append(beanAPI.getAPIName())
        li = sorted(apiList)
        s = ''
        for a in li:
            s += a
        return hash(s)


