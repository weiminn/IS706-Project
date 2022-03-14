import requests
import sys
import os
import time
from bs4 import BeautifulSoup
import time

def errorFile(gav):
    with open('404gav.log','a') as f:
        f.write(gav)
        f.write('\n')

def readHtml(content,v,isVersionDateOrList):
    soup = BeautifulSoup(content,'lxml')
    divContent = soup.find('div',attrs={'class':'gridcontainer'})
    tbody = divContent.find_all('tbody')
    tmpDict = {}
    tmpVersionDateList = []
    for microv in tbody:
        minorv = microv.children
        for child in minorv:
            children2 = child.children
            cnt = 0
            version = None
            tmpList = []
            for child2 in children2:
                tmpList.append(child2)
            date = tmpList[-1].text
            version = None
            if len(tmpList) == 5:
                version = tmpList[1].text
            elif len(tmpList) == 4:  
                version = tmpList[0].text
            if version == None:
                continue
            tmpDict[version] = date
            tmpVersionDateList.append((version,date))
    # print(tmpDict)
    if isVersionDateOrList:
        if v in tmpDict:
            return tmpDict[v]
        return None
    else:
        return tmpVersionDateList
        

def readFromHtml(subDir, version):
    with open(subDir +'/' + 'time.html','r') as f:
        content = f.read()
        date = readHtml(content,version,True)
        return date

def getJarReleaseTime(groupId,artifactId,version,subDir):
    if os.path.exists(subDir +'/' + 'time.html') :
        date = readFromHtml(subDir,version)
        return date
    try:
        requests.adapters.DEFAULT_RETRIES = 3
        print('https://mvnrepository.com/artifact/'+groupId+'/'+artifactId)
        req2 = requests.get('https://mvnrepository.com/artifact/'+groupId+'/'+artifactId)
        if req2.status_code == 200:
            print('200 mvn page')
            print(subDir)
            with open(subDir +'/time.html','wb') as f:
                f.write(req2.content)
            date = readFromHtml(subDir,version)
            return date
    except Exception as e:
        print('404 ')
        print(e)
        errorFile('404 ')
    return None

def getVersionDate(content,version):
    res = readHtml(content,version,True)
    return res

def getTop3GA(content):
    soup = BeautifulSoup(content,'lxml')
    divContent = soup.find_all('div',attrs={'class':'im'})
    cnt = 0
    result = []
    for item in divContent:
        if cnt == 3:
            break
        subt = item.find_all('p',attrs={'class':'im-subtitle'})
        subt0 = subt[0]
        a = subt0.find_all('a')
        groupId = a[0].text
        artifactId = a[1].text
        result.append((groupId,artifactId))
        cnt +=1
    return result

def getNearestVersion(content,versionDate):
    monthall = ['jan','feb','mar','apr','may','jun','jul','aug','seq','oct','nov','dec']
    tt = versionDate.split(',')
    year = int(tt[-1].strip(' '))
    month =  tt[0].lower()
    indexMonth = 0
    for i in range(0,len(monthall)):
        if month == monthall[i]:
            indexMonth = i
            break

    dateList =  readHtml(content,"null",False)
    timeMap = {}
    print(dateList)
    for dateEntry in dateList:
        version = dateEntry[0]
        date = dateEntry[1]
        tt2 = date.split(',')
        year2 = int(tt2[-1].strip(' '))
        month2 = date[0]
        indexMonth2 = 0
        for i in range(0,len(monthall)):
            if month2 == monthall[i]:
                indexMonth2 = i
                break
        if (year2 == year and indexMonth2 <= indexMonth) :
            timeMap[version] = 12*(year - year2) + indexMonth - indexMonth2
        elif year2 < year:
            if indexMonth2 <= indexMonth:
                gap = 12*(year - year2) + indexMonth - indexMonth2
            elif indexMonth2 > indexMonth:
                gap = 12*(year - year2) - (indexMonth2 - indexMonth)
            timeMap[version] = gap
    minV = 100000000
    vv = None
    for version in timeMap:
        if timeMap[version] < minV:
            minV = timeMap[version]
            vv = version
    return version




def searchToken(s, tokens):
    gahashversion = s.split('__fdse__')
    url1 = 'https://mvnrepository.com/artifact/%s/%s' % (gahashversion[0],gahashversion[1])
    print(url1)
    content1 = requests.get(url1).content
    time.sleep(4)
    versionDate = getVersionDate(content1,gahashversion[3])
    print(s + ": "+ versionDate)
    data = tokens.split('__fdse__')
    res = []
    for token in data:
        url2 = 'https://mvnrepository.com/search?q=' + token
        req2 = requests.get(url2)
        time.sleep(3)
        content2 = req2.content
        top3 = getTop3GA(content2)
        for item in top3:
            url3 = 'https://mvnrepository.com/artifact/%s/%s'% (item[0],item[1])
            content3 = requests.get(url3).content
            time.sleep(3)
            versionNear = getNearestVersion(content3,versionDate)
            res.append('candidate_ga_version: %s:%s:%s'  % (item[0],item[1],versionNear))
    return res

def run():
    javaDoc = False
    jarReleaseTime = False
    isPOM = False
    # s = 'redis.clients__fdse__jedis__fdse__8ce424__fdse__2.8.1'
    # jarReleaseTime = True
    isSearch = False
    s = sys.argv[1]
    if len(sys.argv) >= 3:
        s2 = sys.argv[2]
        if s2 == 'javadoc':
            javaDoc = True
        if s2 == 'time':
            jarReleaseTime = True
        if s2 == 'pom':
            isPOM = True
        if s2 == 'search':
            isSearch = True

    if isSearch:
        tokens = sys.argv[3]
        res = searchToken(s, tokens)
        for s in res:
            print(res)
        return

    data = s.split("__fdse__")
    groupId = data[0]
    artifactId = data[1]
    hashCode = data[2]
    version = data[3]
    # groupId = sys.argv[1]
    # artifactId = sys.argv[2]
    # version = sys.argv[3]
    m_data = {
        "groupId": groupId,
        "artifactId":artifactId,
        "version" : version
    }
    subDir = groupId + "__fdse__" + artifactId + "__fdse__" + hashCode
    if not os.path.exists('./output/jar/' + subDir ):
        os.mkdir('./output/jar/' + subDir)
    if jarReleaseTime:
        date = getJarReleaseTime(groupId,artifactId,version,'./output/jar/' + subDir)
        if date == None:
            date = "null"
        print('time: '+ date)
        return
    # req = requests.post('http://10.176.34.86:13333/API/QueryGAV',data=m_data)

    # if req.status_code == 200:
    #     print('200')
    #     with open('./output/jar/' + subDir +'/' + artifactId + "-"+ version +'.jar','wb') as f:
    #         f.write(req.content)
    #     return


    groupIdU = groupId.replace('.','/')
    try:
        requests.adapters.DEFAULT_RETRIES = 3
        if javaDoc:
            fileName = artifactId+'-'+version+ '-javadoc.jar'
        elif isPOM:
            fileName = artifactId+'-'+version+ '.pom'
        else:
            fileName =  artifactId+'-'+version+ '.jar'
        print('https://repo1.maven.org/maven2/'+groupIdU+'/'+artifactId+'/'+version+'/'+ fileName)
        req2 = requests.get('https://repo1.maven.org/maven2/'+groupIdU+'/'+artifactId+'/'+version+'/'+ fileName)
        if req2.status_code == 200:
            print('200')
            with open('./output/jar/' + subDir +'/'+ fileName,'wb') as f:
                f.write(req2.content)
            return
    except Exception as e:
        print('404 '+ s)
        errorFile('404 '+ s)
    
    errorFile('404 '+ s)


run()