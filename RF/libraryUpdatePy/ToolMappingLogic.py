# -*- coding: utf-8 -*- 
import abc
from ILogic import ILogic
import JavaDocUtil
import requests
import json
from typing import List, Tuple, Dict, Set
from ExcelRow import RowData,TableIICell,TableIICellJson
from xlutils.copy import copy

class ToolMappingLogic(ILogic):

    def __init__(self,portId,runType,gaVersionPair):
        self.portId = portId
        self.runType = runType
        self.gaVersionPair = gaVersionPair
        self.srcList = None
        

    def initBeforeExcel(self,sensePack):

        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/compare-gt/excel_relation_to_paper.json','r') as f:
            j = json.load(f)
        self.srcList = j['source_list']
        self.relationList = j['relation_list']
        self.srcMap = j['source_map']
        self.relationMap = j['relation_map']
        self.sensePack = sensePack

        self.GA = None
        self.VPAIR = None

        self.isStart = False


        self.allEntries:List[RowData] = []
        # round
        self.roundRows:List[RowData] = []
        self.roundMappedMethodDict:Dict[str,List[str]] = {}
        self.oneToOneType:Dict[str,str] = {}
        # # TP
        # self.truePositiveEntries:List[RowData] = []
        # self.toolMapTrueEntries:List[RowData] = []
        # self.toolMapFalseEntries:List[RowData] =[]

        # # FP false positive Entries
        # self.falsePositiveEntries:List[RowData] = []

        # # negatives  TN
        # self.trueNegativeEntries:List[RowData] = []
        # # FN
        # self.falseNegativeEntries:List[RowData] = []


    def initSheet4Keys(self,usageDict):
        self.tblIIData = {}
        for source in usageDict:
            for relation in self.relationList:
                if relation in usageDict[source]:
                    if not source in self.tblIIData:
                        self.tblIIData[source] = {}
                    if not relation in self.tblIIData[source]:
                        self.tblIIData[source][relation] = TableIICell(source,relation,usageDict[source][relation])

    def doWithGAMethods(self,GA,VPAIR):
        self.GA = GA
        self.VPAIR = VPAIR
        print('GA version pair: %s__fdse__%s' % (GA,VPAIR))
        if self.gaVersionPair != "none" and self.gaVersionPair == self.GA + '__fdse__' + self.VPAIR:
            self.isStart = True
        if self.gaVersionPair != "none" and not self.isStart:
            self.resetRound()
            return False
        resultRows:List[RowData] = self.queryMappingMethod(GA,VPAIR,self.roundRows)
        # print('raw: %d/%d' % (len(roundMappedRows),len(self.roundRows)))
        self.precisionAndRecall(resultRows)
        # self.setExcel(roundMappedRows)
        # for r in roundMappedRows:
        #     self.mappedRows.append(r)
        self.resetRound()
        if self.gaVersionPair != "none":
            return True
        return False
    
    def resetRound(self):
        self.roundMappedMethodDict = {}
        self.roundRows = []

    # load data for one round
    # 遍历每一行，将runType类型的行加进候选查询列表
    def traverseRow(self,rowEntry):
        mappingSource = rowEntry.mappingSource
        mappedMethods = rowEntry.mappedMethods
        method = rowEntry.method
        if not (rowEntry.isMapping == 'Y' or rowEntry.isMapping == 'N'):
            return
        src,rel = self.transExcelKeyToPaperKey(rowEntry.isMapping,rowEntry.mappingSource,rowEntry.mappedMethodRelation)
        myCell = self.tblIIData[src][rel]
        if 'javadoc' == self.runType and "JavaDoc" in mappingSource:
            self.appendTempRowData(rowEntry,mappedMethods,method,myCell)
        if 'jar' == self.runType and "Jar" == mappingSource:
            self.appendTempRowData(rowEntry,mappedMethods,method,myCell)
        if 'jar3' == self.runType and ("Jar ThirdLib" in mappingSource or "Jar Module" in mappingSource):
            self.appendTempRowData(rowEntry,mappedMethods,method,myCell)
        if 'all' == self.runType:
            self.appendTempRowData(rowEntry,mappedMethods,method,myCell)


    # 加入round row，mappedMethodDict保存deleted method和对应的mapping
    def appendTempRowData(self,rowEntry,mappedMethods,method,myCell):
        myCell.dataPack[rowEntry.rowId] = rowEntry
        self.roundRows.append(rowEntry)
        value = []
        if '\n' in mappedMethods:
            data = mappedMethods.split('\n')
            for item in data:
                value.append(item)
        else:
            value.append(mappedMethods)
        self.oneToOneType[method]  = rowEntry.nton
        self.roundMappedMethodDict[method] = value
    

    def precisionAndRecall(self,roundResultRows:List[RowData]):
        for row in roundResultRows:
            if not (row.isMapping == 'Y' or row.isMapping == 'N'):
                #   悬而未决的数据不加进去
                continue
            # isMappping Retrival   toolHaveMap=True Positive
            method = row.method
            gtMethod = set(self.roundMappedMethodDict[method])
            lenGtMethod = len(gtMethod)
            if row.isMapping == 'Y' and row.toolHaveMap == True:
                toolMappedMethod = row.toolMappedMethod
                toolMappedSet = set()
                if type(toolMappedMethod) == list:
                    toolMappedSet = set(toolMappedMethod)
                elif type(toolMappedMethod) == str:
                    toolMappedSet.add(toolMappedMethod)
                # 交集
                intersect = len(toolMappedSet & gtMethod)
                a_b = len(gtMethod - toolMappedSet)
                b_a = len(toolMappedSet - gtMethod)
                   
                if row.nton == '1 to i':
                    if intersect > 0:
                        intersect = 1
                    if a_b > 0:
                        a_b = 0
                    if b_a > 0:
                        b_a = 0

                if intersect!=0:
                    row.TP += intersect
                    row.TFPN.append('TP')
                # 错误的
                if b_a != 0:
                    row.FP += b_a
                    row.TFPN.append('FP')
                # 漏的
                if intersect!=0 and a_b!=0:
                    row.FN += a_b
                    row.TFPN.append('FN')

            if row.isMapping == 'Y' and row.toolHaveMap == False:
                row.FN += len(self.roundMappedMethodDict[method])
                row.TFPN.append('FN')

            if row.isMapping == 'N' and row.toolHaveMap == True:
                # row.FP += len(row.toolMappedMethod)
                row.FP += 1
                # row.TFPN.append('FP')
                # row.TFPN.append('FN') 
                row.TFPN.append('FN')
            if row.isMapping == 'N' and row.toolHaveMap == False:
                # row.TN += len(self.roundMappedMethodDict[method])
                row.TN += 1
                # row.TFPN.append('TN')
                row.TFPN.append('TP')
            self.allEntries.append(row)

    def doAfterExcelFinish1(self,readWorkBook,xlsPath,runType,duration):
        workbook = copy(readWorkBook)
        # 1. sheet1
        sheet0 = workbook.get_sheet(0)
        TFPNDict = {
            "TP":15,
            "FP":16,
            "TN":17,
            "FN":18,
            "mapped_method":19,
            "mapped_type":21
        }
        
        for r in self.allEntries:
            # if not (row.isMapping == 'Y' or row.isMapping == 'N'):
            #     #   悬而未决的数据不加进去
            #     continue
            cursor = r.rowId -1
            for t in r.TFPN:
                columnOffset = TFPNDict[t]
                sheet0.write(cursor,columnOffset,'X')
            if r.toolHaveMap == True:
                sheet0.write(cursor ,TFPNDict['mapped_method'],r.toolMappedMethod)
                sheet0.write(cursor ,TFPNDict['mapped_type'],r.toolMapType)
        
        # 2. sheet4
        sheet4 = workbook.get_sheet(4)
        sheet4.write(0,18,"Duration")
        sheet4.write(0,19,duration)
        row = 1
        TFPNDict2 = {
            "Y":2,
            "N":3,
            "TP":4,
            "FP":5,
            "TN":6,
            "FN":7,
            "sum":8,
            "pre":9,
            "rec":10
        }
        preTotoalTotal = 0.0
        recTotalTotal = 0.0
        cntTotalTotal = 0.0
        tnRateTotalTotal = 0.0
        tpPreTotal = 0
        tpRecTotal = 0
        fpTotal = 0
        tnTotal = 0
        fnTotal = 0
        for i in range(0,len(self.srcList)):
            source = self.srcList[i]
            # 每个source下precision recall总和
            preTotal = 0.0
            recTotal = 0.0
            cntTotal = 0.0
            tnRateTotal = 0.0
            isFirst = True
            print(source)
            for relation in self.relationList:
                sourceTmp = ' '

                if isFirst == True:
                    sourceTmp = source
                    isFirst = False
                # print(sourceTmp+ " "+ relation)
                if not (source in self.tblIIData and relation in self.tblIIData[source]):
                    # -
                    sheet4.write(row,0,sourceTmp)
                    sheet4.write(row,1,relation)
                    sheet4.write(row,TFPNDict2['Y'],'-')
                    sheet4.write(row,TFPNDict2['N'],'-')
                    sheet4.write(row,TFPNDict2['TP'],'-')
                    sheet4.write(row,TFPNDict2['FP'],'-')
                    sheet4.write(row,TFPNDict2['TN'],'-')
                    sheet4.write(row,TFPNDict2['FN'],'-')
                    sheet4.write(row,TFPNDict2['sum'],'-')
                    sheet4.write(row,TFPNDict2['pre'],'-')
                    sheet4.write(row,TFPNDict2['rec'],'-')
                    row+=1
                    continue    
                tblCell = self.tblIIData[source][relation]
                if len(tblCell.dataPack) == 0:
                    sheet4.write(row,0,sourceTmp)
                    sheet4.write(row,1,relation)
                    sheet4.write(row,TFPNDict2['Y'],'x')
                    sheet4.write(row,TFPNDict2['N'],'x')
                    sheet4.write(row,TFPNDict2['TP'],'x')
                    sheet4.write(row,TFPNDict2['FP'],'x')
                    sheet4.write(row,TFPNDict2['TN'],'x')
                    sheet4.write(row,TFPNDict2['FN'],'x')
                    sheet4.write(row,TFPNDict2['sum'],'x')
                    sheet4.write(row,TFPNDict2['pre'],'x')
                    sheet4.write(row,TFPNDict2['rec'],'x')
                    row+=1
                    continue
                y,n = tblCell.sumOfYN()
                tpPre,tpRec,fp,tn,fn,s = tblCell.sumOfTPFPTNFN()
                tpPreTotal += tpPre
                tpRecTotal += tpRec
                fpTotal += fp
                tnTotal += tn
                fnTotal += fn
                # 每个 source,relation的子类 prrecision recall 总和
                isNone,pre,rec,tnRate,cnt = tblCell.calAveragePrecisionAndRecall()
                if cnt == 0:
                    row+=1
                    continue
                sheet4.write(row,0,sourceTmp)
                sheet4.write(row,1,relation)
                sheet4.write(row,TFPNDict2['Y'],y)
                sheet4.write(row,TFPNDict2['N'],n)
                sheet4.write(row,TFPNDict2['TP'],tpPreTotal)
                sheet4.write(row,TFPNDict2['FP'],fp)
                sheet4.write(row,TFPNDict2['TN'],tn)
                sheet4.write(row,TFPNDict2['FN'],fn)
                sheet4.write(row,TFPNDict2['sum'],s)
                if isNone:
                    sheet4.write(row,TFPNDict2['pre'],tnRate/cnt)
                    tnRateTotal += tnRate
                else:
                    sheet4.write(row,TFPNDict2['pre'],pre/cnt)
                    sheet4.write(row,TFPNDict2['rec'],rec/cnt)
                    preTotal += pre
                    recTotal += rec
                cntTotal += cnt
                row += 1
            if cntTotal == 0:
                continue
            sheet4.write(i+1,12,preTotal/cntTotal)
            sheet4.write(i+1,13,recTotal/cntTotal)
            sheet4.write(i+1,14,tnRateTotal/cntTotal)
            sheet4.write(i+1,15,cntTotal)
            preTotoalTotal += preTotal
            recTotalTotal += recTotal
            tnRateTotalTotal += tnRateTotal
            cntTotalTotal += cntTotal

        averPrecision = preTotoalTotal/583
        averRecall = recTotalTotal/583
        averTnRate = tnRateTotalTotal/100
        sheet4.write(1,18,averPrecision)
        sheet4.write(1,19,averRecall)
        sheet4.write(1,20,averTnRate)
        sheet4.write(1,21,cntTotalTotal)
        precisionPlanB = tpPreTotal/(tpPreTotal+fpTotal)
        recallPlanB = tpRecTotal/(tpRecTotal+fnTotal)
        print('plan B pre: %.2f' % precisionPlanB)
        print('plan B rec: %.2f' % recallPlanB)
        f1 = 2* averPrecision * averRecall /(averPrecision + averRecall)
        sheet4.write(1,22,f1)
        if self.sensePack == None:
            workbook.save(xlsPath[0:-4] + '-%s-auto-.xls' % runType)
        else:
            workbook.save(xlsPath[0:-4] + '-%s-auto-%f.xls' % (runType,self.sensePack[1]))
        return averPrecision,averRecall,f1

    def doAfterExcelFinish2(self,readWorkBook,xlsPath,toolData,runType,duration):
        workbook = copy(readWorkBook)
        # 1. sheet1
        sheet0 = workbook.get_sheet(0)
        TFPNDict = {
            "TP":15,
            "FP":16,
            "TN":17,
            "FN":18,
            "mapped_method":19,
            "mapped_type":21
        }
        
        for r in toolData['allEntries']:
            # if not (row.isMapping == 'Y' or row.isMapping == 'N'):
            #     #   悬而未决的数据不加进去
            #     continue
            cursor = r['rowId'] -1
            for t in r['TFPN']:
                columnOffset = TFPNDict[t]
                sheet0.write(cursor,columnOffset,'X')
            if r['toolHaveMap'] == True:
                sheet0.write(cursor ,TFPNDict['mapped_method'],r['toolMappedMethod'])
                sheet0.write(cursor ,TFPNDict['mapped_type'],r['toolMapType'])
        
        # 2. sheet4
        sheet4 = workbook.get_sheet(4)
        sheet4.write(0,18,"Duration")
        sheet4.write(0,19,duration)
        row = 1
        TFPNDict2 = {
            "Y":2,
            "N":3,
            "TP":4,
            "FP":5,
            "TN":6,
            "FN":7,
            "sum":8,
            "pre":9,
            "rec":10
        }
        preTotoalTotal = 0.0
        recTotalTotal = 0.0
        cntTotalTotal = 0.0
        tnRateTotalTotal = 0.0
        tpPreTotal = 0
        tpRecTotal = 0
        fpTotal = 0
        tnTotal = 0
        fnTotal = 0 
        for i in range(0,len(self.srcList)):
            source = self.srcList[i]
            # 每个source下precision recall总和
            preTotal = 0.0
            recTotal = 0.0
            cntTotal = 0.0
            tnRateTotal = 0.0
            isFirst = True
            print(source)
            for relation in self.relationList:
                sourceTmp = ' '

                if isFirst == True:
                    sourceTmp = source
                    isFirst = False
                # print(sourceTmp+ " "+ relation)
                if not (source in toolData['tblIIData'].keys() and relation in toolData['tblIIData'][source].keys()):
                    # -
                    sheet4.write(row,0,sourceTmp)
                    sheet4.write(row,1,relation)
                    sheet4.write(row,TFPNDict2['Y'],'-')
                    sheet4.write(row,TFPNDict2['N'],'-')
                    sheet4.write(row,TFPNDict2['TP'],'-')
                    sheet4.write(row,TFPNDict2['FP'],'-')
                    sheet4.write(row,TFPNDict2['TN'],'-')
                    sheet4.write(row,TFPNDict2['FN'],'-')
                    sheet4.write(row,TFPNDict2['sum'],'-')
                    sheet4.write(row,TFPNDict2['pre'],'-')
                    sheet4.write(row,TFPNDict2['rec'],'-')
                    row+=1
                    continue    
                tblCell = toolData['tblIIData'][source][relation]
                if len(tblCell['dataPack']) == 0:
                    sheet4.write(row,0,sourceTmp)
                    sheet4.write(row,1,relation)
                    sheet4.write(row,TFPNDict2['Y'],'x')
                    sheet4.write(row,TFPNDict2['N'],'x')
                    sheet4.write(row,TFPNDict2['TP'],'x')
                    sheet4.write(row,TFPNDict2['FP'],'x')
                    sheet4.write(row,TFPNDict2['TN'],'x')
                    sheet4.write(row,TFPNDict2['FN'],'x')
                    sheet4.write(row,TFPNDict2['sum'],'x')
                    sheet4.write(row,TFPNDict2['pre'],'x')
                    sheet4.write(row,TFPNDict2['rec'],'x')
                    row+=1
                    continue
                cellUtil = TableIICellJson()
                y,n = cellUtil.sumOfYN(tblCell)
                # if source == 'None':
                #     print(tblCell)
                planA,planB,s = cellUtil.sumOfTPFPTNFN(tblCell)
                planAorB = False
                if planAorB:
                    # planA
                    sPlan = planA
                    tpPreTotal += planA['sTp']
                    tpRecTotal += planA['sTp']
                    fpTotal += planA['sFp']
                    # if planA['sFp'] !=0:
                    #     print(planA['sFp'])
                    tnTotal += planA['sTn']
                    fnTotal += planA['sFn']
                    tp = planA['sTp']
                    fp = planA['sFp']
                    tn = planA['sTn']
                    fn = planA['sFn']
                else:
                    sPlan = planB
                    tpPreTotal += planB['sTpForPrecision']
                    tpRecTotal += planB['sTpForRecall'] 
                    fpTotal += planB['sFp']
                    tnTotal += planB['sTn']
                    fnTotal += planB['sFn']
                    tp = planB['sTpForPrecision']
                    fp = planB['sFp']
                    tn = planB['sTn']
                    fn = planB['sFn']
                # 每个 source,relation的子类 prrecision recall 总和
                isNone,pre,rec,tnRate,cnt = cellUtil.calAveragePrecisionAndRecall(tblCell)
                if cnt == 0:
                    row+=1
                    continue
                sheet4.write(row,0,sourceTmp)
                sheet4.write(row,1,relation)
                sheet4.write(row,TFPNDict2['Y'],y)
                sheet4.write(row,TFPNDict2['N'],n)
                sheet4.write(row,TFPNDict2['TP'],tp)
                sheet4.write(row,TFPNDict2['FP'],fp)
                sheet4.write(row,TFPNDict2['TN'],tn)
                sheet4.write(row,TFPNDict2['FN'],fn)
                sheet4.write(row,TFPNDict2['sum'],s)
                # if isNone:
                #     sheet4.write(row,TFPNDict2['pre'],tnRate/cnt)
                #     tnRateTotal += tnRate
                # else:
                sheet4.write(row,TFPNDict2['pre'],pre/cnt)
                sheet4.write(row,TFPNDict2['rec'],rec/cnt)
                preTotal += pre
                recTotal += rec
                cntTotal += cnt
                row += 1
            if cntTotal == 0:
                continue
            sheet4.write(i+1,12,preTotal/cntTotal)
            sheet4.write(i+1,13,recTotal/cntTotal)
            sheet4.write(i+1,14,tnRateTotal/cntTotal)
            sheet4.write(i+1,15,cntTotal)
            preTotoalTotal += preTotal
            recTotalTotal += recTotal
            tnRateTotalTotal += tnRateTotal
            cntTotalTotal += cntTotal

        averPrecision = preTotoalTotal/583
        averRecall = recTotalTotal/583
        averTnRate = tnRateTotalTotal/100
        sheet4.write(1,18,averPrecision)
        sheet4.write(1,19,averRecall)
        sheet4.write(1,20,averTnRate)
        sheet4.write(1,21,cntTotalTotal)
        print('tppretotal:%.2f' % tpPreTotal)
        print('fpTotal: %.2f' % fpTotal)
        precisionPlanB = tpPreTotal/(tpPreTotal+fpTotal)
        recallPlanB = tpRecTotal/(tpRecTotal+fnTotal)
        print('plan B pre: %.2f' % precisionPlanB)
        print('plan B rec: %.2f' % recallPlanB)
        f1 = 2* averPrecision * averRecall /(averPrecision + averRecall)
        sheet4.write(1,22,f1)
        if self.sensePack == None:
            workbook.save(xlsPath[0:-4] + '-%s-auto-.xls' % runType)
        else:
            workbook.save(xlsPath[0:-4] + '-%s-auto-%f.xls' % (runType,self.sensePack[1]))
        return averPrecision,averRecall,f1


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
                s = ''
                if 'new_ga' in entry:
                    s += entry['new_ga']['groupId'] + ':'
                    # print(entry['new_ga'])
                    s += entry['new_ga']['artifactId'] + ':'
                    s += entry['new_ga']['version'] + ':'
                row.setToolMappedResult(True,entry['mapped_method'],entry['map_type'] +' '+ s)
            else:
                row.setToolMappedResult(False,None,None)
            toolMapResult.append(row)
        return toolMapResult

    def postQuery(self,GA,versionPair,versions,methods):
        postStr = {}
        postStr['GA'] = GA
        postStr['version_pair'] = versionPair
        postStr['methods'] = methods
        postStr['versions'] = versions
        postStr['phase_name'] = self.runType
        if self.sensePack != None:
            postStr[self.sensePack[0]] = self.sensePack[1]
        # 18123 18124
        req = requests.post('http://10.176.34.86:%s/deleted_method_mapping' % self.portId,json=postStr)
        content = req.content
        j = json.loads(content)
        return j
    # 
    def transExcelKeyToPaperKey(self,isMapping,source,relation):
        src = self.srcMap[source]
        rela  = self.relationMap[relation]
        if rela == 'Class Deletion' or rela == 'Method Deletion':
            src = 'None'

        return src,rela

        
    # # deprecated
    # def doAfterExcelFinish(self,readWorkBook,xlsPath,runType):
    #     nomi = len(self.truePositiveEntries)
    #     denomi = len(self.truePositiveEntries) + len(self.falsePositiveEntries)
    #     denomi2 = len(self.truePositiveEntries) + len(self.falseNegativeEntries)

    #     print('final precision: %f' % (nomi/denomi))
    #     print('final recall: %f'%(nomi/denomi2))
    #     print('map accuracy: %f'%(len(self.toolMapTrueEntries)/len(self.truePositiveEntries)))

    #     workbook = copy(readWorkBook)
    #     sheet1 = workbook.get_sheet(0)
    #     TFPNDict = {
    #         "TP":15,
    #         "FP":16,
    #         "TN":17,
    #         "FN":18,
    #         "TP_T":19,
    #         "TP_F":20,
    #         "mapped_method":21,
    #         "mapped_type":22
    #     }

    #     for r in self.allEntries:
    #         #   悬而未决的数据不加进去
    #         cursor = r.rowId -1
    #         columnOffset = TFPNDict[r.TFPN]
    #         sheet1.write(cursor,columnOffset,'X')
    #         if r.toolHaveMap == True:
    #             sheet1.write(cursor ,TFPNDict['mapped_method'],r.toolMappedMethod)
    #             sheet1.write(cursor ,TFPNDict['mapped_type'],r.toolMapType)
        
    #     sheet3 = workbook.get_sheet(3)

    #     TFPNDict2 = {
    #         "TP":4,
    #         "FP":5,
    #         "TN":6,
    #         "FN":7,
    #         "TP_T":8,
    #         "TP_F":9,
    #         "sum":10
    #     }
    #     for key in self.sheet3Data:
    #         di = self.sheet3Data[key]
    #         rowIndex = self.sheet3KeyRowMap[key]
    #         if di['TP']!=0:
    #             sheet3.write(rowIndex,TFPNDict2['TP'],di['TP'])
    #         if di['FP']!=0:
    #             sheet3.write(rowIndex,TFPNDict2['FP'],di['FP'])
    #         if di['TN'] !=0:
    #             sheet3.write(rowIndex,TFPNDict2['TN'],di['TN'])
    #         if di['FN']!=0:
    #             sheet3.write(rowIndex,TFPNDict2['FN'],di['FN'])
    #         sheet3.write(rowIndex,TFPNDict2['sum'],di['sum'])
    #     workbook.save(xlsPath + '-%s-m.xls' % runType)

    #     # sheet 3 add TN/TP/FN/TP + 1
    # def setSheet3Data(self,row:RowData,subKey):
    #     key = row.isMapping + ":" + row.mappingSource + ":" + row.mappedMethodRelation
    #     if key not in self.sheet3Data:
    #         # init
    #         self.sheet3Data[key] = {}
    #         self.sheet3Data[key]['sum'] = 0
    #         self.sheet3Data[key]['TP'] = 0
    #         self.sheet3Data[key]['FP'] = 0
    #         self.sheet3Data[key]['TN'] = 0
    #         self.sheet3Data[key]['FN'] = 0
    #         self.sheet3Data[key]['TP_T'] = 0
    #         self.sheet3Data[key]['TP_F'] = 0
    #     # add 
    #     self.sheet3Data[key][subKey] += 1
    #     if subKey != "sum":
    #         row.TFPN = subKey
    
