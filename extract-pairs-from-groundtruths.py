import json
from csv import writer
import os

try:
    os.remove("pairs.csv")
    os.remove("libraries.csv")
    os.remove("pomFile")
except:
    print("Files not found")

f = open('groundtruths.json')
 
data = json.load(f)['Y']

pairs = []
 
# print(data)
print(len(data))

count = 0

libversions = []


with open('pairs.csv', 'a', newline='') as f_object: 
    writer_object = writer(f_object)

    for lib in data:
        
        lsplit = lib.split("__XX__")

        for ver in data[lib]:
            vsplit = ver.split("__XX__")

            libversions.append(lib + " __XX__" + vsplit[1])

            for miss in data[lib][ver]:

                if data[lib][ver][miss]["n_to_n"] == '1 to 1':

                    split = miss.split("__XX__")

                    writer_object.writerow([lsplit[0], lsplit[1], vsplit[0], vsplit[1], split[0], split[1], data[lib][ver][miss]["repl_method"][0]]) 
        
                    count = count + 1     


    f_object.close()

# Closing file
f.close()


with open('libraries.csv', 'a', newline='') as f_object: 
        
    writer_object = writer(f_object)

    for lib in libversions:

        writer_object.writerow(lib.split("__XX__")) 

        lSplit = lib.split("__XX__")

    f_object.close()