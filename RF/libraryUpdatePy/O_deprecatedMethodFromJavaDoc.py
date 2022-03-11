import os
import json
import Common
import xlrd
import requests
from bs4 import BeautifulSoup

def readHtml(content,v0,v1):
    soup = BeautifulSoup(content,'lxml')
    divContent = soup.find('div',attrs={'class':'gridcontainer'})
    tbody = divContent.find_all('tbody')
    tmpDict = {}
    versionList = []
    for microv in tbody:
        minorv = microv.children
        for child in minorv:
            children2 = child.children
            cnt = 0
            version = None
            tmpList = []
            for child2 in children2:
                tmpList.append(child2)
            date = tmpList[-1].text
            version = None
            if len(tmpList) == 5:
                version = tmpList[1].text
            elif len(tmpList) == 4:  
                version = tmpList[0].text
            if version == None:
                continue
            tmpDict[version] = date
            versionList.append(version)
    # print(tmpDict)
    i0 = versionList.index(v0)
    i1 = versionList.index(v1)

    return versionList[i1:i0]


def getVersions(GA,versionPair):
    data = versionPair.split('__fdse__')
    v0 = data[0]
    v1 = data[1]
    # result = []
    # todo
    # shell调用A_3rdDBClient生成time.html
    val = os.popen('python3 /home/hadoop/dfs/data/Workspace/LibraryUpdate/A_3rdDBClient.py %s %s' %(GA + '__fdse__' + v0,'time'))
    for l in val.readlines():
        if l == '':
            continue
        print(l)
    subDir = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/output/jar/%s/' % GA
    with open(subDir + 'time.html','r') as f:
        content = f.read()
        versions = readHtml(content,v0,v1)

    versions.reverse()
    return versions


def queryDeprecatedMethod(GA,versionPair,methods):
    versionsFromHtml = getVersions(GA,versionPair)
    resultSet = set()
    for v in versionsFromHtml:
        result =  queryDeprecatedMethodOfOneVersion(GA,versionPair,methods,v)
        for item in result:
            resultSet.add(item)
    return list(resultSet)


def queryDeprecatedMethodOfOneVersion(GA,versionPair,methods,version):
    postStr = {}
    data = GA.split('__fdse__')
    postStr['groupId'] = data[0]
    postStr['artifactId'] = data[1]
    postStr['version'] = version
    newMethods = []
    for method in methods:
        tmp = method.split('__fdse__')
        newMethods.append(tmp[-1])
    postStr['usage_array'] = newMethods
    req = requests.post('http://10.176.34.86:18123/apideprecation',json=postStr)
    content = req.content
    j = json.loads(content)
    result = []
    for key in j:
        if j[key] == 'deprecated':
            result.append(GA + '__fdse2__' + versionPair + '__fdse2__'+ key)

    return result


def columns():
    di = {}
    di['GA'] = 0
    di['version_pair'] = 1
    di['deleted_method'] = 2
    di['frequency'] = 3
    di['mapping_method'] = 4
    di['is_mapping'] = 5
    di['mapping_source'] = 6
    di['mapping_relation'] = 7
    di['deprecation_reason'] = 8
    di['link'] = 9
    di['n_to_n'] = 10 
    di['refactoring'] = 1
    return di


def run():
    xlsPath = Common.GT
    rw = xlrd.open_workbook(xlsPath)
    sheet1 = rw.sheet_by_index(0)
    cols = columns()
    GA = None
    VPAIR = None
    cursor = 0
    tmpMethods = []
    fullResult = []
    for r in sheet1.get_rows():
        if cursor == 0:
            cursor += 1
            continue
        if sheet1.cell(cursor,cols['deleted_method']).value == "":
            break
        if sheet1.cell(cursor,cols['GA']).value != "" and sheet1.cell(cursor,cols['version_pair']).value != "":
            if GA != None and VPAIR != None:
                if not (GA == 'com.google.guava__fdse__guava__fdse__a1e0af' and VPAIR == '13.0.1__fdse__18.0'):
                    continue
                result = queryDeprecatedMethod(GA,VPAIR,tmpMethods)
                print(GA)
                print(VPAIR)
                print('%d/%d'%(len(result),len(tmpMethods)))
                for item in result:
                    fullResult.append(item)
                tmpMethods = []
            GA = sheet1.cell(cursor,cols['GA']).value
            VPAIR = sheet1.cell(cursor,cols['version_pair']).value

        method =  sheet1.cell(cursor,cols['deleted_method']).value
        tmpMethods.append(method)
        cursor += 1

    print(len(fullResult))


run()





