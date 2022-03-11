import os
import json
from functools import cmp_to_key
from typing import Dict,List,Tuple
from empiricalData.DataBean.APIUsageDB import APIUsageDB
import re

def genBatch():
    path = "/home/hadoop/dfs/data/Workspace/LibraryUpdate/output/data/api_call/project_call"

    files = os.listdir(path)
    for file in files:
        s = "java -jar LibEffort-jar-with-dependencies.jar /home/hadoop/dfs/data/Workspace/LibraryUpdate/output /home/hadoop/dfs/data/Workspace/LibraryUpdate/path_config.properties /home/hadoop/dfs/data/Workspace/projects_9_19/projects_git/"+ file[0:-16]
        print(s)

# genBatch()



def mycmp(x,y):
    liA = x.split(',')[0]
    liB = y.split(',')[0]
    if int(liA) > int(liB):
        return 1
    else:
        return -1

# input: api->lineNumber->methodLocation
# output: methodLocation->lineNumber-> list<api>
def reArrange(inputDict):
    output:Dict[str,Dict[str,List[str]]]= {}
    for api in inputDict:
        data = inputDict[api]
        for lineNumber in data:
            methodLocation = data[lineNumber]
            if not methodLocation in output:
                output[methodLocation] = {}
            if not lineNumber in output[methodLocation]:
                output[methodLocation][lineNumber] = []
            if not api in output[methodLocation][lineNumber]:
                output[methodLocation][lineNumber].append(api)
    output2:Dict[str,List[Tuple[str,List[str]]]] = {}
    for methodLocation in output:
        lineNumbersList = output[methodLocation].keys()
        listKeys = sorted(lineNumbersList,key=cmp_to_key(mycmp))
        output2[methodLocation] = []
        for lineNumber in listKeys:
            output2[methodLocation].append((lineNumber,output[methodLocation][lineNumber]))
    result2 = trimData(output2)
    return result2

def trimData(inputData:Dict[str,List[Tuple[str,List[str]]]]):
    result:Dict[str,List[Tuple[str,List[str]]]] = {}
    for methodLocation in inputData:
        result[methodLocation] = []
        for tup in inputData[methodLocation]:
            lineNumber = tup[0]
            apiList = tup[1]
            newAPIList = []
            for api in apiList:
                # trim
                newAPI = trimAPI(api)
                newAPIList.append(newAPI)
            result[methodLocation].append((lineNumber,newAPIList))
    return result

# 把方法的长参数去掉，使用短参数
def trimAPI(api):
    if not "(" in api:
        return api

    index = api.find('(')
    prefix = api[0:index+1]
    suffix = api[index+1:-1]
    if suffix != "":
        data = suffix.split(',')
        for p in data:
            index2 = p.rfind('.')
            subp = p[index2+1:]
            prefix += subp + ","
        prefix = prefix[0:-1] + ")"
    else:
        prefix += ")"
    
    prefix = re.sub('<.*>', '', prefix)

    return prefix
    # print(suffix)




def mergeAPIToResult(path:str,writeFile):
    files = os.listdir(path)
    for file in files:
        if not 'parent_method' in file:
            continue
        if not file in writeFile:
            writeFile[file] = {}
        with open(path +'/' + file,'r') as f:
            j = json.load(f)
            for module in j:
                for fileName in j[module]:
                    if j[module][fileName] == None:
                        continue
                    for jarName in j[module][fileName]:
                        if not fileName in writeFile[file]:
                            writeFile[file][fileName] = {}
                        outputDict = reArrange(j[module][fileName][jarName])
                        if not jarName in writeFile[file][fileName]:
                            writeFile[file][fileName][jarName] = outputDict

# output: project ->file -> jarName -> method -> api usage sequence
def genSequence(usageDBName:str, regen):
    if not regen and os.path.exists(usageDBName):
        with open(usageDBName,'r') as f:
            j = json.load(f)
        res = APIUsageDB(j)
        return res

    writeFile:Dict[str,Dict[str,Dict[str,Dict[str,List[Tuple[str,List[str]]]]]]] = {}
    # path = "/home/hadoop/dfs/data/Workspace/LibraryUpdate/output/data/api_call/api_call"
    path = "/home/hadoop/dfs/data/Workspace/LibraryUpdate/output-api-call-merge/output1"
    mergeAPIToResult(path,writeFile)

    # path = "/home/hadoop/dfs/data/Workspace/LibraryUpdate/output12-23/data/api_call/api_call_result"
    path = "/home/hadoop/dfs/data/Workspace/LibraryUpdate/output-api-call-merge/output2"
    mergeAPIToResult(path,writeFile)

    with open(usageDBName,'w') as f:
        json.dump(writeFile,f,indent=4)
    
    res = APIUsageDB(writeFile)
    return res 
    # return writeFile

