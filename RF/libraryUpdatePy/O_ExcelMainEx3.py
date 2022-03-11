# -*- coding: utf-8 -*- 
import os
import json
import Common
import xlrd
import requests
from ToolMappingLogic import ToolMappingLogic
from ToolMappingLogicAppend import ToolMappingLogicAppend
from ExcelRow import RowData
import sys

def columns():
    di = {}
    di['id'] = 0
    di['proj'] = 1
    di['GA'] = 2
    di['version_pair'] = 3
    di['deleted_method'] = 4
    di['mapping_method'] = 5
    di['is_mapping'] = 6
    di['mapping_source'] = 7
    di['mapping_relation'] = 8
    di['n_to_n'] = 9
    di['deprecation_reason'] = 10
    di['link'] = 11
    di['refactoring'] = 12
    di['frequency'] = 13
    di['find_map'] = 14
    return di

# python3 ciatool/libraryUpdatePy/O_ExcelMain.py 18124 javadoc com.google.guava__fdse__guava__fdse__a1e0af__fdse__13.0.1__fdse__18.0
# python3 ciatool/libraryUpdatePy/O_ExcelMain.py 18123 jar none
def run():
    portId = sys.argv[1]
    runType = sys.argv[2]
    gaVersionPair = sys.argv[3]
    tool = ToolMappingLogicAppend(portId,runType,gaVersionPair)
    # tool = ToolMappingLogic(portId,runType,gaVersionPair)
    xlsPath = Common.GT_3
    rw = xlrd.open_workbook(xlsPath)
    sheet1 = rw.sheet_by_index(0)
    cols = columns()
    GA = None
    VPAIR = None
    cursor = 0
    tool.initBeforeExcel()
    # tool.initSheet3Keys(sheet3)
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
            if len(GA.split("__fdse__")) > 3:
                GAlist = GA.split("__fdse__")
                GA = GAlist[0] + "__fdse__" + GAlist[1] + "__fdse__" + GAlist[2]
            VPAIR = sheet1.cell(cursor,cols['version_pair']).value
        method = sheet1.cell(cursor,cols['deleted_method']).value
        mappingSource = sheet1.cell(cursor,cols['mapping_source']).value
        mappedMethods = sheet1.cell(cursor,cols['mapping_method']).value
        mappedRelation = sheet1.cell(cursor,cols['mapping_relation']).value
        isMapped = sheet1.cell(cursor,cols['is_mapping']).value
        # mappingSource = None
        # mappedMethods = None
        # mappedRelation = None
        # isMapped = None
        rowEntry = RowData(cursor+1,GA,VPAIR,isMapped,method,mappedMethods,mappingSource,mappedRelation)
        tool.traverseRow(rowEntry)
        cursor += 1

        if res == True:
            break
    if tool.gaVersionPair == 'none':
        res = tool.doWithGAMethods(GA,VPAIR)
    tool.doAfterExcelFinish(rw,xlsPath,runType)

run()





