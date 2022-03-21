import os
import json
import datetime
import csv
from csv import writer
import random
import numpy
from Levenshtein import *

try:
    os.remove("G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\\dataset-cnn\\raw\\training.csv")
except:
    print("File not found")
try:
    os.remove("G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\\dataset-cnn\\raw\\validation.csv")
except:
    print("File not found")
try:
    os.remove("G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\\dataset-cnn\\cleaned\\training.csv")
except:
    print("File not found")
try:
    os.remove("G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\\dataset-cnn\\cleaned\\validation.csv")
except:
    print("File not found")

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
    # posPair = p[5] + "__XX__" + p[6]
    
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
            
            can_pair = [p[6], can[1][: can[1].index('(') + 1] + ','.join(e_cargList) + ')']
            negative_pair_to_append.append(can_pair)



    #random sample of 
    if found:
        negative_pair_to_append.pop(positive_position)

    
    if not found:
        print("Found no positive datapoint!")
    else:
        posPair = [p[5], p[6]]
        pos_pairs.append('__XX__'.join(posPair))

        #rank negative pairs by levenshtein distance
        dist = []
        for np in negative_pair_to_append:
            dist.append([np[1], distance(np[1], posPair[1])])

        sortedDist = sorted(dist, key=lambda npd: npd[1])

        for i in range(max(int(len(sortedDist)/3000), 1)):
            neg_pairs.append(posPair[0] + "__XX__" + sortedDist[i][0])

    pcnt = pcnt + 1

training_positives = []
validation_positives = []

training_negatives = []
validation_negatives = []

divide = 1/10

for i in range(0, int(len(neg_pairs)*divide)):
    validation_negatives.append(neg_pairs.pop(random.randrange(0, len(neg_pairs))))
training_negatives = neg_pairs

for i in range(0, int(len(pos_pairs)*divide)):
    validation_positives.append(pos_pairs.pop(random.randrange(0, len(pos_pairs))))
training_positives = numpy.random.choice(pos_pairs, len(training_negatives))

with open('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\\dataset-cnn\\raw\\training.csv', 'a', newline='') as f_object: 
        
    writer_object = writer(f_object, delimiter =";")
        
    for pair in training_positives:

        writer_object.writerow([1, pair]) 
        
    for pair in training_negatives:

        writer_object.writerow([0, pair]) 

    f_object.close()

with open('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\\dataset-cnn\\raw\\validation.csv', 'a', newline='') as f_object: 
        
    writer_object = writer(f_object, delimiter =";")
        
    for pair in validation_positives:

        writer_object.writerow([1, pair]) 
        
    for pair in validation_negatives:

        writer_object.writerow([0, pair]) 

    f_object.close()

with open('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\\dataset-cnn\\raw\\training.csv', 'r') as f, open('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\\dataset-cnn\\cleaned\\training.csv', 'w') as fo:
    for line in f:
        fo.write(line.replace('"', '').replace("'", ""))

with open('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\\dataset-cnn\\raw\\validation.csv', 'r') as f, open('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\\dataset-cnn\\cleaned\\validation.csv', 'w') as fo:
    for line in f:
        fo.write(line.replace('"', '').replace("'", ""))

end = datetime.datetime.now()
print("Start time:", start)
print("End time:", end)
print("Elapsed time:", ((end - start).total_seconds()) / 60, "minutes")
print(pcnt, "Pairs processed")
print(notfound, "Replacements not found!")