import json
import os
from empiricalData.Modifier import isAbstract, isInterface, isPublic, isNative

def parse_soot_api(declaration,classNewName):
    # <com.xuggle.xuggler.IError: void \u003cinit\u003e(long,boolean)>
    declaration = declaration[1:-1]
    index = declaration.find(": ")
    methodName = declaration[index + 2:]
    # className = declaration[0:index].replace("$", ".") 
    className = classNewName
    index2 = methodName.find(' ')
    ret = methodName[0:index2]
    new_method = methodName[index2+1:]

    start = new_method.find("(")
    method_name = new_method[:start]
    if method_name == "<init>" :
        dot_index = className.rfind(".")
        if dot_index < 0:
            new_method = className + new_method[start:]
        else:
            new_method = className[dot_index + 1:] + new_method[start:]
    api = className + "." + new_method
    # print(new_method)
    # print(api)
    # print(ret)
    return ret,api


# parse_soot_api("\u003ccom.xuggle.xuggler.IError: void \u003cinit\u003e(long,boolean)\u003e")

# 输入api_call_result, 查询soot lib_to_method 结果，增加return type结果
def retrieveMethodWithReturn(parsedAPIName,libToMethodJson):

    if libToMethodJson == None:
        return
    for classJson in libToMethodJson:
        className = classJson['className']
        classNewName = className.replace("$", ".") 
        if not classNewName in parsedAPIName:
            continue
        methods = classJson['methods']
        for method in methods:
            methodName = method['methodName']

            modifiers = method['modifiers']
            if isNative(modifiers) or not isPublic(modifiers):
                continue
            returnValue, decodedMethodName = parse_soot_api(methodName,classNewName)
            if parsedAPIName == decodedMethodName:
                return returnValue + '__fdse__' + decodedMethodName

        fields = classJson['fields']
        for field in fields:
            modifiers = field['modifiers']
            if isNative(modifiers) or not isPublic(modifiers):
                continue
            fieldFullName = classNewName + "." + field["fieldName"]
            typ = field['type'].replace('$','.')
            if fieldFullName == parsedAPIName:
                return typ+ '__fdse__' + fieldFullName
    return None


def loadJson(path):
    with open(path,'r') as f:
        j = json.load(f)
    return j


def newSave(result,module,fileName,jarName,fullMethod,lineDict):
    if not module in result:
        result[module] = {}
    if not fileName in result[module]:
        result[module][fileName] = {}
    if not jarName in result[module][fileName]:
        result[module][fileName][jarName] = {}
    if not fullMethod in result[module][fileName][jarName]:
        result[module][fileName][jarName][fullMethod] = {}
    result[module][fileName][jarName][fullMethod] = lineDict

def run():
    rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/'
    apiCallPath = rootPath +  '2020-4-14-ex3/LibAPIOutput/data/api_call/api_call_result'
    files = os.listdir(apiCallPath)
    rerun = set()
    for file in files:
        if not 'parent_method' in file:
            continue
        # if not file in todolist:
        #     continue
        newOutput = rootPath +'2020-4-14-ex3/LibAPIOutput/data/api_call/api_call_result_add_ret/'
        newPath = newOutput + file
        # if os.path.exists(newPath):
        #     continue
        with open(apiCallPath +'/'+ file,'r') as f:
            j = json.load(f)
        res = {}
        for module in j:
            for fileName in j[module]:
                if j[module][fileName] == None:
                    continue
                for jarName in j[module][fileName]:
                    data = jarName.split('/')[0].split('__fdse__')
                    gaHash = data[0] + '__fdse__' + data[1] + '__fdse__' + data[2]
                    jarFileName = data[1] + '-' + data[3] + '.jar'
                    queryPath = rootPath +'2020-4-14-ex3/LibAPIOutput/data/extractLib/lib_to_method/%s/%s.json'
                    libToMethodJson = None
                    if len(data) == 6:
                        jarFileName = data[1] + '-' + data[3] +'-' + data[5]+ '.jar'
                        if os.path.exists(queryPath % (gaHash,jarFileName)):
                            libToMethodJson = loadJson(queryPath % (gaHash,jarFileName))
                    else:
                        if os.path.exists(queryPath % (gaHash,jarFileName)):
                            libToMethodJson = loadJson(queryPath % (gaHash,jarFileName))
                    if libToMethodJson == None:
                        rerun.add(file)
                        continue
                    for method in j[module][fileName][jarName]:
                        # if method == 'wiremock.org.apache.commons.lang.StringUtils.repeat(java.lang.String,int)':
                            # print('aa')
                        fullMethod = retrieveMethodWithReturn(method,libToMethodJson)
                        if fullMethod == None:
                            print('aaaa')
                            rerun.add(file)
                            continue
                        lineDict = j[module][fileName][jarName][method]
                        newSave(res,module,fileName,jarName,fullMethod,lineDict)
        
        with open(newPath,'w') as f:
            json.dump(res,f,indent=4)
    for file in rerun:
        print(file)


# run()