from libraryUpdatePy.empiricalData import Common
import os
import json
import requests

def queryUsage(filePath,methodKey):
    postStr = {}
    postStr['filePath'] = filePath
    postStr['methodKey'] = methodKey
    req = requests.post('http://10.176.34.86:18123/projectsource',json=postStr)
    content = req.content
    j = json.loads(content)
    return j

def matchedMethods(gaHash,vpair,v,methods,idd):
    resultPathPrefix = Common.DELETED_VALIDATION_PATH + gaHash + '/usage_raw/'
    resultPath = resultPathPrefix + v + '.json'
    with open(resultPath,'r') as f:
        j = json.load(f)
    result = []
    for entry in j:
        methodList = entry['method_list']
        fileName = entry['fileName']
        projectName = entry['project']
        data2 = projectName.split('_202')
        projectName = data2[0]
        if "__fdse__" in projectName:
            projectPath = Common.ROOT_PROJECT1 + projectName + '/'
        else:
            projectPath = Common.ROOT_PROJECT2 + projectName + '/'
        fileFullPath = projectPath + fileName
        for invokeMethodKey in methodList:
            apiList = methodList[invokeMethodKey]
            isHave = False
            for lineList in apiList:
                loc = lineList[0]
                apiList2 = lineList[1]
                for api in apiList2:
                    data = api.split('__fdse__')
                    shortApi = data[-1]
                    if shortApi in methods:
                        isHave = True
                        break
                if isHave:
                    break
            if isHave:
                print(fileFullPath)
                # print(invokeMethodKey)
                usageStr = queryUsage(fileFullPath,invokeMethodKey)
                result.append((fileFullPath,invokeMethodKey,usageStr))
    resultPathPrefix = Common.DELETED_VALIDATION_PATH + gaHash + '/usage_context/' + vpair +'/' + str(idd) +'/'
    if not os.path.exists(resultPathPrefix):
        os.makedirs(resultPathPrefix)
    resultPath = resultPathPrefix + v + '.java'
    with open(resultPath,'w') as f:
        cnt = 1
        for s in result:
            fileFullPath = s[0]
            invokeMethodKey = s[1]
            usageJson = s[2]
            f.write(str(cnt))
            f.write('\n')
            f.write(fileFullPath)
            f.write('\n')
            f.write(invokeMethodKey)
            f.write('\n')
            f.write('\n')
            for item in usageJson:
                f.write(item)
                f.write('\n\n')
            f.write('\n\n\n\n\n\n')
            cnt += 1
