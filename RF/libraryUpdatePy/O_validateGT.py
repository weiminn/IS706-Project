import os
import json
import Common
import xlrd


def queryMappingMethod(GA,versionPair,method):
    postStr = {}
    postStr['GA'] = GA
    postStr['version_pair'] = versionPair
    postStr['method'] = method
    req = requests.post('http://10.176.34.86:18123/deleted_method_mapping',json=postStr)
    content = req.content
    j = json.loads(content)
    return j


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

def compareGT(ans,gt):
    gt = gt.split('\n')
    if ans in gt:
        return True
    return False

def run():
    xlsPath = Common.GT
    rw = xlrd.open_workbook(xlsPath)
    sheet1 = rw.sheet_by_index(0)
    cols = columns()
    GA = None
    VPAIR = None
    cursor = 0

    for r in sheet1.get_rows():
        if cursor == 0:
            cursor += 1
            continue
        if sheet1.cell(cursor,cols['deleted_method']).value == "":
            break
        if sheet1.cell(cursor,cols['GA']).value != "" and sheet1.cell(cursor,cols['version_pair']).value != "":
            GA = sheet1.cell(cursor,cols['GA']).value
            VPAIR = sheet1.cell(cursor,cols['version_pair']).value
        method =  sheet1.cell(cursor,cols['deleted_method']).value
        result = queryMappingMethod(GA,VPAIR,method)
        mappedMethod = sheet1.cell(cursor,cols['mapping_method']).value
        flag = compareGT(result,mappedMethod)
        print(GA + " " + VPAIR + " "+ method)

        cursor += 1
# 跑tool 跑出precision
run()





