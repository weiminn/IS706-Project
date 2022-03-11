import os
import json
import shutil



with open('gavs.json','r') as f:
    gavs = json.load(f)

result = {}
dir0218 = '/home/hadoop/dfs/data/Workspace/CongyingXU/Passport/Processed_Downloads_Jars/CrawledGAVs_0218'
dir0922 = '/home/hadoop/dfs/data/Workspace/CongyingXU/Passport/Processed_Downloads_Jars/CrawledGAV_0922'
output = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/CrawledJar'
jarMd5 = '/home/hadoop/dfs/data/Workspace/tyc/Jars-MD5'

def cpJar(dirName,version,jarName,srcPath):
    if not os.path.exists(output+"/"+dirName+"/"+version):
        os.makedirs(output+"/"+dirName+"/"+version)
    shutil.copy(srcPath,output+"/"+dirName+"/"+version+"/"+jarName)

appendCrawl2 = []
for gav in gavs:
    data = gav.split('__fdse__')
    groupId = data[0]
    artifactId = data[1]
    hashPrefix = data[2]
    version = data[3]
    dirName = groupId +"__fdse__"+ artifactId+ "__fdse__"+ hashPrefix
    jarName = artifactId+"-"+ version+".jar"
    if os.path.exists(dir0218+"/"+dirName+"/"+version+"/"+jarName):
        result[gav] = dir0218+"/"+dirName+"/"+version+"/"+jarName
        cpJar(dirName,version,jarName,dir0218+"/"+dirName+"/"+version+"/"+jarName)
    elif os.path.exists(dir0922+"/"+dirName+"/"+version+"/"+jarName):
        result[gav] = dir0922+"/"+dirName+"/"+version+"/"+jarName
        cpJar(dirName,version,jarName,dir0922+"/"+dirName+"/"+version+"/"+jarName)
    elif os.path.exists(jarMd5+"/"+jarName[0:3].upper()+"/"+jarName):
        result[gav] = jarMd5+"/"+jarName[0:3].upper()+"/"+jarName
        cpJar(dirName,version,jarName,jarMd5+"/"+jarName[0:3].upper()+"/"+jarName)
    # else:
        # appendCrawl2.append(gav)
print(len(gavs))
print(len(result))
# print(len(appendCrawl2))
# with open('append_crawl2.json','w') as f:
    # json.dump(appendCrawl2,f,indent=4)
