import os
import json
import requests
from bs4 import BeautifulSoup
from functools import cmp_to_key
from datetime import datetime
from bs4 import NavigableString
from bs4 import Tag
import time

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
    i0 = versionList.index(v0)
    if v1 in versionList:
        i1 = versionList.index(v1)
        return versionList[i1:i0+1]
    else:
        return versionList[i0:]



def cmp_date(itema,itemb):
    d0 = itema[1].split(' ')[0]
    d1 = itemb[1].split(' ')[0]
    dd0 = time.strptime(d0, '%Y-%m-%d') 
    dd1 = time.strptime(d1, '%Y-%m-%d') 
    if dd0 < dd1:
        return -1
    return 1


def readFromHtmlRaw(subDir, v0,v1):
    with open(subDir + 'time-raw.html','r') as f:
        content = f.read()
    soup = BeautifulSoup(content,'lxml')
    divContent = soup.find('pre',attrs={'id':'contents'})
    if divContent == None:
        return None
    children = divContent.children
    versionToDate = {}
    
    version = None
    date = None
    for child in children:
        if type(child) == NavigableString:
            date = child
            if version != None and date != None:
                trimDate = date.strip('\n').strip(' ').strip('-').strip(' ')
                if trimDate != '':
                    versionToDate[version] = trimDate
                version = None
                date = None
        if type(child) == Tag:
            if child.text.endswith('../'):
                continue
            if child.text.endswith('/'):
                version = child.text.strip('/')
    mapList = list(versionToDate.items())
    newVersionToDateList =  sorted(mapList, key=cmp_to_key(cmp_date))
    versionList = []
    flag = False
    for item in newVersionToDateList:
        if item[0] == v0:
            flag = True
        if item[0] == v1:
            versionList.append(item[0])
            flag = False 
        if flag:
            versionList.append(item[0])
    if len(versionList) == 0:
        versionList.append(newVersionToDateList[-1][0])
    return versionList



def getVersions(GA,versionPair):
    data = versionPair.split('__fdse__')
    v0 = data[0]
    v1 = data[1]
    # result = []
    # todo
    # shell调用A_3rdDBClient生成time.html
    cmd = 'python3 /home/hadoop/dfs/data/Workspace/LibraryUpdate/A_3rdDBClient.py %s %s' %(GA + '__fdse__' + v0,'time')
    val = os.popen(cmd)
    for l in val.readlines():
        if l == '':
            continue
        # print(l)
        pass
    subDir = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/output/jar/%s/' % GA
    
    if os.path.exists(subDir + 'time.html'):
        with open(subDir + 'time.html','r') as f:
            content = f.read()
            versions = readHtml(content,v0,v1)
        # asc
        versions.reverse()
        # print(versions)
        return versions
    
    if os.path.exists(subDir + 'time-raw.html'):
        versions = readFromHtmlRaw(subDir,v0,v1)
        # print(versions)
        # asc
        return versions
    
    

    return None


# getVersions('redis.clients__fdse__jedis__fdse__8ce424','2.8.1__fdse__3.4.1')
# getVersions('com.ning__fdse__async-http-client__fdse__5e1536','1.8.12__fdse__1.9.31')
    