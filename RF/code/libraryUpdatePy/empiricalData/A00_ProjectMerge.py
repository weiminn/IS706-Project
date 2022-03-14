import os
from libraryUpdatePy.empiricalData import Common

def getTotalProjects():
    files1 = os.listdir(Common.ROOT_PROJECT1)
    files2 = os.listdir(Common.ROOT_PROJECT2)
    files22 = []
    for file in files2:
        tmp = file.replace('@','__fdse__')
        files22.append(tmp)

    set1 = set(files1)
    set2 = set(files22)
    newSet = []
    for i in set2:
        if i not in set1:
            newSet.append(i.replace('__fdse__','@'))
    return files1, list(newSet)



# a = set()
# for i in files1:
#     a.add(i)
# for i in files22:
#     a.add(i)

# cnt = 1
# for i in a:
#     # os.mkdir(Common.ROOT_PATH +'project1And2Jar/' + i)
#     print(str(cnt)+ '. Project: '+ i)
#     print('https://github.com/'+ i.replace('__fdse__','/'))
#     print('\n\n')
#     cnt+=1


