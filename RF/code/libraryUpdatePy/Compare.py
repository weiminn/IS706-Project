import json
import codecs
import sys
import csv

def json_2_csv():
    # v0-v1.json 1200
    # ID GA_CHANGE_CNT GA VPAIR METHOD_CHANGE_SRC T/F

    # v0.json 2800
    path_v0 = '/Users/pan/Desktop/results-4-7-v0'
    path_v0_v1 = '/Users/pan/Desktop/results-4-7-v0-v1'

    with open(path_v0_v1 +".json", 'r') as json_file:
        json_data_list = json.load(json_file)

    # csvfile = open(path+'.csv', 'w') # 此处这样写会导致写出来的文件会有空行
    # csvfile = open(path+'.csv', 'wb') # python2下
    csvfile = open(path_v0_v1 + '.csv', 'w', newline='')  # python3下
    writer = csv.writer(csvfile)

    writer.writerow(['ID','GA_CHANGE_CNT','GA','VPAIR','METHOD_CHANGE_SRC','T/F'])
    id = 1
    for dic in json_data_list:
        # 读取json数据的每一行，将values数据一次一行的写入csv中
        writer.writerow([id,dic['ga_change_cnt'],dic['ga'],dic['version_pair'],dic['method_change_src'],''])
        id = id + 1
    csvfile.close()

def compare_experiment():
    # 读取compare的json文件 compare_json_file
    with open("/Users/pan/Desktop/total-refactor.json",'r') as compare_json_file:
        compare_json = json.load(compare_json_file)

    # 读取json文件 origin_json_file
    with open("/Users/pan/Desktop/deleted_result-4-23.json", 'r') as origin_json_file:
        origin_json = json.load(origin_json_file)

    with open('/Users/pan/Desktop/excel_relation_to_paper','r') as relation_file:
        relation_json = json.load(relation_file)


    total_precision = 0
    total_recall = 0
    true_negative_rate = 0

    total_TP_count = 0
    total_FP_count = 0
    total_FN_count = 0

    n_FP_count = 0
    n_TN_count = 0
    tnr = 0

    delete_mapped_y_count = 0
    delete_mapped_n_count = 0

    cross_ga_y_dict = {}
    cross_ga_n_dict = {}
    cross_result = {}

    y_json = origin_json['Y']
    n_json = origin_json['N']

    ########## 表五字段 ##########
    deprecation_message_TP_count = 0
    deprecation_message_FP_count = 0
    deprecation_message_TN_count = 0
    deprecation_message_FN_count = 0

    own_library_TP_count = 0
    own_library_FP_count = 0
    own_library_TN_count = 0
    own_library_FN_count = 0

    external_library_TP_count = 0
    external_library_FP_count = 0
    external_library_TN_count = 0
    external_library_FN_count = 0

    ########## 表六字段 ##########
    refactoring_class_move_class_TP_count = 0
    refactoring_class_move_class_FP_count = 0
    refactoring_class_move_class_TN_count = 0
    refactoring_class_move_class_FN_count = 0

    ########## E N D ##########

    for ga_info,ga_value in y_json.items():

        cross_version_dict = {}
        for vp_info,vp_value in ga_value.items():
            ga_and_v_pair = ga_info + "__fdse__" + vp_info

            find_flag = False
            cross_method_dict = {}
            for origin_method,mapped_method_json in vp_value.items():# list index 0 是对应的映射方法
                delete_mapped_y_count = delete_mapped_y_count + 1
                origin_method = origin_method.split('__fdse__')[1]

                origin_source = mapped_method_json['source']
                origin_relation = mapped_method_json['relation']


                comp_mapped_method_list = []
                for comp_ga_info,comp_ga_value in compare_json.items():
                    if not comp_ga_info.startswith(ga_and_v_pair):
                        continue

                    for comp_origin_method,comp_mapped_list in comp_ga_value.items():

                        if origin_method == comp_origin_method:
                            find_flag = True

                            for comp_mapped_dict in comp_mapped_list:
                                comp_mapped_method = list(comp_mapped_dict['after_method'].keys())[0]
                                comp_mapped_method_list.append(comp_mapped_method)

                            break
                temp_dict = {}
                if find_flag:
                    comp_mapped_method_set = set(comp_mapped_method_list)
                    origin_mapped_method_set = set(mapped_method_json['repl_method'])

                    intersection_result_set = comp_mapped_method_set & origin_mapped_method_set

                    TP_count = len(intersection_result_set)
                    FP_count = len(comp_mapped_method_set) - len(intersection_result_set)
                    FN_count = len(origin_mapped_method_set) - len(intersection_result_set)

                    if len(comp_mapped_method_set) == 0:
                        method_precision = 0
                    else:
                        method_precision = len(intersection_result_set) / len(comp_mapped_method_set)
                    method_recall = len(intersection_result_set) / len(origin_mapped_method_set)

                    temp_dict['origin_count'] = len(origin_mapped_method_set)
                    temp_dict['comp_count'] = len(comp_mapped_method_set)
                    temp_dict['TP_count'] = TP_count
                    temp_dict['FP_count'] = FP_count
                    temp_dict['FN_count'] = FN_count
                    temp_dict['method_precision'] = method_precision
                    temp_dict['method_recall'] = method_recall

                    total_TP_count = total_TP_count + TP_count
                    total_FP_count = total_FP_count + FP_count
                    total_FN_count = total_FN_count + FN_count

                    total_recall = total_recall + method_recall
                    total_precision = total_precision + method_precision

                else:
                    temp_dict['find'] = 'Not Find'
                    temp_dict['origin_count'] = len(origin_mapped_method_set)
                    FN_count = len(origin_mapped_method_set)
                    total_FN_count = total_FN_count + FN_count

                cross_method_dict[origin_method] = temp_dict

            cross_version_dict[vp_info] = cross_method_dict

        cross_ga_y_dict[ga_info] = cross_version_dict
    cross_result['Y'] = cross_ga_y_dict

    for ga_info,ga_value in n_json.items():
        cross_version_n_dict = {}
        for vp_info,vp_value in ga_value.items():
            ga_and_v_pair = ga_info + "__fdse__" + vp_info

            cross_method_n_dict = {}
            find_flag = False
            for origin_method in vp_value:
                delete_mapped_n_count = delete_mapped_n_count + 1

                origin_method = origin_method.split('__fdse__')[1]

                # 匹配方法
                comp_mapped_method_list = []
                for comp_ga_info,comp_ga_value in compare_json.items():
                    if not comp_ga_info.startswith(ga_and_v_pair):
                        continue

                    for comp_origin_method,comp_mapped_list in comp_ga_value.items():
                        if origin_method == comp_origin_method:
                            find_flag = True

                            for comp_mapped_dict in comp_mapped_list:
                                comp_mapped_method = list(comp_mapped_dict['after_method'].keys())[0]
                                comp_mapped_method_list.append(comp_mapped_method)
                            break

                temp_dict = {}

                if find_flag:
                    comp_mapped_method_set = set(comp_mapped_method_list)
                    temp_dict['comp_count'] = len(comp_mapped_method_set)
                    n_FP_count = n_FP_count + len(comp_mapped_method_set)

                    temp_dict['FP_count'] = len(comp_mapped_method_set)
                    if len(comp_mapped_method_set) == 0:
                        temp_dict['TN_count'] = 'Y'
                        tnr = tnr + 1
                        n_TN_count = n_TN_count + 1

                else:
                    temp_dict['find'] = 'Not Find'

                cross_method_n_dict[origin_method] = temp_dict

            cross_version_n_dict[vp_info] = cross_method_n_dict

        cross_ga_n_dict[ga_info] = cross_version_n_dict
    cross_result['N'] = cross_ga_n_dict

    average_precision = total_precision / delete_mapped_y_count
    # average_precision = total_TP_count / (total_TP_count + total_FP_count)
    average_recall = total_recall / delete_mapped_y_count
    # average_recall = total_TP_count / (total_TP_count + total_FN_count)
    true_negative_rate = n_TN_count / (n_TN_count + n_FP_count)

    print('delete_mapped_y_count:',delete_mapped_y_count)
    print('delete_mapped_n_count:',delete_mapped_n_count)
    print('total_precision:',total_precision)
    print('total_recall:',total_recall)
    print("=====================================")
    print("tnr",tnr/delete_mapped_n_count)
    print('average_precision:',average_precision)
    print('average_recall:',average_recall)
    print('true_negative_rate:',true_negative_rate)


    json_object = json.dumps(cross_result, indent=4, separators=(', ', ':'))
    output_file = open('/Users/pan/Desktop/cross.json','w')
    output_file.write(json_object)
    output_file.close()

def compare_aura_experiment():
    # 读取compare的json文件 compare_json_file
    with open("/Users/pan/Desktop/aura_result.json", 'r') as compare_json_file:
        compare_json = json.load(compare_json_file)

    # 读取json文件 origin_json_file
    with open("/Users/pan/Desktop/deleted_result-4-22.json", 'r') as origin_json_file:
        origin_json = json.load(origin_json_file)

    cross_ga_y_dict = {}
    cross_ga_n_dict = {}
    cross_result = {}
    y_json = origin_json['Y']
    n_json = origin_json['N']

    total_precision = 0
    total_recall = 0
    true_negative_rate = 0

    total_TP_count = 0
    total_FP_count = 0
    total_FN_count = 0

    delete_mapped_y_count = 0
    delete_mapped_n_count = 0


    for ga_info,ga_value in y_json.items():

        cross_version_dict = {}
        for vp_info,vp_value in ga_value.items():
            ga_and_v_pair = ga_info + "__fdse__" + vp_info

            find_flag = False
            cross_method_dict = {}
            temp_dict = {}

            for origin_method,mapped_method_json in vp_value.items():# list index 0 是对应的映射方法
                delete_mapped_y_count = delete_mapped_y_count + 1

                origin_method = origin_method.split('__fdse__')[1]
                origin_mapped_method_set = set(mapped_method_json['repl_method'])

                if ga_info not in compare_json.keys() or vp_info not in compare_json[ga_info].keys():
                    temp_dict['find'] = 'Not Find'
                    FN_count = len(origin_mapped_method_set)
                    total_FN_count = total_FN_count + FN_count

                else:
                    comp_mapped_method_list = []
                    find_flag = False
                    for comp_origin_method,comp_mapped_list in compare_json[ga_info][vp_info].items():
                        if origin_method == comp_origin_method:
                            find_flag = True
                            comp_mapped_method_list = comp_mapped_list
                            break

                    if find_flag:
                        comp_mapped_method_set = set(comp_mapped_method_list)

                        intersection_result_set = comp_mapped_method_set & origin_mapped_method_set

                        TP_count = len(intersection_result_set)
                        FP_count = len(comp_mapped_method_set) - len(intersection_result_set)
                        FN_count = len(origin_mapped_method_set) - len(intersection_result_set)

                        if len(comp_mapped_method_set) == 0:
                            method_precision = 0
                        else:
                            method_precision = len(intersection_result_set) / len(comp_mapped_method_set)
                        method_recall = len(intersection_result_set) / len(origin_mapped_method_set)

                        temp_dict['origin_count'] = len(origin_mapped_method_set)
                        temp_dict['comp_count'] = len(comp_mapped_method_set)
                        temp_dict['TP_count'] = TP_count
                        temp_dict['FP_count'] = FP_count
                        temp_dict['FN_count'] = FN_count
                        temp_dict['method_precision'] = method_precision
                        temp_dict['method_recall'] = method_recall

                        total_TP_count = total_TP_count + TP_count
                        total_FP_count = total_FP_count + FP_count
                        total_FN_count = total_FN_count + FN_count

                        # 用来求平均precision 和recall
                        total_recall = total_recall + method_recall
                        total_precision = total_precision + method_precision

                    else:
                        temp_dict['origin_count'] = len(origin_mapped_method_set)
                        FN_count = len(origin_mapped_method_set)
                        total_FN_count = total_FN_count + FN_count

                cross_method_dict[origin_method] = temp_dict

            cross_version_dict[vp_info] = cross_method_dict

        cross_ga_y_dict[ga_info] = cross_version_dict
    cross_result['Y'] = cross_ga_y_dict

    n_FP_count = 0
    n_TN_count = 0
    tnr = 0
    for ga_info,ga_value in n_json.items():
        cross_version_n_dict = {}
        for vp_info,vp_value in ga_value.items():
            ga_and_v_pair = ga_info + "__fdse__" + vp_info

            cross_method_n_dict = {}
            find_flag = False
            for origin_method in vp_value:
                delete_mapped_n_count = delete_mapped_n_count + 1

                origin_method = origin_method.split('__fdse__')[1]
                origin_mapped_method_set = set(mapped_method_json['repl_method'])

                # 匹配方法
                comp_mapped_method_list = []
                temp_dict = {}

                if ga_info not in compare_json.keys() or vp_info not in compare_json[ga_info].keys():
                    # 有但是没有 FN情况
                    temp_dict['find'] = 'Not Find'
                    FN_count = len(origin_mapped_method_set)
                    total_FN_count = total_FN_count + FN_count
                else:
                    comp_mapped_method_list = []
                    find_flag = False
                    for comp_origin_method, comp_mapped_list in compare_json[ga_info][vp_info].items():
                        if origin_method == comp_origin_method:
                            find_flag = True
                            comp_mapped_method_list = comp_mapped_list
                            break
                #####################################################################################

                    if find_flag:
                        comp_mapped_method_set = set(comp_mapped_method_list)
                        n_FP_count = n_FP_count + len(comp_mapped_method_set)
                        temp_dict['FP_count'] = len(comp_mapped_method_set)
                        if len(comp_mapped_method_set) == 0:
                            temp_dict['TN_count'] = 'Y'
                            temp_dict['origin_count'] = len(origin_mapped_method_set)
                            temp_dict['comp_count'] = len(comp_mapped_method_set)
                            tnr = tnr + 1
                            n_TN_count = n_TN_count + 1
                    else:
                        temp_dict['find'] = 'Not Find'

                cross_method_n_dict[origin_method] = temp_dict
            cross_version_n_dict[vp_info] = cross_method_n_dict
        cross_ga_n_dict[ga_info] = cross_version_n_dict
    cross_result['N'] = cross_ga_n_dict


    # average_precision = total_precision / delete_mapped_y_count
    average_precision = total_TP_count / (total_TP_count + total_FP_count)
    # average_recall = total_recall / delete_mapped_y_count
    average_recall = total_TP_count / (total_TP_count + total_FN_count)
    true_negative_rate = n_TN_count / (n_TN_count + n_FP_count)

    print('delete_mapped_y_count:',delete_mapped_y_count)
    print('delete_mapped_n_count:',delete_mapped_n_count)
    print('total_precision:',total_precision)
    print('total_recall:',total_recall)
    print("=====================================")
    print("tnr/总数：",tnr/delete_mapped_n_count)
    print('average_precision:',average_precision)
    print('average_recall:',average_recall)
    print('true_negative_rate:',true_negative_rate)


    json_object = json.dumps(cross_result, indent=4, separators=(', ', ':'))
    output_file = open('/Users/pan/Desktop/sss.json', 'w')
    output_file.write(json_object)
    output_file.close()

def calculate_aura_api_count():
    # 读取compare的json文件 compare_json_file
    with open("/Users/pan/Desktop/aura_result.json", 'r') as compare_json_file:
        compare_json = json.load(compare_json_file)

    total_method_count = 0
    has_mapping_method_count = 0

    ga_count = len(list(compare_json.keys()))
    vp_count = 0
    for ga_info,ga_value in compare_json.items():
        vp_count = vp_count + len(list(ga_value.keys()))
        for vp_info,vp_value in ga_value.items():
            total_method_count = total_method_count + len(list(vp_value.keys()))
            for method_info,method_value in vp_value.items():
                # print(type(method_value),"===",method_value)
                if len(method_value) != 0:
                    has_mapping_method_count = has_mapping_method_count + 1

    print("ga_count:", ga_count)
    print("vp_count:", vp_count)
    print("total_method_count:",total_method_count)
    print("has_mapping_method_count:",has_mapping_method_count)

def calculate_refactor_api_count():
    # 读取compare的json文件
    with open("/Users/pan/Desktop/total-refactor.json", 'r') as compare_json_file:
        compare_json = json.load(compare_json_file)

    total_method_count = 0
    has_mapping_method_count = 0

    ga_set = []
    vp_count = len(list(compare_json.keys()))
    for ga_info,ga_value in compare_json.items():
        ga_list = ga_info.split("__fdse__")
        ga = ga_list[0] + '__fdse__' + ga_list[1] + '__fdse__' + ga_list[2]
        ga_set.append(ga)

        total_method_count = total_method_count + len(ga_value)
        for origin_method_info,origin_method_value in ga_value.items():
            if len(origin_method_value) != 0:
                has_mapping_method_count = has_mapping_method_count + 1
            else:
                print(origin_method_info,origin_method_value)

    ga_count = len(set(ga_set))

    print("ga_count:", ga_count)
    print("vp_count:", vp_count)
    print("total_method_count:", total_method_count)
    print("has_mapping_method_count:", has_mapping_method_count)




# if __name__ == '__main__':
    # compare_experiment()
    # json_2_csv()
    # compare_aura_experiment()
    # calculate_aura_api_count()
    # calculate_refactor_api_count()



"""
    原来的匹配方法
    
    
        #
        #                     if origin_method == comp_origin_method and comp_mapped_method in mapped_method_json :
        #                         delete_mapped_count = delete_mapped_count + 1
        #                         delete_mapped_count_ga_version_pair.add(ga_and_v_pair)
        #                         # temp1[origin_method] = mapped_method
        #                         list1.append(temp1)
        #                         # temp_mapping_method.append(mapped_method)
        #                         cross_flag = True
        #                         cross_temp_dict['accuracy'] = 1/len(comp_mapped_list)
        #                         if cross_temp_dict['accuracy'] != 1:
        #                             print(cross_temp_dict['accuracy'])
        #
        #                 if origin_method == comp_origin_method:
        #                     delete_count = delete_count + 1
        #                     delete_count_ga_version_pair.add(ga_and_v_pair)
        #
        #                     cross_temp_dict['mapping_method'] = mapped_method_json
        #                     cross_temp_dict['tool_mapping_method'] = comp_mapped_list
        #
        #         if cross_flag == True:
        #             cross_temp_dict['T/F'] = 'True'
        #         else:
        #             if 'tool_mapping_method' in cross_temp_dict :
        #                 cross_temp_dict['T/F'] = 'False'
        #         # cross_temp_dict['mapping_method'] = mapped_method
        #         cross_method_dict[origin_method] = cross_temp_dict
        #
        #     cross_version_dict[vp_info] = cross_method_dict
        #
        # cross_result[ga_info] = cross_version_dict


        #     if len(list1) != 0:
        #         temp0[vp_info] = list1
        #         list0.append(temp0)
        #
        # if len(list0) != 0:
    #     result_dict[ga_info] = list0
    """

"""        
    原来的匹配方法
        #
        #                     if origin_method == comp_origin_method and comp_mapped_method in mapped_method_json :
        #                         delete_mapped_count = delete_mapped_count + 1
        #                         delete_mapped_count_ga_version_pair.add(ga_and_v_pair)
        #                         # temp1[origin_method] = mapped_method
        #                         list1.append(temp1)
        #                         # temp_mapping_method.append(mapped_method)
        #                         cross_flag = True
        #                         cross_temp_dict['accuracy'] = 1/len(comp_mapped_list)
        #                         if cross_temp_dict['accuracy'] != 1:
        #                             print(cross_temp_dict['accuracy'])
        #
        #                 if origin_method == comp_origin_method:
        #                     delete_count = delete_count + 1
        #                     delete_count_ga_version_pair.add(ga_and_v_pair)
        #
        #                     cross_temp_dict['mapping_method'] = mapped_method_json
        #                     cross_temp_dict['tool_mapping_method'] = comp_mapped_list
        #
        #         if cross_flag == True:
        #             cross_temp_dict['T/F'] = 'True'
        #         else:
        #             if 'tool_mapping_method' in cross_temp_dict :
        #                 cross_temp_dict['T/F'] = 'False'
        #         # cross_temp_dict['mapping_method'] = mapped_method
        #         cross_method_dict[origin_method] = cross_temp_dict
        #
        #     cross_version_dict[vp_info] = cross_method_dict
        #
        # cross_result[ga_info] = cross_version_dict

    with open(path_v0_v1 +".json", 'r') as json_file:
        json_data_list = json.load(json_file)

        #     if len(list1) != 0:
        #         temp0[vp_info] = list1
        #         list0.append(temp0)
        #
        # if len(list0) != 0:
        #     result_dict[ga_info] = list0

    # print("match missing method & replacement method: %d in %d ga version pair" % (delete_mapped_count,len(delete_mapped_count_ga_version_pair)))
    # print("match missing method: %d in %d ga version pair"  % (delete_count,len(delete_count_ga_version_pair)))
"""

