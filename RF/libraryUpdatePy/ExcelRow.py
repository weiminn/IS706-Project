

class TableIICell(object):

    def __init__(self,source,relation,num):
        self.source = source
        self.relation = relation
        # cursor -> DataPack
        # cursor RowData
        self.num = num
        self.dataPack = {}
        self.precisionAndRecallPack = []
    
    def calAveragePrecisionAndRecall(self):
        precisionCellAll = 0.0
        recallCellAll = 0.0

        tnRateAll = 0.0
        isNone  = False
        if self.source == 'None':
            isNone = True
        for key in self.dataPack:
            rowData = self.dataPack[key]
            tp = rowData.TP
            fp = rowData.FP
            tn = rowData.TN
            fn = rowData.FN

            # 一条数据的precision recall
            if isNone:
                # tnRate = tn/(tn+fp) 
                if tn + fp == 0:
                    tnRate = 0
                else:
                    tnRate = tn/(tn+fp) 
                self.precisionAndRecallPack.append((tnRate,0.0))
                tnRateAll += tnRate
                continue
            if tp + fp == 0:
                precision = 0
            else:
                precision = tp/(tp+fp)

            if tp+fn == 0:
                recall = 0
            else:
                recall = tp/(tp+fn)
            self.precisionAndRecallPack.append((precision,recall))
            # cell precision recall 总和
            precisionCellAll += precision
            recallCellAll += recall
        # 单条precision recall 加起来
        return isNone,precisionCellAll,recallCellAll,tnRateAll,len(self.dataPack)

    def sumOfYN(self):
        Y = 0
        N = 0
        for key in self.dataPack:
            rowData = self.dataPack[key]
            if rowData.isMapping == 'Y':
                Y+=1
            elif rowData.isMapping == 'N':
                N+=1
        return Y,N
    
    def sumOfTPFPTNFN(self):
        planA = {}
        planA['sTp'] = 0.0
        planA['sFp'] = 0.0
        planA['sTn'] = 0.0
        planA['sFn'] = 0.0
        planB = {}
        planB['sTpForPrecision'] = 0.0
        planB['sTpForRecall'] = 0.0
        planB['sFp'] = 0.0
        planB['sTn'] = 0.0
        planB['sFn'] = 0.0


        for key in self.dataPack:
            rowData = self.dataPack[key]
            planA['sTp'] += rowData.TP
            planA['sFp'] += rowData.FP
            planA['sTn'] += rowData.TN
            planA['sFn'] += rowData.FN

            prefenmu =  rowData.TP + rowData.FP
            recafenmu = rowData.TP + rowData.FN
            if prefenmu == 0:
                prefenmu  = 0
            else:
                planB['sTpForPrecision'] += rowData.TP/prefenmu
            if recafenmu == 0:
                recafenmu = 0
            else:
                planB['sTpForRecall'] += rowData.TP/recafenmu
            planB['sFp'] += rowData.FP/prefenmu
            planB['sTn'] += rowData.TN
            planB['sFn'] += rowData.FN/recafenmu 
        return planA,planB,self.num

class TableIICellJson(object):

    def calAveragePrecisionAndRecall(self,cell):
        precisionCellAll = 0.0
        recallCellAll = 0.0
        tnRateAll = 0.0
        isNone  = False
        if cell['source'] == 'None':
            isNone = True
        for key in cell['dataPack']:
            rowData = cell['dataPack'][key]
            tp = rowData['TP']
            fp = rowData['FP']
            tn = rowData['TN']
            fn = rowData['FN']
            # 一条数据的precision recall
            # if isNone:
            #     # tnRate = tn/(tn+fp) 
            #     if tn + fp == 0:
            #         tnRate = 0
            #     else:
            #         tnRate = tn/(tn+fp) 
            #     cell['precisionAndRecallPack'].append((tnRate,0.0))
            #     tnRateAll += tnRate
            #     continue
            if tp + fp == 0:
                precision = 0
            else:
                precision = tp/(tp+fp)

            if tp+fn == 0:
                recall = 0
            else:
                recall = tp/(tp+fn)
            cell['precisionAndRecallPack'].append((precision,recall))
            # cell precision recall 总和
            precisionCellAll += precision
            recallCellAll += recall
        # 单条precision recall 加起来
        return isNone,precisionCellAll,recallCellAll,tnRateAll,len(cell['dataPack'])

    def sumOfYN(self,cell):
        Y = 0
        N = 0
        for key in cell['dataPack']:
            rowData = cell['dataPack'][key]
            if rowData['isMapping'] == 'Y':
                Y+=1
            elif rowData['isMapping'] == 'N':
                N+=1
        return Y,N
    
    def sumOfTPFPTNFN(self,cell):
        planA = {}
        planA['sTp'] = 0.0
        planA['sFp'] = 0.0
        planA['sTn'] = 0.0
        planA['sFn'] = 0.0
        planB = {}
        planB['sTpForPrecision'] = 0.0
        planB['sTpForRecall'] = 0.0
        planB['sFp'] = 0.0
        planB['sTn'] = 0.0
        planB['sFn'] = 0.0

        for key in cell['dataPack']:

            rowData = cell['dataPack'][key]
            # print(rowData)
            planA['sTp'] += rowData['TP']
            planA['sFp'] += rowData['FP']
            planA['sTn'] += rowData['TN']
            planA['sFn'] += rowData['FN']


            prefenmu =  rowData['TP'] + rowData['FP']
            recafenmu = rowData['TP'] + rowData['FN']
            if prefenmu == 0:
                prefenmu  = 0
            else:
                planB['sTpForPrecision'] += rowData['TP']/prefenmu
            if recafenmu == 0:
                recafenmu = 0
            else:   
                planB['sTpForRecall'] += rowData['TP']/recafenmu
            if prefenmu != 0:
                planB['sFp'] += rowData['FP']/prefenmu
            planB['sTn'] += rowData['TN']
            if recafenmu !=0 :
                planB['sFn'] += rowData['FN']/recafenmu
        return planA,planB,cell['num']



class RowData(object):

    def __init__(self,rowId,GA,vPair,isMapping,method,mappedMethod,mappingSource,mappedMethodRelation):
        self.rowId = rowId
        self.GA = GA
        self.vPair = vPair
        self.method = method
        self.isMapping = isMapping
        self.mappingSource = mappingSource
        self.mappedMethodRelation = mappedMethodRelation
        self.mappedMethods = mappedMethod
        self.nton = None

        self.TFPN = []

        self.TP = 0
        self.FP = 0
        self.TN = 0
        self.FN = 0
        self.N = 0
    
    def setToolMappedResult(self,toolHaveMap,toolMappedMethod,mapType):
        # toolHaveMap true or fase
        self.toolHaveMap = toolHaveMap
        self.toolMappedMethod = toolMappedMethod
        self.toolMapType = mapType 

    def setToolMappedResult1(self,toolHaveMap,toolMappedMethod,mapType,sourceType):
        # toolHaveMap true or fase
        self.toolHaveMap = toolHaveMap
        self.toolMappedMethod = toolMappedMethod
        self.toolMapType = mapType 
        self.sourceType = sourceType

    def setGranularity(self,granularity):
        self.granularity = granularity