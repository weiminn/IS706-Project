
class MethodMetric(object):

    def __init__(self,methodName):
        self.name = methodName
    
    def setM(self,m2,m3,m4):
        self.m2 = m2
        self.m3 = m3
        self.m4 = m4



class MetricResult(object):


    def __init_(self,ga,vPair):
        self.methodMetric = []
        self.ga = ga
        self.vPair = vPair
    
    def addMethodMetric(self,o):
        self.methodMetric.append(o)

