
from libraryUpdatePy.empiricalData.DataBean.BeanAPISeq import BeanAPISeq
import numpy as np
from libraryUpdatePy.empiricalData.DataBean.BeanAPI import BeanAPI
from functools import cmp_to_key

class SimilarityMatrix(object):

    def buildMatrix(self,seqV0,seqV1,deletedMethod):
        self.l0 = len(seqV0)
        self.l1 = len(seqV1)
        self.dim = self.l0+self.l1
        mat = np.zeros((self.dim, self.dim))
        self.deletedMethod = deletedMethod
        self.mat = mat
        self.seqV0 = seqV0
        self.seqV1 = seqV1
        self.mMap = {}
        for i in range(0,len(seqV0)):
            self.mMap[seqV0[i]] = i
        for i in range(0,len(seqV1)):
            self.mMap[seqV1[i]] = i + self.l0
        self.mMap2 = {}
        for key in self.mMap:
            self.mMap2[self.mMap[key]] = key
        
    # 剩下的方法
    # (List of method from seq) - prevMethods/deletedMethod
    # return None 如果为空表示没有重叠
    # return List of method 如果不为空，返回补集
    def getRestofMethods(self,seq:BeanAPISeq, prevMethods):
        inp = []
        if type(prevMethods) == str:
            inp.append(prevMethods)
        elif type(prevMethods) == list:
            inp = prevMethods
        isFdse = False
        for m in prevMethods:
            if '__fdse__' in m:
                isFdse = True
            else:
                isFdse = False
            break
        res = []
        beanAPIList = seq.getBeanAPIList()
        isHave = False
        for beanAPI in beanAPIList:
            api = beanAPI.getAPIName()
            if isFdse:
                name = api
            else:
                data = api.split('__fdse__')
                name = data[-1]
            if name in prevMethods:
                isHave = True
            else:
                res.append(api)
        if isHave:
            return res
        else:
            return None

    def calculateDis(self,a:BeanAPISeq,b:BeanAPISeq):
        startIndex = self.mMap[a]
        endIndex = self.mMap[b]
        #  频次相加
        dis = a.getFrequencyV1() + b.getFrequencyV1()
        self.mat[startIndex][endIndex] = dis

    # overlap method -> find Next
    def step(self,depth,srcSeq,overlapMethod,dstSeqList):
        if depth == 0:
            return 
        srcToOverleppedMethodMap = {}
        for seqDst in dstSeqList:
            if seqDst == srcSeq:
                continue
            stepMethods = self.getRestofMethods(seqDst,overlapMethod)
            if stepMethods  == None or len(stepMethods) == 0:
                continue
            srcToOverleppedMethodMap[seqDst] = stepMethods
            self.calculateDis(srcSeq, seqDst)
        for seq in srcToOverleppedMethodMap:
            self.step(depth-1,seq,srcToOverleppedMethodMap[seq], self.seqV1)

            

    def queryMat(self):
        for srcSeq in self.seqV0:
            nextMethod = []
            beanAPIList = srcSeq.getBeanAPIList()
            for beanAPI in beanAPIList:
                api = beanAPI.getAPIName()
                data = api.split('__fdse__')
                if data[-1] != self.deletedMethod:
                    nextMethod.append(api)
            self.step(3,srcSeq,nextMethod,self.seqV1)
        print('getSeqsChainFromMat')
        chains,disList = self.getSeqsChainFromMat()
        return chains,disList


    #
    def getSeqsChainFromMat(self):
        res = []
        testSet = set()
        for seq in self.seqV0:
            index = self.mMap[seq]
            for i in range(self.l0, self.dim):
                dis = self.mat[index][i]
                if dis !=0:
                    for j in range(self.l0,self.dim):
                        if i == j:
                            continue
                        dis2 = self.mat[i][j]
                        if dis2 !=0:
                            entry = []
                            entry.append(index)
                            entry.append(i)
                            entry.append(j)
                            res.append(entry)
                            testSet.add(i)
                            testSet.add(j)
                            testSet.add(index)
                    entry = []
                    entry.append(index)
                    entry.append(i)
                    res.append(entry)
                    testSet.add(i)
                    testSet.add(index)
        disD = {}
        for i in range(0,len(res)):
            entry = res[i]
            dis = 0
            for item in entry:
                f = self.mMap2[item].getFrequencyV1()
                dis += f
            disD[i] = dis
        rankList = sorted(disD.items(),key=cmp_to_key(self.mycmpId))
        res2 = []
        disList = []
        for tup in rankList:
            index = tup[0]
            dis = tup[1]
            res2.append(res[index])
            disList.append(dis)
        
        a = set([746, 747, 1395, 1434, 1611, 1700])
        # if len(a & testSet) != 0:
            # print('found')
            # print(a & testSet)
        # print(testSet)
        return res2,disList

    def mycmpId(self,a,b):
        # desc
        if a[1] < b[1]:
            return -1
        else:
            return 1

    # map 的方法所在的顺序
    def getIndex(self,listOfRankedSeqs,disList,mappedMethod):
        index = None
        isFound = False
        for i in range(0,len(listOfRankedSeqs)):
            entry = listOfRankedSeqs[i]
            for j in range(1,len(entry)):
                seqId = entry[j]
                seq = self.mMap2[seqId]
                beanAPIList = seq.getBeanAPIList()
                for beanAPI in beanAPIList:
                    apiName = beanAPI.getAPIName()
                    data = apiName.split('__fdse__')
                    name = data[-1]
                    if name == mappedMethod:
                        isFound = True
                        index = i
                        break
                if isFound:
                    break
        return (index,len(listOfRankedSeqs))


