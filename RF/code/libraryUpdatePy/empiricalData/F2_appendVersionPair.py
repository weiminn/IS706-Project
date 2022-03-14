from empiricalData import Common
import json

def appendVersionPair(result):
    key = 'com.google.guava__fdse__guava__fdse__a1e0af'
    if key not in result:
        result[key] = []
    result[key].append(('13.0.1','18.0'))
    key = 'org.apache.lucene__fdse__lucene-core__fdse__b441e2'
    if key not in result:
        result[key] = []
    result[key].append(('2.9.3','3.5.0'))
    key = 'org.jsoup__fdse__jsoup__fdse__a363ec'
    if key not in result:
        result[key] = []
    result[key].append(('1.7.2','1.13.1'))
    key = 'org.elasticsearch__fdse__elasticsearch__fdse__29148e'
    if key not in result:
        result[key] = []
    result[key].append(('0.20.6','1.2.1')) # 
    result[key].append(('1.5.1','2.0.0'))
    result[key].append(('2.4.3','5.1.1'))
    result[key].append(('0.20.6','5.1.1'))
    key = 'redis.clients__fdse__jedis__fdse__8ce424'
    if key not in result:
        result[key] = []
    result[key].append(('2.2.1','3.3.0'))
    

def appendVersionPairFromJson(result):
    with open(Common.MANUALLY_SELECTED_V_PAIR,'r') as f:
        j = json.load(f)
    for gaHash in j:
        for versionPair in j[gaHash]:
            v0 = versionPair[0]
            v1 = versionPair[1]
            if not gaHash in result:
                result[gaHash] = []
            result[gaHash].append((v0,v1))
