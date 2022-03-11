# -*- coding: utf-8 -*- 
import abc
from ILogic import ILogic
import JavaDocUtil
import requests
import json
from typing import List, Tuple, Dict, Set
from ExcelRow import RowData
from xlutils.copy import copy

class ToolMappingSetGranu(ILogic):

    def __init__(self,portId,gaVersionPair):
        self.portId = portId
        self.gaVersionPair = gaVersionPair

    def initBeforeExcel(self):
        self.GA = None
        self.VPAIR = None

        self.isStart = False

        # round
        self.roundRows:List[RowData] = []
        self.roundMappedMethodDict:Dict[str,List[str]] = {}
        self.mappedRows = []
 

    def doWithGAMethods(self,GA,VPAIR):
        self.GA = GA
        self.VPAIR = VPAIR
        print(GA)
        print(VPAIR)
        if self.gaVersionPair != "none" and self.gaVersionPair == self.GA + '__fdse__' + self.VPAIR:
            self.isStart = True
        if self.gaVersionPair != "none" and not self.isStart:
            self.resetRound()
            return False
        roundMappedRows:List[RowData] = self.queryMappingMethod(GA,VPAIR,self.roundRows)
        self.setExcel(roundMappedRows)
        self.resetRound()
        if self.gaVersionPair != "none":
            return True
        return False
    
    def setExcel(self,rows):
        for r in rows:
            self.mappedRows.append(r)

    def resetRound(self):
        self.roundMappedMethodDict = {}
        self.roundRows = []

    def doAfterExcelFinish(self,readWorkBook,xlsPath):
        workbook = copy(readWorkBook)
        sheet1 = workbook.get_sheet(0)
        for r in self.mappedRows:
            cursor = r.rowId - 1
            sheet1.write(cursor,21,r.granularity)
        workbook.save(xlsPath + '-mmm.xls')
    
            
    # load data for one round
    def traverseRow(self,rowEntry):
        method = rowEntry.method

        mappedMethods = None
        self.appendTempRowData(rowEntry,mappedMethods,method)
    
    # 加入round row，mappedMethodDict保存deleted method和对应的mapping
    def appendTempRowData(self,rowEntry,mappedMethods,method):
        self.roundRows.append(rowEntry)


    # exec post
    def queryMappingMethod(self,GA,versionPair,rows):
        if len(rows) == 0:
            return []
        methods = []
        # KV: K= method 到V= row的mapping
        tempDict = {}
        for r in rows:
            methods.append(r.method)
            tempDict[r.method] = r
        versions = JavaDocUtil.getVersions(GA,versionPair)
        result = self.postQuery(GA,versionPair,versions,methods)
        toolMapResult:List[RowData]= []
        for entry in result:
            method = entry['method']            
            row = tempDict[method]
            missingValue = entry['missing_key']
            row.setGranularity(missingValue)

            toolMapResult.append(row)
        return toolMapResult

    def postQuery(self,GA,versionPair,versions,methods):
        postStr = {}
        postStr['GA'] = GA
        postStr['version_pair'] = versionPair
        postStr['methods'] = methods
        postStr['versions'] = versions
        # 18123 18124
        req = requests.post('http://10.176.34.86:%s/class_existence' % self.portId,json=postStr)
        content = req.content
        j = json.loads(content)
        return j


