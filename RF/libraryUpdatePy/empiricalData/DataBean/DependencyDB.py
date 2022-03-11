from typing import List, Tuple, Dict

class DependencyDB(object):

    def __init__(self,depDb):
        #               project  lib
        self.depDb:Dict[str,List[str]] = depDb
        
        self.libVersionUsageDesc = None
    
    def depByLibVersionUsageDesc(self):
        if self.libVersionUsageDesc != None:
            return self.libVersionUsageDesc
        versionMap = {}
        for proj in self.depDb:
            data = self.depDb[proj]
            for jar in data:
                data2 = jar.split("__fdse__")
                gaHash = data2[0] + "__fdse__" + data2[1] +"__fdse__" + data2[2]
                version = data2[-1]
                if gaHash not in versionMap:
                    versionMap[gaHash] = {}
                if version not in versionMap[gaHash]:
                    versionMap[gaHash][version] = 0
                versionMap[gaHash][version] += 1
        # for gaHash in versionMap:
        #     versionMapList = sorted(versionMap[gaHash].items(), key=lambda item:item[1], reverse=True)
        #     newDict = {}
        #     for tup in versionMapList:
        #         version = tup[0]
        #         num = tup[1]
        #         newDict[version] = num
        #     versionMap[gaHash] = newDict
        self.libVersionUsageDesc = versionMap
        return self.libVersionUsageDesc
