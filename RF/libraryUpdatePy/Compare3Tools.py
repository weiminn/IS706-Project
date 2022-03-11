import os
import json

with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/compare-gt/deleted_result-4-22.json','r') as f:
    gt = json.load(f)

class CompareHistory(object):

    def matchTypeMethod(self,v0,va0,v1,va1):
        if v0 == va0 and v1 == va1:
            # print('1       %s %s %s %s' %(v0,va0,v1,va1))
            return 1
        if v0 == va0:
            # print('2       %s %s %s %s' %(v0,va0,v1,va1))
            return 2
        return 3

    def matchCode(self,srcDict,dstDict):
        dstEntry = []
        for key3,value3 in dstDict.items():
            deleted_method_data = re.split(r'[.()]',key3)
            smallMapping = {}
            smallMapping['migrated_method_data'] = []
            for mMethod in value3:
                migrated_method_data = re.split(r'[.()]',mMethod)
                smallMapping['migrated_method_data'].append(migrated_method_data[-3])
            smallMapping['deleted_method_data'] = deleted_method_data[-3]
            smallMapping['src'] = key3
            smallMapping['dst'] = value3
            dstEntry.append(smallMapping)

        matchedResults = []
        for fileName in srcDict:
            changed_codes = srcDict[fileName]
            for deleted_str in changed_codes["deleted"]:
                for entry in dstEntry:
                    if not entry['deleted_method_data'] in deleted_str:
                        continue
                    for added_str in changed_codes["added"]:
                        flag = False
                        for m1 in entry['migrated_method_data']:
                            if m1 in added_str:
                                flag = True
                                break
                        if flag:
                            pack={
                                "method_change_src":entry['src'],
                                "method_change_dst":entry['dst'],
                                "deleted_method":entry['deleted_method_data'],
                                "added_method":entry['migrated_method_data'],
                                "deleted_line":deleted_str,
                                "added_line":added_str,
                                "changed_file_name": fileName
                                # "ga_code_change":srcDict
                            }
                            matchedResults.append(pack)
        return matchedResults

    def run(self):
        rootResult1800 = '/home/hadoop/dfs/data/Workspace/ws/result-4-16'
        files = os.listdir(rootResult1800)
        for file in files:
            if os.path.getsize(savePath+result) == 0:
                continue
        with open("/home/hadoop/dfs/data/Workspace/ws/finalResult-4-16.json") as project_ga_changes_file:
            ga_code_changes = json.load(project_ga_changes_file)
        api_changes = gt
        results=[]
        cnt = 0
        for projectName in ga_code_changes:
            projectData = ga_code_changes[projectName]
            for commitData in projectData:
                # 每一个commit
                libChangeList = commitData['libChangeList']
                changedCodes = commitData['changedCodes']
                commitGADict = {}
                for libChange in libChangeList:
                    # 每一个lib
                    artifactId = libChange['artifactId']
                    groupId = libChange['groupId']
                    version1 = libChange['version1']
                    version2 = libChange['version2']
                    commitGADict[groupId +'__fdse__'+ artifactId] =  (version1,version2)
                isHaveGAs = {}
                for ga in commitGADict:
                    isHave = False
                    gah = None
                    for key in api_changes:
                        if key.startswith(ga):
                            gah = key
                            isHave = True
                            break
                    if isHave:
                        isHaveGAs[ga] = gah
                if len(isHaveGAs) == 0:
                    continue
                for ga in isHaveGAs:
                    gah = isHaveGAs[ga]
                    gtData = api_changes[gah]
                    ga_ver1 = commitGADict[ga][0]
                    ga_ver2 = commitGADict[ga][1]
                    for vPair,value2 in gtData.items():
                        vers_pair=vPair.split('__fdse__')
                        matchType = matchTypeMethod(vers_pair[0],ga_ver1,vers_pair[1],ga_ver2)
                        tmpRes = matchCode(changedCodes,value2)
                        if tmpRes != None and len(tmpRes) !=0:
                            for it in tmpRes:
                                it['match_version_type'] = matchType
                                it['ga_change_cnt'] = cnt
                                it['version_pair'] = vPair
                                it['ga'] = gah
                                it['project'] = projectName
                                it['commit'] = commitData['currCommitId']
                                it['parent_commit'] = commitData['parentCommitId']
                                if matchType == 1 or matchType == 2:
                                    it['match_version'] = vers_pair[0]
                                results.append(it)
                            print("update:%d" %(len(results)))
            cnt +=1
        print(len(results))
        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/verification/results-4-17.json','w') as f:
            json.dump(results,f,indent=4)


    def matchType123(self):
        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/verification/results-4-17.json','r') as f:
            j = json.load(f)
        result = {}
        for i in j:
            t = i['match_version_type']
            if t not in result:
                result[t] = []
            result[t].append(i)
                # key = i['method_change_src'] +"__fdse__"+ i['version_pair']
                # result1.add(key)
        print(result.keys())
        for key in result.keys():
            if key == 1:
                v = 'v0-v1'
            if key == 2:
                v = 'v0'
            if key == 3:
                v = 'code'
            with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/verification/results-4-17-%s.json' % v,'w') as f:
                json.dump(result[key],f,indent=4)


    def statistic(self):
        # with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/verification/results-4-7-v0-v1.json','r') as f:
        #     j = json.load(f)
        #     result = set()   
        #     print(len(j)) 
        #     for i in j:
        #         key = i['method_change_src'] +"__fdse__"+ i['version_pair']
        #         result.add(key)
        #     print(len(result))
        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/verification/results-4-7-v0.json','r') as f:
            j = json.load(f)
            result = set()    
            print(len(j))
            for i in j:
                key = i['method_change_src'] +"__fdse__"+ i['version_pair']
                result.add(key)
            print(len(result))
            #print(result)

        with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/verification/results-4-7-code.json','r') as f:
            j = json.load(f)
            result = set()    
            print(len(j))
            for i in j:
                key = i['method_change_src'] +"__fdse__"+ i['version_pair']
                result.add(key)
            print(len(result))

# run()

# matchType123()

# statistic()


class CompareAura(object):

    def __init__(self):
        output = '/home/hadoop/dfs/data/Workspace/LibraryUpdate-plh/aura_result'
        path ='/home/hadoop/dfs/data/Workspace/LibraryUpdate-plh/matchResult.py'



class CompareRefDiff(object):

    def __init__(self):
        total = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/ciatool/libraryUpdatePy/compare/total-refactor.json'