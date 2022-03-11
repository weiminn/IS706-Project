import json
import os
import requests
import sys

def run():
    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/output/table_ga.json','r') as f:
        j = json.load(f)
    RECORDS = j['RECORDS']
    cnt = 0
    a = ['commons','pool2']
    s1 = set(a)
    cnt = 0
    for item in RECORDS:
        groupId = item['group_id']
        artifactId = item['artifact_id']
        data = groupId.split('.')
        data2 = artifactId.split('.')
        s2 = set(data)
        for g in data2:
            s2.add(g)
        if len(s1 & s2) == len(s1):
            # print(item)
            cnt +=1
    print(cnt)

run()
