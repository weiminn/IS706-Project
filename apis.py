import os
import subprocess
import json
import datetime

os.chdir('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\extracted')
extracted = os.listdir()

os.chdir('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\libs')
files = os.listdir()

filt = list(filter(lambda x: '.jar' == x[-4:], files)) #select only jar files
filt = list(filter(lambda x: x + '.json' not in extracted, filt)) #filter all already-extracted jars

start = datetime.datetime.now()
print("Start time:", start)
fcnt = 0
for f in filt:

    fcnt = fcnt + 1

    apis = {}
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
        _r_split2 = [x[:-1] for x in _r_split_]

        a = []

        path = _c.split('/')
        path = '.'.join(path) + '.'

        for m in _r_split2:
            m_split = m.split(' ')

            if ' throws ' in m: #remove throw phrase
                m_split = m_split[0: m_split.index('throws')]
            if 'abstract' not in m:
                if '(' not in m_split[1]: #not a constructor
                    if '(' in m: # is a method
                        if '<' in m: #has angle brackets for generics
                            a_pos = 0
                            for i in range(len(m_split)):
                                if '<' in m_split[i]:
                                    break
                                a_pos = a_pos + 1
                            b_pos = 0
                            for i in range(len(m_split)):
                                if '(' in m_split[i]:
                                    break
                                b_pos = b_pos + 1
                            
                            if a_pos < b_pos: #if the angle brackets are before method name
                                if b_pos - a_pos > 1: #if the generic defines the return types and arguments
                                #     a.append([' '.join(m_split[a_pos:b_pos]), path + ' '.join(m_split[b_pos:])])
                                # else: #if angle brackets are only in return type
                                    a.append([' '.join(m_split[a_pos:b_pos]), path + ' '.join(m_split[b_pos:])])

                                    #todo: handle generics before return type

                            else: #if the angle brackets are in parameter only
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
                            #just take the first element as return and the others as the method 
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
                    a.append([m_split[1].split('(')[0], ' '.join(m_split[1:])])

            
        apis[f].extend(a)
        print(f, ":", fcnt, "/", len(filt) , ":", cnt, "/", len(_classes) , ": Extracted ", len(a), " methods from ", path)

        cnt = cnt + 1

    apis = json.dumps(apis)

    # with open(str(time.time()) + '.json', 'a', newline='') as f_object: 
    with open(f + '.json', 'a', newline='') as f_object: 
            
        f_object.write(apis)

        f_object.close()

    os.rename('G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\libs\\' + f + '.json', 'G:\My Drive\Term 4.2\IS706 - Software Mining and Analysis\Project\extracted\\' + f + '.json')

end = datetime.datetime.now()
print("Start time:", start)
print("End time:", end)
print("Elapsed time:", ((end - start).total_seconds()) / 60, "minutes")
print(fcnt, "files processed")