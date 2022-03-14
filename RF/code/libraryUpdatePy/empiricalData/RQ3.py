import json
from typing import List, Tuple, Dict
from BeanAPISeq import BeanAPISeq
from BeanAPI import BeanAPI

class RQ3(object):

    def dumpRQ3Data(self):
        rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-data/'
        finalResultName = 'usage_final_result-21-1-14-filter.json'
        outputRQ3Json = 'RQ-data/RQ3.json'
        self.dumpRQ3(rootPath,finalResultName,outputRQ3Json)


    def dumpRQ3(self,rootPath,finalResultName,outputRQ3Json):
        #                  ga     vPair    modifiedAPI
        with open(rootPath +'/' + finalResultName,'r') as f:
            j = json.load(f)
            modifiedAPI:Dict[str,Dict[str,List[str]]] = self.getDistinctModifiedAPI(j)
        with open(rootPath +'/'+ outputRQ3Json,'w') as f:
            json.dump(modifiedAPI,f,indent=4)

    def getDistinctModifiedAPI(self,finalResult:Dict[str,Dict[str,Dict[str,Dict]]]):
        gavSum = self.allGAs(finalResult)
        metricResult = {}
        for gav in gavSum:
            data = gav.split("__fdsefdse__")
            ga = data[0]
            if not ga in metricResult:
                metricResult[ga] = {}
            vpair = data[1]
            modifiedAPIAndBeanAPISeqMap: Dict[str,List[str]] = self.getModifiedAPIsDistinct(finalResult,ga,vpair)
            if not vpair in metricResult[ga]:
                metricResult[ga][vpair] = modifiedAPIAndBeanAPISeqMap
        return metricResult
    
    def getModifiedAPIsDistinct(self,finalResult,ga,v) -> Dict[str,BeanAPISeq]:
        # result:Dict[str,List[BeanAPISeq]] = {}
        resultA = set()
        resultC = set()
        res = {}
        key = 'a_only_modified'
        self.getModifiedAPIsDistinctOne(finalResult,ga,v,resultA,key)
        key = 'c_modified'
        self.getModifiedAPIsDistinctOne(finalResult,ga,v,resultC,key)
        key = 'a_has_deleted'
        self.getModifiedAPIsDistinctOne(finalResult,ga,v,resultA,key)
        res['a'] = list(resultA)
        res['c'] = list(resultC)

        return res

    def getModifiedAPIsDistinctOne(self,finalResult,ga,v,result:Dict[str,List[BeanAPISeq]],key):
        if key in finalResult and ga in finalResult[key] and v in finalResult[key][ga]:
            beanAPISeqList = finalResult[key][ga][v]['usage']
            for beanAPISeq in beanAPISeqList:
                seqId = beanAPISeq['id']
                beanAPIs =  beanAPISeq['apiSeq']
                for beanAPI in beanAPIs:
                    if "modified" == beanAPI['changeType']:
                        apiName = beanAPI['api']
                        if apiName not in result:
                            result.add(apiName)
                        # if apiName not in result:
                        #     result[apiName] = []
                        # isIn = False
                        # for tmp in result[apiName]:
                        #     if tmp['id'] == seqId:
                        #         isIn = True
                        #         break
                        # if not isIn:
                            # result.append(beanAPISeq)


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

    def loadRQ3Json(self):
        rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-data/'
        outputRQ3Json = 'RQ-data/RQ3.json'
        with open(rootPath + outputRQ3Json,'r') as f:
            j = json.load(f)
        cnt = 0
        for ga in j:
            for vpair in j[ga]:
                a = j[ga][vpair]['a']
                c = j[ga][vpair]['c']
                aset = set(a)
                cset = set(c)
                m = set()
                for i in aset:
                    m.add(i)
                for i in cset:
                    m.add(i)
                cnt += len(m)
        print(cnt)

a = RQ3()
# a.dumpRQ3Data()
a.loadRQ3Json()
