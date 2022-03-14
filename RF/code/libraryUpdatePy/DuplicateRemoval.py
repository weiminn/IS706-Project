# 根据4个字段去重
# method_change_src
# method_change_dst
# deleted_line
# added_line
import json
import ast
def queryResult(result,json_data):
    flag = False
    for test_duplicate in result:
        if json_data['method_change_src'] == test_duplicate['method_change_src'] \
                and json_data['method_change_dst'] == test_duplicate['method_change_dst'] \
                and json_data['deleted_line'] == test_duplicate['deleted_line'] \
                and json_data['added_line'] == test_duplicate['added_line'] :

            if json_data['ga_change_cnt'] in test_duplicate['ga_change_cnt']:
                return
            flag = True
            break
        else:
            continue
    if flag:
        test_duplicate['ga_change_cnt'].append(json_data['ga_change_cnt'])
        return
    # flag false
    add_dict = {}

    add_dict['method_change_src'] = json_data['method_change_src']
    add_dict['method_change_dst'] = json_data['method_change_dst']
    add_dict['deleted_method'] = json_data['deleted_method']
    add_dict['added_method'] = json_data['added_method']
    add_dict['deleted_line'] = json_data['deleted_line']
    add_dict['added_line'] = json_data['added_line']
    add_dict['changed_file_name'] = json_data['changed_file_name']
    add_dict['match_version_type'] = json_data['match_version_type']
    add_dict['ga_change_cnt'] = []
    add_dict['ga_change_cnt'].append(json_data['ga_change_cnt'])
    add_dict['version_pair'] = json_data['version_pair']
    add_dict['ga'] = json_data['ga']
    add_dict['project'] = json_data['project']
    add_dict['commit'] = json_data['commit']
    add_dict['parent_commit'] = json_data['parent_commit']
    add_dict['match_version'] = json_data['match_version']

    result.append(add_dict)

def duplicate_removal():
    # with open("/Users/pan/Desktop/results-4-7-v0-v1.json", 'r') as duplicate_json_file:
    #     duplicate_json_list = json.load(duplicate_json_file)

    with open('/Users/pan/Desktop/results-4-7-v0.json','r') as file:
        duplicate_json_list = json.load(file)

    result_list= []

    for json_data in duplicate_json_list:
        queryResult(result_list,json_data)

    # json_object = json.dumps(result_list, indent=4, separators=(', ', ':'))
    # output_file = open('/Users/pan/Desktop/v0.json','w')
    # output_file.write(json_object)
    # output_file.close()
    #
    print(len(result_list))

if __name__ == '__main__':
    duplicate_removal()