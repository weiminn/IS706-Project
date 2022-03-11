# -*- coding: utf-8 -*- 
import os
import json
import Common
import xlrd
import requests
from ToolMappingSetGranu import ToolMappingSetGranu
from ExcelRow import RowData
import sys

def columns():
    di = {}
    di['id'] = 0
    di['GA'] = 1
    di['version_pair'] = 2
    di['deleted_method'] = 3
    di['mapping_method'] = 4
    di['is_mapping'] = 5
    di['mapping_source'] = 6
    di['mapping_relation'] = 7
    di['n_to_n'] = 8
    di['deprecation_reason'] = 9
    di['link'] = 10
    di['refactoring'] = 11
    di['frequency'] = 12
    di['deprecate'] = 13
    di['reason'] = 14
    di['TP'] = 15
    di['FP'] = 16 
    di['TN'] = 17
    di['FN'] = 18
    di['mapped_method'] = 19
    di['mapped_type'] = 20
    di['granularity'] = 21
    return di

# python3 ciatool/libraryUpdatePy/O_ExcelMain.py 18124 com.google.guava__fdse__guava__fdse__a1e0af__fdse__13.0.1__fdse__18.0
# python3 ciatool/libraryUpdatePy/O_ExcelMain.py 18123 none
def run():
    portId = sys.argv[1]
    gaVersionPair = sys.argv[2]
    tool = ToolMappingSetGranu(portId,gaVersionPair)
    xlsPath = Common.GT
    rw = xlrd.open_workbook(xlsPath)
    sheet1 = rw.sheet_by_index(0)
    cols = columns()
    GA = None
    VPAIR = None
    cursor = 0
    tool.initBeforeExcel()
    for r in sheet1.get_rows():
        res = False
        if cursor == 0:
            cursor += 1
            continue
        if sheet1.cell(cursor,cols['deleted_method']).value == "":
            break
        if sheet1.cell(cursor,cols['GA']).value != "" and sheet1.cell(cursor,cols['version_pair']).value != "":
            if GA != None and VPAIR != None:
                res = tool.doWithGAMethods(GA,VPAIR)
            GA = sheet1.cell(cursor,cols['GA']).value
            VPAIR = sheet1.cell(cursor,cols['version_pair']).value
        method = sheet1.cell(cursor,cols['deleted_method']).value
        mappingSource = None
        mappedMethods = None
        mappedRelation = None
        isMapped = None
        rowEntry = RowData(cursor+1,GA,VPAIR,isMapped,method,mappedMethods,mappingSource,mappedRelation)
        tool.traverseRow(rowEntry)
        cursor += 1

        if res == True:
            break
    if tool.gaVersionPair == 'none':
        res = tool.doWithGAMethods(GA,VPAIR)
    tool.doAfterExcelFinish(rw,xlsPath)

run()
