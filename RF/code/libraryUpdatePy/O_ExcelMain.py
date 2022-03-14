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
import datetime
from empiricalData.MyEncoder import MyEncoder
from empiricalData.MyDecoder import MyDecoder



def columns():
    di = {}
    di['id'] = 0
    offset = 0
    di['Proj'] = 1
    di['GA'] = 1 + offset
    di['version_pair'] = 2 + offset
    di['deleted_method'] = 3 + offset
    di['mapping_method'] = 4 + offset
    di['is_mapping'] = 5 + offset
    di['mapping_source'] = 6 + offset
    di['mapping_relation'] = 7 + offset
    di['n_to_n'] = 8 + offset
    di['deprecation_reason'] = 9 + offset
    di['link'] = 10 + offset
    di['refactoring'] = 11 + offset
    di['frequency'] = 12 + offset
    return di

def traverseExcelGetDataStruct(sheet1,cols,tool):
    cursor = 0
    m = {}
    for r in sheet1.get_rows():
        if cursor == 0:
            cursor += 1
            continue
        isMapped = sheet1.cell(cursor,cols['is_mapping']).value
        if isMapped != 'N' and isMapped != 'Y':
            cursor +=1
            continue
        mappingSource = sheet1.cell(cursor,cols['mapping_source']).value
        mappedRelation = sheet1.cell(cursor,cols['mapping_relation']).value
        transSource,transRelation =  tool.transExcelKeyToPaperKey(isMapped,mappingSource,mappedRelation)
        cursor += 1
        if not transSource in m:
            m[transSource] = {}
        if not transRelation in m[transSource]:
            m[transSource][transRelation] = 0
        m[transSource][transRelation] +=1
    
    # for s in m:
    #     print(s)
    #     print('--------')
    #     for k in tool.orderS:
    #         if k in m[s]:
    #             print('%s, %d'%(k,m[s][k]))
    #     print('--------')
    return m

# python3 ciatool/libraryUpdatePy/O_ExcelMain.py 18124 javadoc com.google.guava__fdse__guava__fdse__a1e0af__fdse__13.0.1__fdse__18.0
# python3 ciatool/libraryUpdatePy/O_ExcelMain.py 18123 jar none

def run():
    portId = sys.argv[1]
    runType = sys.argv[2]
    gaVersionPair = sys.argv[3]
    # 1.正常
    # f1 = start(portId,runType,gaVersionPairs,None)
    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/compare-gt/thresholds.json','r') as f:
        j = json.load(f)
    # 2. sensitiveness
    # TH_FIND_SIMILAR_SUPER_CLASS = [0,0.5,1,1.5,2,2.5,3,3.5,4]
    TH_FIND_SIMILAR_SUPER_CLASS = [0.5,1]
    result = {}
    senseName = 'TH_FIND_SIMILAR_SUPER_CLASS'
    for v in TH_FIND_SIMILAR_SUPER_CLASS:
        senPack = (senseName,v)
        precision,recall,f1 = start(portId,runType,gaVersionPair,senPack)
        result[v] = {}
        result[v]['precision'] = precision
        result[v]['recall'] = recall
        result[v]['f1'] = f1
        print('pre:%.2f, rec: %.2f, f1:%.2f' %(precision,recall,f1))
        break
    j['temp'] = result
    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/compare-gt/thresholds.json','w') as f:
        json.dump(j,f,indent=4)

def queryFinder(sheet1,cols,tool):
    GA = None
    VPAIR = None
    cursor = 0
    for r in sheet1.get_rows():
        res = False
        if cursor == 0:
            cursor += 1
            continue
        # print(cursor)
        # print(cols['deleted_method'])
        if sheet1.cell(cursor,cols['deleted_method']).value == "":
            break
        if sheet1.cell(cursor,cols['GA']).value != "" and sheet1.cell(cursor,cols['version_pair']).value != "":
            if GA != None and VPAIR != None:
                res = tool.doWithGAMethods(GA,VPAIR)
            GA = sheet1.cell(cursor,cols['GA']).value
            VPAIR = sheet1.cell(cursor,cols['version_pair']).value
        if res == True:
            break
        method = sheet1.cell(cursor,cols['deleted_method']).value
        mappingSource = sheet1.cell(cursor,cols['mapping_source']).value
        mappedMethods = sheet1.cell(cursor,cols['mapping_method']).value
        mappedRelation = sheet1.cell(cursor,cols['mapping_relation']).value
        ntoN = sheet1.cell(cursor,cols['n_to_n']).value
        isMapped = sheet1.cell(cursor,cols['is_mapping']).value
        rowEntry = RowData(cursor+1,GA,VPAIR,isMapped,method,mappedMethods,mappingSource,mappedRelation)
        rowEntry.nton = ntoN
        tool.traverseRow(rowEntry)
        cursor += 1

    if tool.gaVersionPair == 'none':
        res = tool.doWithGAMethods(GA,VPAIR)


def start(portId,runType,gaVersionPair,sensePack):

    startTime = datetime.datetime.now()
    tool = ToolMappingLogic(portId,runType,gaVersionPair)
    xlsPath = Common.GT_1
    rw = xlrd.open_workbook(xlsPath)
    sheet1 = rw.sheet_by_index(0)
    sheet4 = rw.sheet_by_index(4)
    cols = columns()
    tool.initBeforeExcel(sensePack)
    tableIIDict =  traverseExcelGetDataStruct(sheet1,cols,tool)


    tool.initSheet4Keys(tableIIDict)

    # queryFinder(sheet1,cols,tool)
    # with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/compare-gt/toolmappinglogic.json','w') as f:
    #     m = MyEncoder(indent=4)
    #     s = m.encode(tool)
    #     f.write(s)


    endTime = datetime.datetime.now()
    duration = (endTime - startTime).seconds

    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/compare-gt/toolmappinglogic.json','r') as f:
        # content = f.read()
        toolData = json.load(f)
        # m = MyDecoder()
        # toolData = m.decodeToolMappingLogic(content)

    # precision,recall,f1 = tool.doAfterExcelFinish1(rw,xlsPath,runType,duration)
    precision,recall,f1 = tool.doAfterExcelFinish2(rw,xlsPath,toolData,runType,duration)

    return precision,recall,f1

run()
