# -*- coding: utf-8 -*- 
import abc
from ILogic import ILogic
import JavaDocUtil
import requests
import json
from typing import List, Tuple, Dict, Set

class TestOneRowLogic(ILogic):

    def initBeforeExcel(self,portId):
        self.portId = portId

    def queryMappedMethodMain(self,GA,VPAIR,method,mappingSource,mappedMethods,runType):
        print(GA)
        print(VPAIR)
        methods = []
        methods.append(method)
        mappedMethodsRes = self.queryMappingMethod(GA,VPAIR,methods,runType)
        if mappedMethodsRes != None:
            for item in mappedMethodsRes:
                if 'find_map' in item:
                    print('-------')
                    print(item['method'])
                    print(item['find_map'])
                    print(item['mapped_method'])
        else:
            print('tool: no map')
        

    # exec post
    def queryMappingMethod(self,GA,versionPair,methods,runType):
        if len(methods) == 0:
            return []
        versions = JavaDocUtil.getVersions(GA,versionPair)
        result = self.postQuery(GA,versionPair,versions,methods,runType)
        return result

    ## 
    def postQuery(self,GA,versionPair,versions,methods,runType):
        postStr = {}
        postStr['GA'] = GA
        postStr['version_pair'] = versionPair
        postStr['methods'] = methods
        postStr['versions'] = versions
        postStr['phase_name'] = runType
        req = requests.post('http://10.176.34.86:%s/deleted_method_mapping' % self.portId,json=postStr)
        content = req.content
        j = json.loads(content)
        return j


# 108