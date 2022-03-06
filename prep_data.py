import json
from pyjarowinkler import distance
import csv
libs = open("libs.json","r")
op = json.load(libs)
lib_names = op["jedis-2.2.1.jar"]
# remove front part of the api name since every api has it
dep_api = "redis.clients.jedis.BinaryTransaction.exec".replace('redis.clients.', '', 1)
dep_ret_typ = "java.util.List"
dep_param = ""
print(lib_names[1])
print(len(lib_names))
with open('lib_data.csv', 'w', newline = '') as csvfile:
    writer = csv.writer(csvfile, delimiter = "|")
    writer.writerow(['api_name', 'ret_type', 'params', 'api_sim', 'ret_sim', 'param_sim', 'result'])
    for i in range(len(lib_names)):
        ret_type = lib_names[i][0]
        api_raw = lib_names[i][1]
        prm_type = api_raw[api_raw.find('(')+1 : api_raw.find(')')]
        api_name = api_raw.split("(")[0].replace('redis.clients.', '', 1)
        api_sim = distance.get_jaro_distance(dep_api, api_name, winkler=True, scaling = 0.2)
        ret_sim = distance.get_jaro_distance(dep_ret_typ, ret_type, winkler=True, scaling = 0.2)
        result = 1 if api_name == "redis.clients.jedis.Transaction.exec".replace('redis.clients.', '', 1) else 0
        if (dep_param == prm_type):
            param_sim = 1
        elif dep_param == "" or prm_type == "":
            param_sim = 0
        else: 
            param_sim = distance.get_jaro_distance(dep_param, prm_type, winkler=True, scaling = 0.1)
        writer.writerow([api_name, ret_type, prm_type, str(api_sim), str(ret_sim), str(param_sim), str(result)])

        



