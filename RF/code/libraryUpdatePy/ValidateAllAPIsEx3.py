import os
import json
import requests
from EmpiricalTop200 import postToJarDiffServer
from JavaDocUtil import getVersions
from functools import cmp_to_key
from empiricalData.D2_UsageSelection import mycmpVersionTup
from typing import List, Tuple, Dict
from packaging import version
from empiricalData.D_genApiUsageSequence import trimAPI

class MergeAPIResult(object):

    def mergeAPIResult(self):
        apiPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/LibAPIOutput/data/api_call/api_call_result_add_ret'
        files = os.listdir(apiPath)
        result = {}
        for file in files:
            if not file.endswith('parent_method.json'):
                continue
            if not file.endswith('.json'):
                continue
            projectName = file.split('_2021')[0]
            if 'j256' in projectName:
                continue
            if 'jhy' in projectName:
                continue
            with open(apiPath +'/' +file,'r') as f:
                j = json.load(f)
            result[projectName] = j 
        print('project size: %d' % len(result))
        # with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/api_call_raw_merge-4-16.json','w') as f:
        #     json.dump(result,f,indent=4)

# a = MergeAPIResult()
# a.mergeAPIResult()

class GenerageVersionPair(object):

    def mycmpVersionTup(self,x,y):
        v1 = x
        v2 = y
        v1 = v1.replace('-android','')
        v1 = v1.replace('-jre','')
        v2 = v2.replace('-android','')
        v2 = v2.replace('-jre','')
        if version.parse(v1) > version.parse(v2):
            return 1
        else:
            return -1

    def distinctLibs(self):
        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/api_call_raw_merge-4-16.json','r') as f:
            j = json.load(f)
        libS = set()
        libCnt = 0
        projectLibDict = {}
        for proj in j:
            for mod in j[proj]:
                for fi in j[proj][mod]:
                    for lib in j[proj][mod][fi]:
                        libS.add(lib)
                        if not proj in projectLibDict:
                            projectLibDict[proj] = set()
                        projectLibDict[proj].add(lib)
        for proj in projectLibDict:
            libCnt += len(projectLibDict[proj])
        print('project size: %d, lib size:%d' % (len(j),libCnt))
        
        li = set()
        result = {}
        for lib in libS:
            data = lib.split('__fdse__')
            g = data[0]
            a = data[1]
            ha = data[2]
            v = data[3]
            libName = '%s__fdse__%s__fdse__%s' %(g,a,ha)
            li.add(libName)
            if libName not in result:
                result[libName] = {}
                result[libName]['use_v0'] = []
                result[libName]['use_v1'] = ""
            if v not in result[libName]['use_v0']:
                result[libName]['use_v0'].append(v)
        for lib in result:
            vers = result[lib]['use_v0']
            newVers =  sorted(vers, key=cmp_to_key(self.mycmpVersionTup))
            result[lib]['use_v0'] = newVers
        # with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/use_libs-4-16.json','w') as f:
        #     json.dump(result,f,indent=4)
        # result = self.addV1()

        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/use_libs-pair-4-16.json','r') as f:
            result = json.load(f)
        projectWithUpdateLib = self.projectLibv0v1(projectLibDict,result)
        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/proj_update_libs-4-16.json','w') as f:
            json.dump(result,f,indent=4)

    def addV1(self):
        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/use_libs-4-16.json','r') as f:
            j = json.load(f)
        for lib in j:
            vers = j[lib]['use_v0']
            latest = vers[-1]
            li = getVersions(lib,latest + '__fdse__----')
            if li == None or len(li) == 0:
                print('err:      %s' % lib)
            else:
                newest = li[-1]
                print('%s %s %s' %(lib,latest,newest))
                j[lib]['use_v1'] = newest
        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/use_libs-pair-4-16.json','w') as f:
            json.dump(j,f,indent=4)
        return j

    def projectLibv0v1(self,projLib,result):
        projWithUpdateLib = {}
        libNum = 0
        for proj in projLib:
            for lib in projLib[proj]:
                data = lib.split('__fdse__')
                g = data[0]
                a = data[1]
                ha = data[2]
                v = data[3]
                libName = '%s__fdse__%s__fdse__%s' %(g,a,ha)
                if result[libName]['use_v1'] != v:
                    libNum+=1
                    if proj not in projWithUpdateLib:
                        projWithUpdateLib[proj] = []
                    projWithUpdateLib[proj].append(lib+'__fdse__'+result[libName]['use_v1'])
        print('proj with update lib: %d, lib num: %d' % (len(projWithUpdateLib),libNum))
        return projWithUpdateLib

        
# a = GenerageVersionPair()
# a.distinctLibs()

class DiffVersionAndUsageAPI(object):

    def diffAPIAndUsage(self):
        path = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/use_libs-pair-4-16.json'
        with open(path,'r') as f:
            libs = json.load(f)
        apiCallPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/api_call_raw_merge-4-16.json'
        with open(apiCallPath,'r') as f:
            apiCall = json.load(f)
        # with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/proj_update_libs-4-16.json','r') as f:
        #     projUpdatePair = json.load(f)
        projValidAPIVPair = {}
        validAPINum = 0
        result = {}
        for projectName in apiCall:
            for mod in apiCall[projectName]:
                for fi in apiCall[projectName][mod]:
                    for lib in apiCall[projectName][mod][fi]:
                        data = lib.split('__fdse__')
                        gahash = '%s__fdse__%s__fdse__%s' %(data[0],data[1],data[2])
                        v1 = libs[gahash]['use_v1']
                        v0 =  data[3]
                        d = apiCall[projectName][mod][fi][lib]
                        versionPair = v0 + '__fdse__' + v1
                        methods = {}
                        methodKeys = []
                        for key in d:
                            mData = key.split('__fdse__')
                            methodShort = trimAPI(mData[1])
                            methods[methodShort] = '%s__fdse__%s' %(mData[0],methodShort)
                            methodKeys.append(methodShort)
                        if v0 == v1:
                            continue
                        if len(methodKeys) == 0:
                            continue
                        if not projectName in projValidAPIVPair:
                            projValidAPIVPair[projectName] = set()
                        projValidAPIVPair[projectName].add('%s__fdse__%s__fdse__%s__fdse__%s__fdse__%s'%(data[0],data[1],data[2],data[3],v0))
                        validAPINum += len(methodKeys)
                        diffJson = self.postToJarDiffServer(data[0],data[1],v0,v1,methodKeys)
                        if len(diffJson) == 0 or len(diffJson['deleted'])==0:
                            continue
                        print(gahash)
                        deletedMethods = diffJson['deleted']
                        if not projectName in result:
                            result[projectName] = {}
                        if not lib in result[projectName]:
                            result[projectName][gahash] = {}
                        res = []
                        for m in deletedMethods:
                            res.append(methods[m])
                        result[projectName][gahash][versionPair] = res
        cntLib = 0
        for proj in projValidAPIVPair:
            cntLib += len(projValidAPIVPair[proj])
        print('proj valid API proj num: %d, lib num: %d, api num: %d' %(len(projValidAPIVPair),cntLib,validAPINum))
        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/api_call_deleted_raw-4-20.json','w') as f:
            json.dump(result,f,indent=4)
        # with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/api_call_deleted_raw-4-16.json','r') as f:
            # result = json.load(f)
        cntLib2 = 0
        diffAPINum = 0
        vPairNum = 0
        for proj in result:
            cntLib2 += len(result[proj])
            for lib in result[proj]:
                vPairNum += len(result[proj][lib])
                for vPair in result[proj][lib]:
                    diffAPINum += len(result[proj][lib][vPair])
        print('proj diff API %d, lib num: %d, vPair num: %d, api num:%d' %(len(result),cntLib2,vPairNum,diffAPINum))

    def postToJarDiffServer(self,groupId,artifactId,v1,v2,usage_array):
        postStr = {}
        postStr['groupId'] = groupId
        postStr['artifactId'] = artifactId
        postStr['version1'] = v1
        postStr['version2'] = v2
        postStr['usage_array'] = usage_array
        # req = requests.post('http://10.176.34.86:18123/jardiff',json=postStr)
        req = requests.post('http://10.176.34.86:18123/jardiff',json=postStr)

        content = req.content
        j = json.loads(content)
        return j

# a = DiffVersionAndUsageAPI()
# a.diffAPIAndUsage()

class GenExcel(object):

    def saveDistinctDeletedMethods(self,rootPath,deleted,finalResultDate):
        fexcel = open(rootPath + '/deleted-method-ex3-%s.csv' % finalResultDate,'w')
        cntl = 0
        for proj in deleted:
            for ga in deleted[proj]:
                for version in deleted[proj][ga]:
                    isFirst = True
                    deletedMethodsMap = deleted[proj][ga][version]

                    for method in deletedMethodsMap:
                        # print(method)
                        prefix = str(cntl+1) + ','
                        if isFirst:
                            prefix += proj+ ','+ ga +"," + version + ","
                            isFirst = False
                        else:
                            prefix +=  ",,"  +  ","
                        fexcel.write(prefix +"\""+ method  +"\"\n" )
                        cntl +=1
        fexcel.close()
        print(cntl)

    def genExcel(self):
        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3/api_call_deleted_raw-4-20.json','r') as f:
            j = json.load(f)
        self.saveDistinctDeletedMethods('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-14-ex3',j,'4-20')

# a = GenExcel()
# a.genExcel()


# 168
# 1. 选定之后的依赖数据 project size: 168, lib size:975
# 2. 需要更新依赖 proj with update lib: 121, lib num: 690
# 3. 有调用到依赖中的API proj valid API 121, lib num: 688, api num: 49969
# 4. 调用到的API有删除 proj diff API projum 34, lib num: 63 v_pair num: 63, api num: 111 
# 5. tool
# 6. SUCCESS的API和项目数量
# proj valid API proj num: 121, lib num: 688, api num: 49969
# proj diff API 34, lib num: 60, vPair num: 60, api num:106

#deprecated
def run2():
    path = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-12/select_ga_vpair.json'
    with open(path,'r') as f:
        j = json.load(f)
    result = {}
    for p in j:
        if p not in result:
            result[p] = {}
        for vPair in j[p]:
            data = p.split('__fdse__')
            print(p)
            print(vPair[0])
            print(vPair[1])
            diffJson = postToJarDiffServer(data[0],data[1],vPair[0],vPair[1])
            if len(diffJson) == 0:
                continue
            sPair = vPair[0] + "__fdse__" + vPair[1]
            if sPair not in result[p]:
                result[p][sPair] = {}
            deletedClass = diffJson['deleted_classes']
            result[p][sPair]['deleted_class'] = deletedClass
            deletedEntryInClass = diffJson['undeleted_class_deleted_items']
            result[p][sPair]['deleted_method'] = deletedEntryInClass
    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-12/raw_deleted_method-4-14.json','w') as f:
        json.dump(result,f,indent=4)

# run2()



