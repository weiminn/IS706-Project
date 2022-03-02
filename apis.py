import os
import subprocess
import json

os.chdir('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\_libs')
try:
    os.remove("apis.json")
except:
    print("Files not found")


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
        _r_split = list(filter(lambda x: ';' in x, r_split))
        _r_split_ = [x.strip(' ') for x in _r_split]

        a = []

        path = _c.split('/')
        # path.pop(len(path)-1)
        path = '.'.join(path) + '.'

        for m in _r_split_:
            m_split = m.split(' ')
            if 'abstract' not in m:
                if '(' not in m_split[1]: #not a constructor
                    if '(' in m: # is a method
                        m_split.pop(0)
                        if 'static' in m and 'final' in m: #is final static
                            a.append([m_split[2], path + ' '.join(m_split[3:])])
                        elif 'final' in m:
                            a.append([m_split[1], path + ' '.join(m_split[2:])])
                        elif 'static' in m:
                            a.append([m_split[1], path + ' '.join(m_split[2:])])
                        else:
                            a.append([m_split[0], path + ' '.join(m_split[1:])])
                else:
                    ret = m_split[1].split('(')[0]
                    m_split.pop(0)
                    a.append([ret, ' '.join(m_split[1:])])
            
        apis[f].extend(a)
        print(cnt, "/", len(_classes) , ": Extracted ", len(a), " methods")
        if len(a) == 0:
            print("Nothing extracted!") #pause

        cnt = cnt + 1

apis = json.dumps(apis)

with open('apis.json', 'a', newline='') as f_object: 
        
    f_object.write(apis)

    f_object.close()