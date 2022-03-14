import os
import json

def run():

    top100Path = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/dep_by_proj_desc_top100.json'
    with open(top100Path,'r') as f:
        j = json.load(f)
    gaList = []
    for item in j:
        gaList.append(item[0])
    historyPath = '/home/hadoop/dfs/data/Workspace/ws/finalResult.json'
    with open(historyPath,'r') as f:
        j2 = json.load(f)

    gaList.clear()
    gaList.append('com.google.guava__fdse__guava')
    gaList.append('org.eclipse.jetty__fdse__jetty-server')
    gaList.append('io.netty__fdse__netty-all')
    gaList.append('com.alibaba__fdse__fastjson')
    gaList.append('org.apache.lucene__fdse__lucene-core')
    gaList.append('org.jsoup__fdse__jsoup')
    gaList.append('org.elasticsearch__fdse__elasticsearch')
    result = []
    cnt = 0
    for projectEntry in j2:
        for projectKey in projectEntry:
            data = projectEntry[projectKey]
            newEntry = []
            for entry in data:
                ga = entry['groupId']  + "__fdse__" + entry['artifactId']
                if ga in gaList:
                    newEntry.append(entry)
                    cnt +=1
            #
            if len(newEntry) !=0:
                newResult = {}
                newResult['project'] = projectKey
                newResult['data'] = newEntry
                result.append(newResult)
    with open('/home/hadoop/dfs/data/Workspace/ws/finalResult-100ga.json','w') as f:
        json.dump(result,f,indent=4)
    print(cnt)


print(Common.GT)


# run()