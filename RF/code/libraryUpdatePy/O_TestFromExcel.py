# -*- coding: utf-8 -*- 
import os
import json
import Common
import xlrd
import requests
from TestOneRowLogic import TestOneRowLogic
import sys

def columns():
    di = {}
    di['id'] = 0
    offSet = 0
    di['GA'] = 1 + offSet
    di['version_pair'] = 2+ offSet
    di['deleted_method'] = 3+ offSet
    di['mapping_method'] = 4+ offSet
    di['is_mapping'] = 5+ offSet
    di['mapping_source'] = 6+ offSet
    di['mapping_relation'] = 7+ offSet
    di['n_to_n'] = 8+ offSet
    di['deprecation_reason'] = 9+ offSet
    di['link'] = 10+ offSet
    di['refactoring'] = 11+ offSet
    di['frequency'] = 12+ offSet
    return di


def run():
    # 18123@LibraryUpdate 18124 @LibraryUpdate-plh
    portId = sys.argv[1]
    runType = sys.argv[2]
    rowId = sys.argv[3]
    rowId = int(rowId)-1
    tool = TestOneRowLogic()
    xlsPath = Common.GT_1
    rw = xlrd.open_workbook(xlsPath)
    sheet1 = rw.sheet_by_index(0)
    cols = columns()
    GA = None
    VPAIR = None
    cursor = 0
    tool.initBeforeExcel(portId)
    
    for r in sheet1.get_rows():
        if cursor == 0:
            cursor += 1
            continue
        if sheet1.cell(cursor,cols['deleted_method']).value == "":
            break
        if sheet1.cell(cursor,cols['GA']).value != "" and sheet1.cell(cursor,cols['version_pair']).value != "":
            GA = sheet1.cell(cursor,cols['GA']).value
            VPAIR = sheet1.cell(cursor,cols['version_pair']).value
        method = sheet1.cell(cursor,cols['deleted_method']).value
        mappingSource = sheet1.cell(cursor,cols['mapping_source']).value
        mappedMethods = sheet1.cell(cursor,cols['mapping_method']).value
        if cursor == rowId:
            print('%s %s %s %s' % (GA,VPAIR,method,mappingSource))
            tool.queryMappedMethodMain(GA,VPAIR,method,mappingSource,mappedMethods,runType)
            break
        cursor += 1


run()





