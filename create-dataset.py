import os
import json
import datetime
import csv

os.chdir('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project')
with open('pairs.csv', newline='') as csvfile:
    pos_pairs = list(csv.reader(csvfile))

os.chdir('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\extracted')
extracted = os.listdir()

fcnt = 0
filt = list(filter(lambda x: x[1] + '-' + x[3] + '.jar.json' in extracted, pos_pairs)) #select all json files

start = datetime.datetime.now()
print("Start time:", start)

for p in filt:
    name = p[1] + '-' + p[3] + '.jar.json'
    namepath = 'G:\\My Drive\\Term 4.2\\IS706 - Software Mining and Analysis\\Project\\extracted\\' + name

    print("Processing:", name)
    posPair = p[5] + "__XX__" + p[6]
    
    f = open(namepath)
    loaded = json.load(f)
    allcandidates = list(filter(lambda x: x[0] == p[4], loaded[name[:-5]])) #filter candidates with the same return type

    found = False

    #filter out the positive pair
    for can in allcandidates:
        if can[1][: can[1].index('(')] == p[6][: p[6].index('(')]:

            #extract args from candidate
            cargs = can[1][can[1].index('(') + 1: can[1].index(')')]
            cargList = cargs.split(',')
            cargList = [x.strip(' ') for x in cargList]
            e_cargList = []
            for arg in cargList:
                e_cargList.append(arg.split('.')[len(arg.split('.'))-1])

            #extract args from groundtruth
            gargs = p[6][p[6].index('(') + 1: p[6].index(')')]
            # gargList = gargs.split(',')
            e_gargList = gargs.split(',')
            # gargList = [x.strip(' ') for x in gargList]

            #compare arguments
            if set(e_cargList) == set(e_gargList):
                found = True
                print("Filtered out positive datapoint:", p[6])

                #unable to find some matches because of generic notations

                break

    f.close()
    fcnt = fcnt + 1

    # if not found:
    #     print("Found no positive datapoint!")


end = datetime.datetime.now()
print("Start time:", start)
print("End time:", end)
print("Elapsed time:", ((end - start).total_seconds()) / 60, "minutes")
print(fcnt, "files processed")