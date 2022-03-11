import json
import sys
import os
from empiricalData.E_genDB import m2,m,generateGroundTruthRaw


def validateGA():
    path = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-data/dep-db-21-1-20.json'
    with open(path,'r') as f:
        j = json.load(f)
    itemSet = set()
    fim = {}
    fimVersion = {}
    for proj in j:
        for item in j[proj]:
            index = item.rfind('__fdse__')
            itemSet.add(item[0:index])
            if item[0:index] not in fim:
                fim[item[0:index]] = 0
            if item[0:index] not in fimVersion:
                fimVersion[item[0:index]] = set()
            fimVersion[item[0:index]].add(item[index:])
            fim[item[0:index]] +=1
    itemList = list(itemSet)
    print(len(itemList))
    

    fim2 = sorted(fim.items(),key = lambda x:x[1],reverse = True)
    # fim2 = sorted(fim.items(),key = lambda x:x[1])
    # fim3 = sorted(fim2,reverse=True)
    # print(fim2[0:100])
    a = fim2[0:2000] # 104个
    top200 = []
    for item in a:
        top200.append(item[0])
    # print(top200)
    # print(a)
    # print(len(fim2))
    # print(lclen(j))
    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/verification/deleted_result-3-15.json','r') as f:
        j2 = json.load(f)
    for item in j2:
        if item not in top200:
            print(item)
    # for item in top100:
    #     aaa = fimVersion[item]
    #     if len(aaa) == 1:
    #         print(item)
    #         print(aaa)

# 11419 个GA
# validateGA()
# test()
# m()
# m2()
# m2()
def top200Select():
    m()
top200Select()

# resultDate = '21-3-27-filterUsage10'
# generateGroundTruthRaw(resultDate)

def validateGA2():
    path = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-data/topNiGAVersionPair-21-1-28.json'
    with open(path,'r') as f:
        j = json.load(f)
    print(len(j))

# validateGA2()


def finalResult():
    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/verification/deleted_result-3-15.json','r') as f:
        j2 = json.load(f)
    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-data/usage_final_result-21-3-23.json','r') as f:
        finalResult = json.load(f)
    deletedAPI = finalResult['a_has_deleted']
    print(len(deletedAPI))
    cnt = 0
    for gaHash in deletedAPI:
        if gaHash not in j2:
            cnt+=1
    print(cnt)
# finalResult()
