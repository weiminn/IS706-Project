import os
import json
import xlrd
import xlwt
import requests

from libraryUpdatePy.empiricalData import Common
from typing import List, Tuple, Dict, Set


def postToJarDiffServer(groupId,artifactId,v1,v2,):
    postStr = {}
    postStr['groupId'] = groupId
    postStr['artifactId'] = artifactId
    postStr['version1'] = v1
    postStr['version2'] = v2
    postStr['all_diff_api'] = True
    req = requests.post('http://10.176.34.86:18123/jardiff',json=postStr)
    content = req.content
    j = json.loads(content)
    return j


def run():
    with open(Common.MANUALLY_SELECTED_V_PAIR,'r') as f:
        j = json.load(f)
    wt = xlwt.Workbook()
    sheet1 = wt.add_sheet(u'sheet1',cell_overwrite_ok=True)
    row = 0
    result = {}
    for gaHash in j:
        vPairs = j[gaHash]
        data = gaHash.split('__fdse__')
        groupId = data[0]
        artifactId = data[1]
        # sheet1.write(row,0, gaHash)
        for vPair in vPairs:
            # sheet1.write(row,1, vPair)
            v0 = vPair[0]
            v1 = vPair[1]
            print(gaHash)
            print(vPair)
            diffJson = postToJarDiffServer(groupId,artifactId,v0,v1)
            if not gaHash in result:
                result[gaHash] = {}
            result[gaHash][v0+ "__fdse__" + v1] =  diffJson
    with open(Common.ROOT_DATA_PATH +'2021-02-09-diff-all-public.json','w') as f:
        json.dump(result,f,indent=4)
            # deletedFieldInClass:Dict = diffJson['deleted_field_in_class']
            # deletedMethodInClass:Dict = diffJson['deleted_method_in_class']
            # deletedClass:Dict = diffJson['deleted_classes']

            # sheet1.write(row,2,'deleted_classes')
            # for deletedC in deletedClass:
            #     pass
            # sheet1.write(row,2,'deleted_method_in_class')
            # sheet1.write(row,2,'deleted_field_in_class')

    
# run()

def load():
    with open(Common.ROOT_DATA_PATH +'2021-02-09-diff-all-public.json','r') as f:
        j = json.load(f)
    cnt = 0
    for gaHash in j:
        for vPair in j[gaHash]:
            j2 = j[gaHash][vPair]
            deletedClass = j2['deleted_classes']
            deletedEntryInClass = j2['undeleted_class_deleted_items']
            s1 = len(deletedClass)
            cnt += s1
            for item in deletedEntryInClass:
                s2 = len(item['deleted_fields_in_class'])
                s3 = len(item['deleted_method_in_class'])
                cnt += s2
                cnt += s3
    print(cnt)

    
load()

# 35825