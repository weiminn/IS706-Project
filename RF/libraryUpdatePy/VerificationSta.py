import os

import json


def loadJson(name):

    with open('/home/hadoop/dfs/data/Workspace/LibraryUpdate/verification/'+name,'r') as f:
        j = json.load(f)
    a = set()
    b = set()
    c = set()
    for item in j:
        ga = item['ga']
        a.add(ga)
        version_pair = item['version_pair']
        b.add(ga + '__fdse__'+ version_pair)
        method_change_src = item['method_change_src']
        c.add(ga + '__fdse__'+ version_pair + '__fdse__' + method_change_src)
    print('distrinct ga: %d, version pair: %d, method: %d'%(len(a),len(b),len(c)))

def run():
    loadJson('results-4-7-v0-v1.json')
    loadJson('results-4-7-v0.json')
    loadJson('results-4-7-code.json')
run()