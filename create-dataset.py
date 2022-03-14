import os
import json
import datetime
import csv
from csv import writer
import random

os.chdir('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project')
with open('pairs.csv', newline='') as csvfile:
    raw_pos_pairs = list(csv.reader(csvfile))

os.chdir('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\_extracted')
extracted = os.listdir()
filt = list(filter(lambda x: x[1] + '-' + x[3] + '.jar.json' in extracted, raw_pos_pairs)) #select all json files

start = datetime.datetime.now()
print("Start time:", start)

notfound = 0
pcnt = 0

pos_pairs = []
neg_pairs = []

for p in filt:
    name = p[1] + '-' + p[3] + '.jar.json'
    namepath = 'G:\\My Drive\\Term 4.2\\IS706 - Software Mining and Analysis\\Project\\_extracted\\' + name

    print(pcnt, '/', len(raw_pos_pairs), "Processing:", name)
    print("Searching:", p[6])
    posPair = p[5] + "__XX__" + p[6]
    pos_pairs.append(posPair)
    
    f = open(namepath)
    loaded = json.load(f)
    # allcandidates = list(filter(lambda x: x[0] == p[4], loaded[name[:-5]])) #filter candidates with the same return type
    allcandidates = list(filter(lambda x: x[0] == x[0], loaded[name[:-5]]))

    #for this file
    negative_pair_to_append = []

    #find out the positive pair
    positive_position = 0
    found = False
    if '(' not in p[6]:
        print("Replacement", p[6], "is not method!!!")
        notfound = 1 + notfound
    else:
        for can in allcandidates:
            
            e_cargList = []

            #check if positive candidate
            if can[1][: can[1].index('(')] == p[6][: p[6].index('(')]:

                #extract args from candidate
                cargs = can[1][can[1].index('(') + 1: can[1].index(')')]
                cargList = cargs.split(',')
                cargList = [x.strip(' ') for x in cargList]
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
                    print("Found out positive datapoint:", p[6])
            
            if not found:
                positive_position = positive_position + 1
            
            can_pair = p[6] + "__XX__" +  can[1][: can[1].index('(') + 1] + ','.join(e_cargList) + ')'
            negative_pair_to_append.append(can_pair)


    #random sample of 
    if found:
        negative_pair_to_append.pop(positive_position)
    
    sample = random.sample(negative_pair_to_append, int(len(negative_pair_to_append)/10))

    neg_pairs.extend(sample)
    
    f.close()

    if not found:
        print("Found no positive datapoint!")

    pcnt = pcnt + 1

with open('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\\dataset\\positive.txt', 'a', newline='') as f_object: 
        
    writer_object = writer(f_object)
        
    for pair in pos_pairs:

        writer_object.writerow([pair]) 

    f_object.close()

with open('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\\dataset\\negative.txt', 'a', newline='') as f_object: 
        
    writer_object = writer(f_object)

    for pair in neg_pairs:

        writer_object.writerow([pair]) 

    f_object.close()

end = datetime.datetime.now()
print("Start time:", start)
print("End time:", end)
print("Elapsed time:", ((end - start).total_seconds()) / 60, "minutes")
print(pcnt, "Pairs processed")
print(notfound, "Replacements not found!")