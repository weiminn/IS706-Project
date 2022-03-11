import os
import json
from typing import List, Tuple, Dict
from empiricalData.DataBean.DependencyDB import DependencyDB

def mergeDepToResult(path:str,result):
    files = os.listdir(path)
    for file in files:
        keyFile = file[0:-16]
        result[keyFile] = []
        with open(path+'/'+file,'r') as f:
            j = json.load(f)
            for key in j:
                data = j[key]
                for item in data:
                    dd = item.split('__fdse__')
                    s = dd[0]+"__fdse__"+dd[1]+"__fdse__"+dd[2]+"__fdse__"+dd[3]
                    if not s in result[keyFile]:
                        result[keyFile].append(s)

## project-> list<jar>
def getDepByProjJson(depDbName:str, regen):
    if not regen and os.path.exists(depDbName):
        with open(depDbName,'r') as f:
            j:Dict[str,List[str]] = json.load(f)
            res = DependencyDB(j)
            return res
            
    result:Dict[str,List[str]] = {}
    path:str = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/output/data/dependency/parse2jar'
    mergeDepToResult(path,result)
    path:str = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/output12-23/data/dependency/parse2jar'
    mergeDepToResult(path,result)
    # todo append
    with open(depDbName,'w') as f:
        json.dump(result,f,indent=4)

    res = DependencyDB(result)
    return res

def dumpTop100GA(result):
    sta = {}
    for proj in result:
        data = result[proj]
        for jar in data:
            data2 = jar.split("__fdse__")
            if data2[0] +"__fdse__" + data2[1] not in sta:
                sta[data2[0] +"__fdse__" + data2[1]] = 0
            sta[data2[0] +"__fdse__" + data2[1]] += 1
    d = sorted(sta.items(), key=lambda item:item[1], reverse=True)
    i = 0
    d2 = []
    for en in d:
        i+=1
        print(en)
        jar = en[0]
        d2.append(en)
        if i ==100:
            break
    with open('dep_by_proj_desc_top100.json','w') as f:
        json.dump(d2,f,indent=4)


# 挑选合适的GA找example
def findGAVersionPair(query):
    result = getDepByProjJson()
    # dumpTop100GA(result)

    # query
    # query = "com.squareup.okhttp3__fdse__okhttp"
    versionMap = {}
    for proj in result:
        data = result[proj]
        for jar in data:
            if query in jar:
                data2 = jar.split("__fdse__")
                version = data2[-1]
                # print(proj + ": " + version)
                if version not in versionMap:
                    versionMap[version] = 0
                versionMap[version] +=1
    versionMapList = sorted(versionMap.items(), key=lambda item:item[1], reverse=True)
    # for item in versionMapList:
    #     print(item)
    return versionMapList
    # print(len(result)G)

# findGAVersionPair("com.squareup.okhttp3__fdse__okhttp")



def mergeDeps2():
    path = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/output/data/dependency/parse2jar'
    files = os.listdir(path)
    result = {}
    for file in files:
        data1 = file.split('_2020')
        projName = data1[0]
        with open(path+'/'+file,'r') as f:
            j = json.load(f)
        result[projName] = j
    with open('dep.json','w') as f:
        json.dump(result,f,indent=4)
    print(len(result))
# mergeDeps2()

def checkExists():
    path = '/home/hadoop/dfs/data/Workspace/CongyingXU/Passport/Processed_Downloads_Jars/CrawledGAVs_0218/'

    with open('gavs.json','r') as f:
        j = json.load(f)
    exi = 0
    crawl = []
    for item in j:
        index = item.rfind('__fdse__')
        dirPath = item[0:index]
        version = item[index+8:]
        data = item.split('__fdse__')
        aId = data[1]
        # version = data[3]
        if os.path.exists(path+dirPath+"/"+version+"/"+aId+"-"+version+".jar"):
            exi +=1
        else:
            crawl.append(item)
        # print(dirPath)
        # print(version)
        # break
    print(exi)
    print(len(j))
    with open('append_crawl.json','w') as f:
        json.dump(crawl,f,indent=4)
# checkExists()


def checkMergeCrawlGAV():
    with open('append_crawl.json','r') as f:
        j = json.load(f)
    path = '/home/hadoop/dfs/data/Workspace/CongyingXU/Passport/Processed_Downloads_Jars/CrawledGAV_0922/'
    crawl = []
    for item in j:
        index = item.rfind('__fdse__')
        dirPath = item[0:index]
        version = item[index+8:]
        data = item.split('__fdse__')
        aId = data[1]
        # version = data[3]
        dst = path+dirPath+"/"+version+"/"+aId+"-"+version+".jar"
        # print(dst)
        if not os.path.exists(path+dirPath+"/"+version+"/"+aId+"-"+version+".jar"):
            crawl.append(item)
        # break
    print(len(crawl))
    print(len(j))

# checkMergeCrawlGAV()