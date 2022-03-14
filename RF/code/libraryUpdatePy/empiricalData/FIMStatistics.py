from typing import List, Tuple, Dict


#                            ga     version   key
def fimStatistics(FIM:Dict[str,Dict[str,Dict[str,List[List[str]]]]]):
    cnt = 0
    for gaHash in FIM:
        for version in FIM[gaHash]:
            cnt += len(FIM[gaHash][version]['FIM_fre'])
            # [
                # {
                #     "usage_seq": [
                #         "com.google.protobuf.UnknownFieldSet__fdse__com.google.protobuf.UnknownFieldSet.Builder.build()"
                #     ],
                #     "frequency": 56
                # },

    print('FIM cnt: %s' % cnt)