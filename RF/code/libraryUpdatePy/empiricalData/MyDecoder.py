import os
import json
from empiricalData.DataBean.BeanAPISeq import BeanAPISeq
from empiricalData.DataBean.BeanAPI import BeanAPI
from empiricalData.DataBean.RankedDependencyUsage import GAVUsage

from ToolMappingLogic import ToolMappingLogic
from ExcelRow  import RowData,TableIICell
class MyDecoder(object):

    # finalResult 的格式
    def decodeToSeqBeanList(self,seqBeanJson):
        seqList = []
        for seqBeanStr in seqBeanJson:
            idd = seqBeanStr['id']
            apiSeq = seqBeanStr['apiSeq']
            freV1 = seqBeanStr['frequencyV1']
            freV2 = seqBeanStr['frequencyV2']
            beanAPISeq =  BeanAPISeq('c')
            totalFrequencySizeV1 = seqBeanStr['totalFrequencySizeV1']
            totalFrequencySizeV2 = seqBeanStr['totalFrequencySizeV2']
            beanAPISeq.setFrequencyV1(freV1)
            beanAPISeq.setFrequencyV2(freV2)
            beanAPISeq.setTotalUsageSizeV1(totalFrequencySizeV1)
            beanAPISeq.setTotalUsageSizeV2(totalFrequencySizeV2)
            beanAPISeq.setId(idd)
            for api in apiSeq:
                name  = api['api']
                typ = api['changeType']
                beanAPI = BeanAPI(name)
                beanAPI.setChangeType(typ)
                beanAPISeq.addBeanAPI(beanAPI)
            seqList.append(beanAPISeq)
        return seqList

    # FIM   格式
    def decodeToSeqBeanListFIM(self,seqJson):
        usageSeq = seqJson['usage_seq']
        fre = seqJson['frequency']
        beanAPISeq = BeanAPISeq('c')
        beanAPISeq.setFrequencyV1(fre)
        for api in usageSeq:
            beanAPI = BeanAPI(api)
            beanAPISeq.addBeanAPI(beanAPI)
        return beanAPISeq

    def decodeCountOverview(self,s):
        # :List[Tuple[str,List[GAVUsage]]]
        newResult = []
        for entry in s:
            gaHash = entry[0]
            gavUsage = entry[1]
            newList = []
            for item in gavUsage:
                gavUsage = GAVUsage(item['gaHash'],item['version'],item['depNum'],item['apiUsageNum'])
                newList.append(gavUsage)
            newTup = (gaHash,newList)
            newResult.append(newTup)
        return newResult

    def decodeToolMappingLogic(self,s):
        pass




