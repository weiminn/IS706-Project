import json
from libraryUpdatePy.empiricalData.F_select_validate import filterNullMap

def mappingGroundTruth():
    result = {}
    result['com.google.common.io.Files.newInputStreamSupplier(File)'] = ['Files.asByteSource(File)']
    result['com.google.common.io.ByteStreams.newInputStreamSupplier(byte[])'] = ['Files.asByteSource(File)']
    result['com.google.common.io.Files.newReaderSupplier(File,Charset)'] = ['Resources.asByteSource(URL)']
    result['com.google.common.io.Files.newOutputStreamSupplier(File)'] = ['ByteSource.wrap(byte[])']
    result['com.google.common.io.Resources.newInputStreamSupplier(URL)'] = ['Files.asCharSource(File, Charset)']
    result['org.eclipse.jetty.server.Server.setThreadPool(ThreadPool)'] = ['Server.Server(ThreadPool pool)']
    result['redis.clients.jedis.JedisPoolConfig.setMaxActive(int)'] = ['setMaxTotal()']
    result['org.apache.lucene.search.Hits.iterator()'] = ['TopScoreDocCollector','TopDocs']
    result['org.apache.lucene.search.Hit.getDocument()'] = ['TopScoreDocCollector','TopDocs']
    result['org.apache.lucene.util.NumericUtils.floatToPrefixCoded(float)'] = ['floatToSortableInt']
    result['org.apache.lucene.util.NumericUtils.doubleToPrefixCoded(double)'] = ['doubleToSortableLong']
    result['org.apache.lucene.document.NumericField.setIntValue(int)'] = ['NumericDocValuesField']
    result['org.apache.lucene.document.NumericField.setLongValue(long)'] = ['NumericDocValuesField']
    result['org.apache.lucene.document.NumericField.setDoubleValue(double)'] = ['NumericDocValuesField']
    result['org.apache.lucene.document.NumericField.setFloatValue(float)'] = ['NumericDocValuesField']
    result['org.apache.lucene.document.Document.getFieldable(String)'] = ['Document.getField(String)','Document.getFields(String)']
    result['org.jsoup.select.Elements.get(int)'] = ['Element.select(String)']
    result['org.elasticsearch.action.search.SearchResponse.hits()'] = ['SearchResponse.getHits()']
    result['org.elasticsearch.action.bulk.BulkItemResponse.failed()'] = ['BulkItemResponse.isFailed()']
    result['org.elasticsearch.index.query.GeoDistanceFilterBuilder.lat(double)'] = ['GeoDistanceQueryBuilder.lat(double)']
    result['org.elasticsearch.index.query.GeoDistanceFilterBuilder.distance(double,DistanceUnit)'] = ['GeoDistanceQueryBuilder.distance(double,DistanceUnit)']
    result['org.elasticsearch.index.query.RangeFilterBuilder.gte(Object)'] = ['RangeQueryBuilder.gte(Object)']
    result['org.elasticsearch.index.query.GeoBoundingBoxFilterBuilder.bottomRight(double,double)'] = ['GeoBoundingBoxQueryBuilder.bottomRight(double,double)']
    result['org.elasticsearch.index.query.RangeFilterBuilder.gt(Object)'] = ['RangeQueryBuilder.gt(Object)']
    result['org.elasticsearch.common.settings.ImmutableSettings.settingsBuilder()'] = ['Settings.builder()']
    result['org.elasticsearch.index.query.GeoBoundingBoxFilterBuilder.topLeft(double,double)'] = ['GeoBoundingBoxQueryBuilder.topLeft(double,double)']
    result['org.elasticsearch.index.query.RangeFilterBuilder.lt(Object)'] = ['RangeQueryBuilder.lt(Object)']
    result['org.elasticsearch.index.query.RangeFilterBuilder.lte(Object)'] = ['RangeQueryBuilder.lte(Object)']
    result['org.elasticsearch.index.query.GeoDistanceFilterBuilder.lon(double)'] = ['GeoDistanceQueryBuilder.lon(double)']
    result['org.elasticsearch.action.index.IndexResponse.isCreated()'] = ['IndexResponse.status()']
    result['org.elasticsearch.action.delete.DeleteResponse.isFound()'] = ['DeleteResponse.status()']
    result['org.elasticsearch.common.settings.Settings.settingsBuilder()'] = ['Settings.builder()']
    result['org.elasticsearch.node.NodeBuilder.settings(Settings)'] = ['Node(Settings)']
    result['org.elasticsearch.action.search.SearchRequestBuilder.setFilter(FilterBuilder)'] = ['SearchRequestBuilder.setQuery(QueryBuilder)']
    return result

def findDeletedAPIs(seqId,usage):
    deletedAPI = set()
    for m in usage:
        seq = m['apiSeq']
        if m['id'] == seqId:
            for api in seq:
                if api['changeType'] == 'deleted':
                    deletedAPI.add(api['api'])
    return list(deletedAPI)

def findMappedAPIs(deletedAPI,groundTruth):
    res = []
    for api in deletedAPI:
        data = api.split('__fdse__')
        if data[-1] in groundTruth:
            res.append(groundTruth[data[-1]])
    return res


def validate():
    rootPath = '/home/hadoop/dfs/data/Workspace/LibraryUpdate/2020-data/'
    gt = mappingGroundTruth()
    key = 'a_has_deleted'
    with open(rootPath + 'usage_final_result-21-1-14-filter.json','r') as f:
        finalResult = json.load(f)
        deleted = finalResult[key]
    filteredResult = filterNullMap(deleted)
    distinctAPI = set()
    distinctMappedAPI = set()
    
    for ga in filteredResult:
        for versionPair in filteredResult[ga]:
            usage = filteredResult[ga][versionPair]['usage']
            simi_map = filteredResult[ga][versionPair]['simi_map']
            for m in simi_map:
                original_seq_id = m['original_seq_id']
                
                deletedAPIs = findDeletedAPIs(original_seq_id,usage)
                for api in deletedAPIs:
                    distinctAPI.add(api)
                mappedAPIs = findMappedAPIs(deletedAPIs,gt)

                dst_seq_map = m['dst_seq_map']
                allDstAPIs = set()
                for dst in dst_seq_map:
                    dstId = dst[0]['id']
                    apiSeq = dst[0]['apiSeq']
                    for apiBean in apiSeq:
                        allDstAPIs.add(apiBean['api'])

                for api in allDstAPIs:
                    haveAPIMapped = False
                    for mapped in mappedAPIs:
                        for sub in mapped:
                            if sub in api:
                                haveAPIMapped = True
                                distinctMappedAPI.add(api)
                                break
                        if haveAPIMapped:
                            break
    print(len(distinctAPI))
    print(len(distinctMappedAPI))
    for i in distinctMappedAPI:
        print(i)

validate()

