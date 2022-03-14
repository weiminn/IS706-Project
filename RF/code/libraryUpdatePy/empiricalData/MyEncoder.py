import json
from empiricalData.DataBean.BeanAPI import BeanAPI
from empiricalData.DataBean.BeanAPISeq import BeanAPISeq
from typing import List, Tuple, Dict, Set
from empiricalData.MetricResult import MethodMetric,MetricResult
from empiricalData.DataBean.RankedDependencyUsage import GAVUsage
from ToolMappingLogic import ToolMappingLogic
from ExcelRow import RowData
from ExcelRow import TableIICell
class MyEncoder(json.JSONEncoder):

    def default(self, o):

        if isinstance(o, BeanAPISeq):
            return o.__dict__
        elif isinstance(o,BeanAPI):
            return o.__dict__
        elif isinstance(o,List):
            res = []
            for item in o:
                s = self.default(item)
                res.append(s)
            return res
        elif isinstance(o,Dict):
            res = {}
            for item in o.items():
                key = item[0]
                value = item[1]
                s = self.default(value)
                res[key] = s
            return res
        elif isinstance(o,MetricResult):
            return o.__dict__
        elif isinstance(o,MethodMetric):
            return o.__dict__
        elif isinstance(o, GAVUsage):
            return o.__dict__
        elif isinstance(o, ToolMappingLogic):
            return o.__dict__
        elif isinstance(o,RowData):
            return o.__dict__
        elif isinstance(o,TableIICell):
            return o.__dict__
        else:
            print(type(o))
            return super.default(o)



# result2 = {}
# result = {}

# a = BeanAPISeq("aaa")
# b = BeanAPI("api name")
# a.getBeanAPIList().append(b)
# li = []
# li.append(a)
# s = MyEncoder(indent=4)
# result['aa'] = li
# result2['bbb'] = result
# ss = s.encode(result2)
# print(ss)