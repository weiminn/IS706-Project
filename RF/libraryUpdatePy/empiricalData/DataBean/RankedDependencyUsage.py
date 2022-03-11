from typing import List, Tuple, Dict

from functools import cmp_to_key

class GAVUsage(object):

    def __init__(self,gahash, version, depNum, apiUsageNum):
        self.gaHash = gahash
        self.version = version
        self.depNum = depNum
        self.apiUsageNum = apiUsageNum

    def setDepNum(self,num):
        self.depNum = num
    
    def setAPIUsageNum(self,num):
        self.apiUsageNum = num


class RankedDependencyUsage(object):


    def __init__(self):
        #               ga
        self.usage:Dict[str,List[GAVUsage]] = {}
    

    def setGAHashAndUsageMapping(self,gaHash,di):
        self.usage[gaHash] = di


    def cmp22(self,gaEntryA:Tuple[str,List[GAVUsage]], gaEntryB):
        cntA = 0
        for gavUsage in gaEntryA[1]:
            apiNum = gavUsage.apiUsageNum
            cntA += apiNum

        cntB = 0
        for gavUsage in gaEntryB[1]:
            apiNum = gavUsage.apiUsageNum
            cntB += apiNum  
        # desc
        if cntA < cntB:
            return 1
        else:
            return -1

    def rankByAPIUsageNumber(self):
        res:List[Tuple[str,List[GAVUsage]]] = sorted(self.usage.items(),key=cmp_to_key(self.cmp22))
        return res
    #                                           ga
    def filterLowAPIUsage(self,res:List[Tuple[str,List[GAVUsage]]], Th):
        newRes = []
        for tup in res:
            gaHash = tup[0]
            gavUsageList = tup[1]
            newList = []
            for gavUsage in gavUsageList:
                # newList.append(gavUsage)
                if gavUsage.apiUsageNum > Th:
                    newList.append(gavUsage)
                else:
                    if gaHash =='org.elasticsearch__fdse__elasticsearch__fdse__29148e':
                        versionList = ['1.3.4','5.6.0','2.4.3','2.0.0','0.20.6','1.2.1','5.1.1','2.2.1','3.3.0','1.7.2','1.13.1']
                        if gavUsage.version in versionList:
                            newList.append(gavUsage)
                    if gaHash == 'com.google.guava__fdse__guava__fdse__a1e0af':
                        if gavUsage.version == '13.0.1' or gavUsage.version =='18.0':
                            newList.append(gavUsage)
                    if gaHash == 'org.apache.lucene__fdse__lucene-core__fdse__b441e2':
                        if gavUsage.version == '3.5.0' or gavUsage.version == '3.6.2' or gavUsage.version == '4.0.0':
                            newList.append(gavUsage)
                    if gaHash == 'redis.clients__fdse__jedis__fdse__8ce424':
                        if gavUsage.version == '2.2.1' or gavUsage.version == '3.3.0':
                            newList.append(gavUsage)
                    if gaHash == 'org.jsoup__fdse__jsoup__fdse__a363ec':
                        if gavUsage.version == '1.7.2' or gavUsage.version == '1.13.1':
                            newList.append(gavUsage)
            if len(newList) !=0:
                newTup = (tup[0],newList)
                newRes.append(newTup)

        return newRes


