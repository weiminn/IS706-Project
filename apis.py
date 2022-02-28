import os
import subprocess
import json

try:
    os.remove("apis.json")
except:
    print("Files not found")


os.chdir('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\_libs')
files = os.listdir()
apis = {}

for f in files:
    print("Extracting: " + f)
    apis[f] = []
    returned_output = subprocess.check_output("jar -tf "  + f)
    o_split = str(returned_output).split('\\r\\n')

    classes = list(filter(lambda x: '.class' in x, o_split))
    print(len(classes), " classes found in ", f)
    _classes = []

    for c in classes:
        _classes.append(c[:-6])

    cnt = 1
    for _c in _classes:
        s = "javap -public -cp " + f + " " + _c

        returned_methods = subprocess.check_output(s)
        r_split = str(returned_methods).split('\\r\\n')
        # compiledFrom = r_split.pop(0)
        # classTitle = r_split.pop(0)
        # close = r_split.pop(len(r_split) - 1)
        # close2 = r_split.pop(len(r_split) - 2)
    
        apis[f].extend(r_split)
        print(cnt, "/", len(_classes) , ": Extracted ", len(r_split), " methods")
        cnt = cnt + 1

apis = json.dump(apis)

with open('apis.json', 'a', newline='') as f_object: 
        
    f_object.write(apis)

    f_object.close()