import os
import json
import requests
from EmpiricalTop200 import postToJarDiffServer
from JavaDocUtil import getVersions


def run():
    path = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-3-data/topNiGAVersionPair-21-3-23-top200-empirical.json'
    with open(path,'r') as f:
        j = json.load(f)
        for p in j:
            print(p)
# run()


def run2():
    path = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-12/select_ga_vpair.json'
    with open(path,'r') as f:
        j = json.load(f)
    result = {}
    for p in j:
        if p not in result:
            result[p] = {}
        for vPair in j[p]:
            data = p.split('__fdse__')
            print(p)
            print(vPair[0])
            print(vPair[1])
            diffJson = postToJarDiffServer(data[0],data[1],vPair[0],vPair[1])
            if len(diffJson) == 0:
                continue
            sPair = vPair[0] + "__fdse__" + vPair[1]
            if sPair not in result[p]:
                result[p][sPair] = {}
            deletedClass = diffJson['deleted_classes']
            result[p][sPair]['deleted_class'] = deletedClass
            deletedEntryInClass = diffJson['undeleted_class_deleted_items']
            result[p][sPair]['deleted_method'] = deletedEntryInClass
    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-12/raw_deleted_method-4-14.json','w') as f:
        json.dump(result,f,indent=4)

# run2()

def saveDistinctDeletedMethods(rootPath,deleted,finalResultDate):
    fexcel = open(rootPath + '/deleted-method-%s.csv' % finalResultDate,'w')
    cntl = 0
    for ga in deleted:
        for version in deleted[ga]:
            isFirst = True
            deletedMethodsMap = deleted[ga][version]

            for method in deletedMethodsMap:
                # print(method)
                prefix = str(cntl+1) + ','
                if isFirst:
                    prefix += ga +"," + version + ","
                    isFirst = False
                else:
                    prefix +=  ","  +  ","
                fexcel.write(prefix +"\""+ method  +"\"\n" )
                cntl +=1
    fexcel.close()
    print(cntl)

def genExcel():
    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-12/raw_deleted_method-4-14.json','r') as f:
        j = json.load(f)
    cnt = 0
    cnt2 = 0
    result = {}
    cnt3 = 0
    for p in j:
        for vPair in j[p]:
            cnt2 +=1
            if p not in result:
                result[p] = {}
            if vPair not in result[p]:
                result[p][vPair] = []
            deletedClass = j[p][vPair]['deleted_class']
            for cl in deletedClass:
                l = len(cl['deleted_method_in_class'])
                if l !=0:
                    cnt3 +=1
                    result[p][vPair].append(cl['deleted_method_in_class'][0])
                    # if l>1:
                    #     cnt3+=1
                    #     result[p][vPair].append(cl['deleted_method_in_class'][1])
                cnt += l
            deletedMethod = j[p][vPair]['deleted_method']
            for method in deletedMethod:
                l = len(method['deleted_method_in_class'])
                if l !=0:
                    # for m in method['deleted_method_in_class']:
                    result[p][vPair].append(method['deleted_method_in_class'][0])
                    cnt3 +=1
                    # if l>1:
                    #     cnt3+=1
                    #     result[p][vPair].append(method['deleted_method_in_class'][1])
                    # if l>2:
                    #     cnt3+=1
                    #     result[p][vPair].append(method['deleted_method_in_class'][2])
                        
                cnt += l

            # cnt += len(deletedMethod)
    print("all method: " + str(cnt))
    print("chosen method: " + str(cnt3))
    # 825
    print("ga vPair: " + str(cnt2))
    # saveDistinctDeletedMethods('/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-4-12',result,'4-13')

# genExcel()


# "com.ning__fdse__async-http-client__fdse__5e1536":[ 
#         [
#         "1.8.12",
#         "1.9.31"
#     ],

