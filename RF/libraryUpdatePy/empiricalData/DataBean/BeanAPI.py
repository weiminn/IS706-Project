import json
# from jsonobject import *

class BeanAPI():


    def __init__(self, name):
        self.api = name
        # modified, deleted, added
        self.changeType = ""
    
    def setChangeType(self,changeType):
        self.changeType = changeType

    def getChangeType(self):
        return self.changeType

    def getAPIName(self):
        return self.api
    
    def  __str__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr
    
    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr

    # def default(self, obj):
    #     if isinstance(obj, bool):
    #         return 1 if obj else 0
    #     return super().default(obj)

    # def default(self, o):
    #     if isinstance(o, BeanAPI):
    #         return o.__dict__
    #     else:
    #         return json.JSONEncoder.default(self, o)
        # if isinstance(obj, BeanAPI):
        #     return {"api":"a","b":"b"}

        # # if isinstance(obj, (Node, JoinCriteria)):
        # #     keys = [key for key in obj.__dict__.keys() if
        # #             key[0] != '_' and key not in ('line', 'pos')]
        # #     ret = {key: getattr(obj, key) for key in keys if getattr(obj, key)}
        # #     return ret

        # # if isinstance(obj, QualifiedName):
        # #     return obj.parts

        # return JSONEncoder.default(self, obj) 
