# -*- coding: utf-8 -*- 
import abc
from ILogic import ILogic
import JavaDocUtil
import requests
import json
from typing import List, Tuple, Dict, Set
from ExcelRow import RowData
from xlutils.copy import copy

class ToolMappingLogicAppend(ILogic):

    def __init__(self,portId,runType,gaVersionPair):
        self.portId = portId
        self.runType = runType
        self.gaVersionPair = gaVersionPair

    def initBeforeExcel(self):
        self.GA = None
        self.VPAIR = None

        self.isStart = False
        # precision and recall

        self.allEntries:List[RowData] = []
        # round
        self.roundRows:List[RowData] = []
        self.roundMappedMethodDict:Dict[str,List[str]] = {}

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
        # print('raw: %d/%d' % (len(roundMappedRows),len(self.roundRows)))
        self.precisionAndRecall(roundMappedRows)
        self.resetRound()
        if self.gaVersionPair != "none":
            return True
        return False

    def setExcel(self,rows):
        for r in rows:
            self.mappedRows.append(r)

    def resetRound(self):
        # self.roundMappedMethodDict = {}
        self.roundRows = []

    def doAfterExcelFinish(self,readWorkBook,xlsPath,runType):
        workbook = copy(readWorkBook)
         # 1. sheet1
        sheet0 = workbook.get_sheet(0)
        TFPNDict = {
            "TP":15,
            "FP":16,
            "TN":17,
            "FN":18,
            "tool_mapped_method":19,
            "mapped_type":21,
            "mapping_source":7
        }
        for r in self.allEntries:
            cursor = r.rowId -1

            if r.toolHaveMap == True:

                sheet0.write(cursor,TFPNDict['tool_mapped_method'],r.toolMappedMethod)
                sheet0.write(cursor,TFPNDict['mapped_type'],r.toolMapType)
                sheet0.write(cursor,TFPNDict['mapping_source'],r.sourceType)

                toolSet:set
                mappedMethodSet = set(self.roundMappedMethodDict[r.method])

                toolMethodList = []
                if isinstance(r.toolMappedMethod,str):
                    toolMethodList = r.toolMappedMethod.split('\n')
                else:
                    toolMethodList = r.toolMappedMethod

                toolSet = set(toolMethodList)
                intersectionResult = toolSet & mappedMethodSet
                if len(intersectionResult) >= len(mappedMethodSet):
                    sheet0.write(cursor,14,"Y")
                else:
                    sheet0.write(cursor,14,"N")
                toolResult = "\n".join(toolSet)


                sheet0.write(cursor,TFPNDict['mapped_method'],r.mappedMethods)
                sheet0.write(cursor,TFPNDict['mapped_type'],r.toolMapType)
                sheet0.write(cursor,TFPNDict['mapping_source'],r.sourceType)

                toolSet:set
                mappedMethodSet = set(self.roundMappedMethodDict[r.method])

                if isinstance(r.toolMappedMethod,str):
                    if r.toolMappedMethod in mappedMethodSet:
                        sheet0.write(cursor,14,"Y")
                    elif r.toolMappedMethod.find('\n') != -1:
                        toolList = r.toolMappedMethod.split("\n")
                        toolSet = set(toolList)
                        intersectionResult = toolSet & mappedMethodSet

                        if len(intersectionResult) >= len(mappedMethodSet):
                            sheet0.write(cursor,14,"Y")
                        else:
                            sheet0.write(cursor,14,"N")

                else:
                    #  isinstance(r.toolMappedMethod,list)
                    toolSet = set(r.toolMappedMethod)
                    intersectionResult =  toolSet & mappedMethodSet
                    if len(intersectionResult) >= len(mappedMethodSet):
                        sheet0.write(cursor,14,"Y")

                    else:
                        sheet0.write(cursor,14,"N")
                toolResult = "\n".join(toolSet)
                sheet0.write(cursor,TFPNDict['mapped_method'],toolResult)
                sheet0.write(cursor,TFPNDict['mapped_type'],r.toolMapType)
                sheet0.write(cursor,TFPNDict['mapping_source'],r.sourceType)

        workbook.save(xlsPath + '-%s-m.xls' % runType)
    
    def precisionAndRecall(self,roundMappedRows:List[RowData]):
        '''
        粗略的依靠这个方法来设置 allEntries
        '''

        for row in roundMappedRows:
            # if not (row.isMapping == 'Y' or row.isMapping == 'N'):
            #     #   悬而未决的数据不加进去
            #     continue
            # isMappping Retrival   toolHaveMap=True Positive
            self.allEntries.append(row)
            # if not (row.isMapping == 'Y' or row.isMapping == 'N'):
            #     #   悬而未决的数据不加进去
            #     continue
            # cursor = row.rowId -1
            # columnOffset = TFPNDict[row.TFPN]
            # sheet0.write(cursor,columnOffset,'X')
            # if r.toolHaveMap == True:
            #     sheet1.write(cursor ,TFPNDict['mapped_method'],r.toolMappedMethod)
            #     sheet1.write(cursor ,TFPNDict['mapped_type'],r.toolMapType)



    # load data for one round
    # 遍历每一行，将runType类型的行加进候选查询列表
    def traverseRow(self,rowEntry):
        method = rowEntry.method
        mappedMethods = rowEntry.mappedMethods
        self.appendTempRowData(rowEntry,mappedMethods,method)
    
    # 加入round row，mappedMethodDict保存deleted method和对应的mapping
    def appendTempRowData(self,rowEntry,mappedMethods,method):
        self.roundRows.append(rowEntry)
        value = []
        if '\n' in mappedMethods:
            data = mappedMethods.split('\n')
            for item in data:
                value.append(item)
        else:
            value.append(mappedMethods)
        self.roundMappedMethodDict[method] = value


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
            if entry['find_map'] == True:
                mapType = entry['map_type'] 
                if 'new_ga' in entry:
                    newGA = entry['new_ga']
                    mapType = mapType + ':%s %s %s' %(newGA['groupId'],newGA['artifactId'],newGA['version'])
                # 这个mapped_method是java返回的工具的映射方法
                row.setToolMappedResult1(True,entry['mapped_method'],mapType,entry['source_type'])
            else:
                row.setToolMappedResult1(False,None,None,None)
            toolMapResult.append(row)
        return toolMapResult

    def postQuery(self,GA,versionPair,versions,methods):
        postStr = {}
        postStr['GA'] = GA
        postStr['version_pair'] = versionPair
        postStr['methods'] = methods
        postStr['versions'] = versions
        postStr['phase_name'] = self.runType
        # 18123 18124
        req = requests.post('http://10.176.34.86:%s/deleted_method_mapping' % self.portId,json=postStr)
        content = req.content
        j = json.loads(content)
        return j

    def initSheet3Keys(self,sheet3):
        pass

