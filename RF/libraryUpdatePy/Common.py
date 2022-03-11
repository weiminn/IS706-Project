
LIBDETECT_CONFIG = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/path_config.properties'

ROOT_PATH = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/'

ROOT_DATA_PATH = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-data/'

ROOT_PROJECT1 = '/home/hadoop/dfs/data/Workspace/projects_9_19/projects_git/'
ROOT_PROJECT2 = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/projects_extra/85_3000/repository/'


# 1. LibDetect API Extraction data merge, no filter

DEP_DB_PATH = ROOT_DATA_PATH + 'dep-db-%s.json'
USAGE_DB_PATH = ROOT_DATA_PATH + 'usage-db-%s.json' 

# 2. FIM and GA version pair selection 


MANUALLY_SELECTED_V_PAIR = ROOT_DATA_PATH + 'manually_selected_version_pair.json'

FIM_FILE = ROOT_DATA_PATH + 'usage-overview-FIM-%s.json'

USAGE_COUNT_OVERVIEW = ROOT_DATA_PATH +'usage-count-%s.json'
USAGE_COUNT_OVERVIEW_ALL = ROOT_DATA_PATH +'usage-count-%s-all.json'
RANKEDGA =  ROOT_DATA_PATH + 'rankedGAVersionAndAPICount-%s.json'
RANKEDGAVPair =  ROOT_DATA_PATH + 'topNiGAVersionPair-%s.json'
# 3.

FINAL_RESULT = ROOT_DATA_PATH + 'usage_final_result-%s.json'


FINAL_RESULT_A_DELETED = ROOT_DATA_PATH + 'deleted_result/temp_final_result_%s-%s.json'

FINAL_RESULT_DELETED_EXCEL = ROOT_DATA_PATH + 'deleted_result/usage_final_result-deleted-excel-%s.csv'

DELETED_VALIDATION_PATH = ROOT_DATA_PATH + 'deleted_result/'

METRIC_RESULT = ROOT_DATA_PATH + 'metric_result-%s.json'

DELETED_METHOD_GROUND_TRUTH = ROOT_DATA_PATH + 'deleted_result/del-gt-%s.json'
DELETED_METHOD_GROUND_TRUTH_FILTERED = ROOT_DATA_PATH + 'deleted_result/del-gt-%s-filtered.json'







GT_1 = ROOT_PATH + 'output/groundtruth/Ex1-21-4-23.xls'

GT_3 = ROOT_PATH + 'output/groundtruth/Deleted-method-ex3-4-21-NEW.xls'
# GT_3 = ROOT_PATH + 'output/groundtruth/deleted-methods-21-4-20.xls'

