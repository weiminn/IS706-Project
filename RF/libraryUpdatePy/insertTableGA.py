import json
import os
import requests

def run():
    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/output/table_ga.json','r') as f:
        j = json.load(f)
    RECORDS = j['RECORDS']
    cnt = 0
    for item in RECORDS:
        print(cnt)
        req = requests.post('http://localhost:9200/table/ga',json=item)
        print(req.content)
        cnt+=1

run()
