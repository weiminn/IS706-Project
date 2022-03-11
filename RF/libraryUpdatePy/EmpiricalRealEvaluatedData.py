import os
import json
from empiricalData.E_genDB import genDB
from empiricalData.E_genDB import topUsageSelection2
from empiricalData.E_genDB import topUsagePairSelection
from packaging import version
import Common
from empiricalData.MyEncoder import MyEncoder
def projectNumLibNum():
    # p85 = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/projects_extra/85_3000/repository'
    # p = '/home/hadoop/dfs/data/Workspace/projects_9_19/projects_git'
    # pSet = set()
    # fs = os.listdir(p)
    # fs2 = os.listdir(p85)
    # for f in fs:
    #     pSet.add(f)
    # for f in fs2:
    #     pSet.add(f.replace('@','__fdse__'))
    # print( 'project all: %d' % len(pSet))
    print('project all: 4712')
    path = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-data/dep-db-21-1-20.json'
    with open(path,'r') as f:
        j = json.load(f)
    projectSet = set()
    itemSet = set()
    fim = {}
    fimVersion = {}
    GAV = set()
    nullLib = 0
    for proj in j:
        if '@' in proj:
            projectSet.add(proj.replace('@','__fdse__'))
        else:
            projectSet.add(proj)

        if len(j[proj]) == 0:
            nullLib +=1
        for item in j[proj]:
            GAV.add(item)
            index = item.rfind('__fdse__')
            itemSet.add(item[0:index])
            if item[0:index] not in fim:
                fim[item[0:index]] = 0
            if item[0:index] not in fimVersion:
                fimVersion[item[0:index]] = set()
            fimVersion[item[0:index]].add(item[index:])
            fim[item[0:index]] +=1
    itemList = list(itemSet)
    print('project: %d'% len(projectSet))
    print('GA sum: %d' % len(fim))
    # project: 5575
    # GA sum: 11419
    # GAV: 31393
    print('null lib project: %d' % nullLib)
    print('project have lib: %d' % (4712-nullLib))
    print('GAV: %d' % len(GAV))

# projectNumLibNum()

# SELECT PROJECT
# 原始收集的项目 4712
#      null lib project 2145
#      project have lib 2567
#                   ga 11419
#                   gav 31393

# SELECT TOP 200 考虑API Usage
# GA 11419
#       无 Usage的lib 11419-4586
#       有 usage的lib 4586
#           version<=1:3078
#           version>1 1508
#               top200 
#               select 85 major, 771 minor, 1048 patch

# SELECT LIB 考虑API Usage
# GA 11419
#      无 Usage 11419-4586
#      有 usage 4586
#      usage<10 4586-999
#      usage>10 lib = 999
#       version<=1: 999-230
#       version >1: 230



# SELECT VERSION PAIR:
# 230 Lib, 771(major: x, minor x, patch) version pair + Usage  -> Diff Jar
#   major: 182
#   minor: 320
#   patch: 149
#   无major: 114
#   相同major，minor，patch，但是后面还有后缀 6 （4.12-beta-2', '4.12'）
#
# 37 Lib, 99 version pair, 738 API




def selection():
    depDb,usageDb = genDB()
    GAVersionAndAPICount,COUNTALL = topUsageSelection2(depDb,usageDb)
    print('过滤的usage<=10的情况 %d' % len(GAVersionAndAPICount))
    
    topNiGAVersionPair:Dict[str,List[Tuple[str,str]]] = topUsagePairSelection(GAVersionAndAPICount)
    return
    date = '21-4-19-all'
    filePath = Common.RANKEDGAVPair % date
    with open(filePath, 'w') as f:
        encoder = MyEncoder(indent=4)
        s = encoder.encode(topNiGAVersionPair)
        f.write(s)

    print('ga leng: %d' % len(topNiGAVersionPair))
    vPairLength = 0
    res = [0,0,0,0,0,0]
    majorMinorPath = {}
    for key in topNiGAVersionPair:
        # vPairLength += len(topNiGAVersionPair[key])
        for gaptype in topNiGAVersionPair[key]:
            if gaptype not in majorMinorPath:
                majorMinorPath[gaptype] = 0
            majorMinorPath[gaptype] += len(topNiGAVersionPair[key][gaptype])
        # for verPair in topNiGAVersionPair[key]:
        #     v0 = verPair[0]
        #     v1 = verPair[1]
        #     vp0 = version.parse(v0)
        #     vp1 = version.parse(v1)
        #     if (not hasattr(vp0, 'major')) or (not hasattr(vp1, 'major')):
        #         res[3] +=1
            #     continue
            # if vp0.major != vp1.major:
            #     res[0] +=1
            #     continue
            # if (not hasattr(vp0, 'minor')) or (not hasattr(vp1, 'minor')):
            #     res[4] +=1
            #     continue
            # if vp0.minor != vp1.minor:
            #     res[1] +=1
            #     continue
            # if vp0.micro != vp1.micro:
            #     res[2] +=1
            #     continue
            # res[5] +=1
    print('vpair length: %d' % vPairLength)
    print(res)
    print(majorMinorPath)
    # top selection raw: 4586
    # top remove gav usage<=1: 230
    # ga leng: 230
    # vpair length: 771

selection()
