import os
import json
from libraryUpdatePy.empiricalData import B_genGavs
from packaging import version
from functools import cmp_to_key


##########
## 生成batch文件批量跑findExample
def mycmp(x,y):
    if version.parse(x) > version.parse(y):
        return 1
    else:
        return -1

def mycmp2(x,y):
    return x-y

def selectTop5(versionMapList):
    if len(versionMapList) >5:
        versionMapList = versionMapList[0:5]
    versionList = []
    for item in versionMapList:
        versionList.append(item[0])
    versionList.sort(key=cmp_to_key(mycmp))
    return versionList

def genBatch():
    a = "dep_by_proj_desc_top100.json"
    with open(a,'r') as f:
        j = json.load(f)
    for item in j:
        ga = item[0]
        # print(ga)
        versionMapList = B_genGavs.findGAVersionPair(ga)
        versionList = selectTop5(versionMapList)
        print("./debug_server2.sh" +" " +ga +" " + versionList[0] + " "+ versionList[-1])
        # for i in range(0,len(versionList)-1):
        #     print("./debug_server2.sh" +" " +ga +" " + versionList[i] + " "+ versionList[i+1])
        # break

# genBatch()




### 输入log文件，统计批量跑的 deleted modify等数据

def tongji():
    result = {}
    currGAV = None

    DIFF_ADD_METHOD_STR = '[main] INFO  DiffInfoPrinter  - JarDiff: Added method number: '
    DIFF_DELETE_METHOD_STR = '[main] INFO  DiffInfoPrinter  - JarDiff: Deleted method number: '
    DIFF_MODIFY_METHOD_STR = '[main] INFO  DiffInfoPrinter  - JarDiff: Modified method number: '
    USAGE_V1 = '[main] INFO  FindUpdateExamples  - CodeBase: v1 API Invoked in lib number: '
    USAGE_V2 = '[main] INFO  FindUpdateExamples  - CodeBase: v2 API Invoked in lib number: '
    INTER_ALL = '[main] INFO  FindUpdateExamples  - Intersection api number: '
    INTER_ADDED = '[main] INFO  FindUpdateExamples  - Intersection added method number: '
    INTER_DELETED = '[main] INFO  FindUpdateExamples  - Intersection deleted method number: '
    INTER_CHANGE_PREV = '[main] INFO  FindUpdateExamples  - Intersection changed_method_prev method number: '
    INTER_CHANGE_CURR = '[main] INFO  FindUpdateExamples  - Intersection changed_method_curr method number: '

    with open('findExample.log','r') as f:
        for line in f:
            if line.startswith('[main] INFO  FindUpdateExamples  - Analyzing: '):
                currGAV = line.replace('[main] INFO  FindUpdateExamples  - Analyzing: ','')
                currGAV = currGAV.rstrip('\n')
                result[currGAV] = {}
                continue
            if line.startswith(DIFF_ADD_METHOD_STR):
                s = line.replace(DIFF_ADD_METHOD_STR,'')
                result[currGAV]['jardiff_added_method'] = int(s)
                continue
            if line.startswith(DIFF_DELETE_METHOD_STR):
                s = line.replace(DIFF_DELETE_METHOD_STR,'')
                result[currGAV]['jardiff_deleted_method'] = int(s)
                continue
            if line.startswith(DIFF_MODIFY_METHOD_STR):
                s = line.replace(DIFF_MODIFY_METHOD_STR,'')
                result[currGAV]['jardiff_modified_method'] = int(s.split(',')[0])
                continue
            if line.startswith(USAGE_V1):
                s = line.replace(USAGE_V1,'')
                result[currGAV]['usage_v1'] = int(s)
                continue
            if line.startswith(USAGE_V2):
                s = line.replace(USAGE_V2,'')
                result[currGAV]['usage_v2'] = int(s)
                continue
            if line.startswith(INTER_ALL):
                s = line.replace(INTER_ALL,'')
                result[currGAV]['inter_all'] = int(s)
                continue
            if line.startswith(INTER_ADDED):
                s = line.replace(INTER_ADDED,'')
                result[currGAV]['inter_add'] = int(s)
                continue
            if line.startswith(INTER_DELETED):
                s = line.replace(INTER_DELETED,'')
                result[currGAV]['inter_delete'] = int(s)
                continue
            if line.startswith(INTER_CHANGE_PREV):
                s = line.replace(INTER_CHANGE_PREV,'')
                result[currGAV]['inter_change_prev'] = int(s)
                continue

            if line.startswith(INTER_CHANGE_CURR):
                s = line.replace(INTER_CHANGE_CURR,'')
                result[currGAV]['inter_change_curr'] = int(s)
                continue

    # s1 = 0
    # s2 = 0
    # s3 = 0
    # s4 = 0
    # for gav in result:
    #     if 'inter_add' in result[gav]:
    #         s1 += result[gav]['inter_add']
    #     if 'inter_delete' in result[gav]:
    #         s2 += result[gav]['inter_delete']
    #     if 'inter_change_prev' in result[gav]:
    #         s3 += result[gav]['inter_change_prev']
    #     if 'inter_change_curr' in result[gav]:
    #         s4 += result[gav]['inter_change_curr']
    # print(s1)
    # print(s2)
    # print(s3)
    # print(s4)
    for gav in result:
        if 'inter_delete' in result[gav]:
            s = result[gav]['inter_delete']
            if s !=0:
                print(gav)
# tongji()
            
            