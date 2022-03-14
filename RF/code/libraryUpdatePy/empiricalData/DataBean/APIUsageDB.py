from typing import List, Tuple, Dict


class OneAPIInvocationSpot(object):

    def __init__(self,name,loc):
        self.name:str = name
        self.loc:str = loc


class OneLineInvocationSpotList(object):

    def __init__(self,loc, apiInvocationList):
        self.loc:str = loc
        self.apiInvocationList:List[OneAPIInvocationSpot] = apiInvocationList


class APIUsageInOneMethod(object):

    #   List[Tuple[str,List[str]]]
    def __init__(self, tupList):
        self.usageInOneMethodList:List[OneLineInvocationSpotList] = []
        for tup in tupList:
            loc = tup[0]
            apiList = tup[1]
            apiInvocationSpotList = []
            for api in apiList:
                item = OneAPIInvocationSpot(api,loc)
                apiInvocationSpotList.append(item)
            li = OneLineInvocationSpotList(loc,apiInvocationSpotList)
            self.usageInOneMethodList.append(li)



class APIUsageDB(object):


    # #                            project ->file -> jarName -> method  -> APIUsageInOneMethod
    def __init__(self, usageDb:Dict[str,Dict[str,Dict[str,Dict[str,APIUsageInOneMethod]]]]):
        self.usageDB = usageDb
    

    # 目的1: 排除掉dep usage很高，但是抽不出api的
    # usageDb: projectFile->srcFile->jarName->method->list<lineNumer,list<call>>
    # output: gaHash->version->cnt
    def countAPIUsageNumber(self):
        # todo 
        TRH = 0
        usageDb = self.usageDB
        gavUsageCount:Dict[str,Dict[str,int]] = {}
        for projectFile in usageDb:
            for srcFile in usageDb[projectFile]:
                for jarName in usageDb[projectFile][srcFile]:
                    tempRemovalList = []
                    gavhashversion = jarName.split("__fdse__")
                    gaHash = gavhashversion[0] + "__fdse__" + gavhashversion[1] + "__fdse__" + gavhashversion[2]
                    version = gavhashversion[3]

                    if not gaHash in gavUsageCount:
                        gavUsageCount[gaHash] = {}
                    if not version in gavUsageCount[gaHash]:
                        gavUsageCount[gaHash][version] = 0

                    usageCountTotal = 0
                    for method in usageDb[projectFile][srcFile][jarName]:
                        cnt = 0
                        usageSeq = usageDb[projectFile][srcFile][jarName][method]
                        for entry in usageSeq:
                            ln = entry[0]
                            call = entry[1]
                            cnt += len(call)

                        if cnt <= TRH:
                            tempRemovalList.append(method)
                        else:
                            usageCountTotal += cnt
                    
                    gavUsageCount[gaHash][version] = usageCountTotal
                    for method in tempRemovalList:
                        usageDb[projectFile][srcFile][jarName].pop(method)
        return gavUsageCount







