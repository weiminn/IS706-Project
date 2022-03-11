import os

from libraryUpdatePy.empiricalData import Common
from libraryUpdatePy.empiricalData import A00_ProjectMerge


proj1,proj2 = A00_ProjectMerge.getTotalProjects()

for proj in proj1:
    sh = 'java -jar LibHarmo-jar-with-dependencies.jar /home/hadoop/dfs/data/Workspace/LibraryUpdate/output-2nd-1-27 %s' % Common.LIBDETECT_CONFIG
    projPath = Common.ROOT_PROJECT1 + proj
    cmd = sh + " " +projPath
    print(cmd)


for proj in proj2:
    sh = 'java -jar LibHarmo-jar-with-dependencies.jar /home/hadoop/dfs/data/Workspace/LibraryUpdate/output-2nd-1-27 %s' % Common.LIBDETECT_CONFIG
    projPath = Common.ROOT_PROJECT2 + proj
    cmd = sh + " " +projPath
    print(cmd)

