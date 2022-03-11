from libraryUpdatePy.empiricalData.E_genDB import m,m2
from libraryUpdatePy.empiricalData.K_ValidateDeletedMethodUsage import dumpUsage
from libraryUpdatePy.empiricalData.I_FIMMergeTable import buildTablePartial

from libraryUpdatePy.empiricalData import Common
import json
from libraryUpdatePy.empiricalData.K_ValidateDeletedMethodUsage import isDstMethodsExistsInFIM,isDstMethodsExistsInFIMMerge,isDstMethodsExistsInUsage,saveToFilteredGt,isDstMethodsExistsInOtherUsage
from libraryUpdatePy.empiricalData.L_SourceCodeUsage import matchedMethods
# 1. genDb,select pair, FIM
# m()


# 2. java diff，generateRawGroundTruth
#
# m2()

#  拿到Excel.csv ，人工核验生成标准答案 生成 del-gt-1-28.json

#  读取 del-gt-1-28.json 生成usage 数据、FIM 数据、FIM Merge数据
#

# 3.  manually selected version pair
def dumpUsageFIMAndFIMMerge():
    # buildTablePartial('21-1-28','21-1-28','21-1-28')
    # dump Usage Raw, Usage FIM and Usage Merge
    # buildTablePartial('21-1-28','21-1-28','21-1-28')
    dumpUsage()

# dumpUsageFIMAndFIMMerge()


#  读取 del-gt-1-28.json 验证 usage 数据、FIM 数据、FIM Merge数据
#

def readUsageFIMAndFIMMerge():
    with open(Common.DELETED_METHOD_GROUND_TRUTH % '1-28','r') as f:
        gt = json.load(f)
    s = 0
    numa = 0
    numb = 0
    numc = 0
    numd = 0
    nume = 0
    result = {}
    for gaHash in gt:
        for versionpair in gt[gaHash]:
            data = versionpair.split('__fdse__')
            v0 = data[0]
            v1 = data[1]
            for entry in gt[gaHash][versionpair]:
                srcMethod = entry['src']
                dstMethods = entry['dst']
                s += 1
                # a/sum
                a = isDstMethodsExistsInUsage(gaHash,v1,dstMethods)
                numa += a
                # b/sum
                if a == 1: 
                    # v1就有usage的
                    # 查看 a = 1 的usage
                    if numb == 30:
                        print('aa')
                    b = isDstMethodsExistsInFIM(gaHash,v1,dstMethods)
                    entry['id'] = numb
                    saveToFilteredGt(result,gaHash,versionpair,entry)
                    numb += b

                    e = isDstMethodsExistsInFIMMerge(gaHash,versionpair,v1,dstMethods)
                    nume += e
                    
                else:
                    # v1 没有找到的，去隔壁版本找
                    c = isDstMethodsExistsInOtherUsage(gaHash,dstMethods)
                    # 隔壁版本有的，merge有没有
                    numc += c
                    if c == 1:
                        d = isDstMethodsExistsInFIMMerge(gaHash,versionpair,v1,dstMethods)
                        numd += d
    print("total api mapping: %d" % s)
    print("usage exist in v1: %d" % numa)
    print("usage exist in v1 FIM: %d" % numb)
    print("\tusage exist in v1 and merged: %d" % nume)
    print("usage not exist in v1: %d" % (s- numa))
    print("\tusage exist in other version: %d" % numc)
    print("\t\tusage exist in merged: %d" % numd)
    print("\tusage not exist in other version: %d" % (s- numa-numc))
    print("ga num: %d" % len(result))
    # with open(Common.DELETED_METHOD_GROUND_TRUTH_FILTERED % '1-28','w') as f:
    #     json.dump(result,f,indent=4)


readUsageFIMAndFIMMerge()



# total api mapping: 339
# usage exist in v1: 101
#         usage exist in v1 and merged: 45
# usage not exist in v1: 238
#         usage exist in other version: 103
#                 usage exist in merged: 28
#         usage not exist in other version: 135
# ga num: 13

# for api mapping 
    # lookup v0 usage + frequency
    # loopup v1 usage + frequency


def exportSourceCodeUsage():
    with open(Common.DELETED_METHOD_GROUND_TRUTH_FILTERED % '1-28','r') as f:
        gt = json.load(f)
    result = {}
    for gaHash in gt:
        for versionpair in gt[gaHash]:
            data = versionpair.split('__fdse__')
            v0 = data[0]
            v1 = data[1]
            for entry in gt[gaHash][versionpair]:
                idd = entry['id']
                srcMethod = entry['src']
                srcMethods = []
                srcMethods.append(srcMethod.split('__fdse__')[-1])
                dstMethods = entry['dst']
                matchedMethods(gaHash,versionpair,v0,srcMethods,idd)
                matchedMethods(gaHash,versionpair,v1,dstMethods,idd)
                
# exportSourceCodeUsage()
