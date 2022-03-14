import os
import matplotlib
import json
import math
from D_genApiUsageSequence import genSequence
from B_genGavs import getDepByProjJson
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from typing import List, Tuple, Dict
from functools import cmp_to_key
from D2_UsageSelection import mycmpVersionTup
from packaging import version
from D4_jarDiff import postToJarDiffServer

class RQ1_1Data(object):

    def __init__(self):
        pass

    def loadDB(self,root,dbData):
        depDbName:str = root + '/2020-data/dep-db-%s.json' % dbData 
        usageDbName:str = root + '/2020-data/usage-db-%s.json' % dbData

        depDb:Dict[str,List[str]] = getDepByProjJson(depDbName, False)
        usageDB:Dict[str,Dict[str,Dict[str,Dict[str,List[Tuple[str,List[str]]]]]]] = genSequence(usageDbName, False)
        return depDb, usageDB

    def dumpRQ1Data(self):
        rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate'
        dbData = '21-1-14'
        depDb, apiDb = self.loadDB(rootPath, dbData)
        result = {}
        for project in depDb:
            for libGAHV in depDb[project]:
                idx = libGAHV.rfind('__fdse__')
                gah = libGAHV[0:idx]
                v = libGAHV[idx+8:]
                if gah not in result:
                    result[gah] = {}
                    result[gah]['dep'] = 0
                result[gah]['dep'] += 1
        #  quartz-scheduler__fdse__quartz_2020-09-20_parent_method.json

        # Dict[str,Dict[str,Dict[str,Dict[str,List[Tuple[str,List[str]]]]]]]
        for parentMethodFileName in apiDb:
            # quartz-plugins/src/test/java/org/quartz/integrations/tests/QTZ225_SchedulerClassLoadHelperForPlugins_Test.java
            for srcFileName in apiDb[parentMethodFileName]:
                # junit__fdse__junit-dep__fdse__2a5a4e__fdse__4.8.2__fdse__jar/junit-dep-4.8.2.jar
                for jarFileName in apiDb[parentMethodFileName][srcFileName]:
                    data = jarFileName.split('/')[0].split('__fdse__')
                    gah = data[0] + '__fdse__' + data[1] + '__fdse__' + data[2]
                    if 'api' not in result[gah]:
                        result[gah]['api'] = 0

                    for srcFileMethod in apiDb[parentMethodFileName][srcFileName][jarFileName]:
                        for tup in apiDb[parentMethodFileName][srcFileName][jarFileName][srcFileMethod]:
                            lineNumber = tup[0]
                            apiList = tup[1]
                            l = len(apiList)
                            result[gah]['api'] = result[gah]['api'] + l
        with open(rootPath +'/2020-data/RQ-data/RQ1-1.json','w') as f:
            json.dump(result,f,indent=4)
        
    def plot(self):
        rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-data/'
        path = rootPath + 'RQ-data/RQ1-1.json'
        with open(path,'r') as f:
            j = json.load(f)
        apiSum = 0
        depSum = 0
        keys = list(j.keys())
        rmkeys = []
        for gah in keys:
            if 'api' in j[gah]:
                api = j[gah]['api']
            else:
                api = 0

            dep = j[gah]['dep']
            if api ==0 or dep == 0:
                rmkeys.append(gah)
                continue
            
            apiSum = api + apiSum
            depSum = dep + depSum
        rmkeys.append('junit__fdse__junit__fdse__03dca4')
        newKeys = []
        for key in j:
            if not key in rmkeys:
                newKeys.append(key)

        matrix = np.zeros((len(newKeys),2))
        for i in range(0,len(newKeys)):
            gah = newKeys[i]
            if 'api' in j[gah]:
                api = j[gah]['api']
            else:
                api = 0
            dep = j[gah]['dep']
            matrix[i][0] = dep*1.0/depSum
            matrix[i][1] = api*10.0/apiSum
            if matrix[i][1]>3.5:
                print(gah)
            # matrix[i][0] = math.log(dep*1.0/depSum)

        fig, ax = plt.subplots()
        ax.scatter(matrix[:,0], matrix[:,1], alpha=0.5)
        ax.set_xlabel(r'used by projects', fontsize=15)
        ax.set_ylabel(r'api used by projects', fontsize=15)
        ax.set_title('Volume and percent change')
        ax.grid(True)
        fig.tight_layout()
        plt.savefig(rootPath + 'RQ-data/rq1-1.png',format='png')

class RQ1_2Data(object):

    def dumpRQ1Data(self):
        rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate'
        with open(rootPath + '/2020-data/rankedGAVersionAndAPICount-topNiGAVersionPair-21-1-14-filter.json','r') as f:
            j = json.load(f)
        #                               gah            version 
        rankedGAVersionAndAPICount:Dict[str,List[Tuple[str,int,int]]] = j['rankedGAVersionAndAPICount']
        topNiGAVersionPair = j['topNiGAVersionPair']
        majors = {}
        micros = {}
        minors = {}
        result = {}
        for ga in rankedGAVersionAndAPICount:
            result[ga] = {}
            versionTupsList = rankedGAVersionAndAPICount[ga]
            versionTupsList.sort(key=cmp_to_key(mycmpVersionTup))
            majors = {}
            micros = {}
            minors = []
            result[ga]['major'] = majors
            result[ga]['micro'] = micros
            result[ga]['minor'] = minors
            for vtups in versionTupsList:
                parsedV = version.parse(vtups[0])
                if hasattr(parsedV, 'major'):
                    major = str(parsedV.major)
                elif hasattr(parsedV,'micro'):
                    micro = str(parsedV.micro)
                elif hasattr(parsedV, 'minor'):
                    minor = str(parsedV.minor)
                # todo
                if major not in majors:
                    majors[major] = []
                majors[major].append(vtups[0])
                # key = major
                # if key not in micros:
                    # micros[key] = []
                # micros[key].append(vtups[0])
                key = major + '.' + micro
                if key not in micros:
                    micros[key] = []
                micros[key].append(vtups[0])

                minors.append(vtups[0])
            majorCmpList = []
            for mV in majors:
                majorCmpList.append(majors[mV][0])
            microCmpList = []
            for mV in micros:
                microCmpList.append(micros[mV][0])
            minorsCmpList = minors
        print('a')

            # postToJarDiffServer()

        
            


     
# RQ 1-1
# a = RQ1_1Data()
# # a.dumpRQ1Data()
# a.plot()
a = RQ1_2Data()
a.dumpRQ1Data()






