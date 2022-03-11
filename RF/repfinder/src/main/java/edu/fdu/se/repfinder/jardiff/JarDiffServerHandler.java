package edu.fdu.se.repfinder.jardiff;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import edu.fdu.se.repfinder.JDT.JDTHelper;
import edu.fdu.se.repfinder.global.Config;
import edu.fdu.se.repfinder.global.Global;
import edu.fdu.se.repfinder.server.MethodBean;
import edu.fdu.se.repfinder.server.MyNetUtil;
import edu.fdu.se.repfinder.util.GAVUtil;
import edu.fdu.se.repfinder.util.LibUtil;
import edu.fdu.se.repfinder.util.SootMethodToString;

import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;

@SuppressWarnings("Duplicates")
public class JarDiffServerHandler implements HttpHandler {

    /**
     *
     * input:
     * jsonobject: g a v1,v2
     *             list<usage>
     *
     *                 {
     *     "groupId":"redis.clients",
     *     "artifactId":"jedis",
     *     "version2":"2.8.1",
     *     "version1":"2.7.3",
     *     "usage_array":[
     *         "com.google.gson.internal.reflect.UnsafeReflectionAccessor.makeAccessible(AccessibleObject)",
     *         "com.google.gson.internal.PreJava9DateFormatProvider.getUSDateFormat(int)"
     *     ]
     *
     *     }
     * output      g a v1,
     *             list<usage,added/deleted/modifed/same>
     * @param exchange
     */
    @Override
    public void handle(HttpExchange exchange) {
        try {
            InputStream is = exchange.getRequestBody();
            OutputStream os = exchange.getResponseBody();
            String contentType = exchange.getRequestHeaders().get("Content-type").get(0);
            Object jsonObject = MyNetUtil.parsePostedKeys(is, contentType);
            String resp = "{}";
            if(jsonObject instanceof JSONObject) {
                String result = doDiff((JSONObject) jsonObject);
                if (result != null) {
                    resp = result;
                }
            }
            exchange.sendResponseHeaders(200, resp.length());
            os.write(resp.getBytes());
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            exchange.close();
        }
    }

    /**
     *
     * @param jsonObject
     */
    private String doDiff(JSONObject jsonObject){
        String groupId = jsonObject.getString("groupId");
        String artifactId = jsonObject.getString("artifactId");
        String version1 = jsonObject.getString("version1");
        String version2 = jsonObject.getString("version2");
        JSONArray apiArray = jsonObject.getJSONArray("usage_array");
        boolean isAllDiffAPI = false;
        if(jsonObject.containsKey("all_diff_api")){
            isAllDiffAPI = jsonObject.getBoolean("all_diff_api");
        }
        Global.setLogger(JarDiffServerHandler.class);
        Global.logger.info(groupId + " " + artifactId + " " + version1 + " " + version2);
//        String jointName = LibUtil.getJointJarName(artifactId, version, classifier);
        String gah = LibUtil.getMD5LibName(groupId, artifactId);
        String realJarPathPrev = Config.JAR_PATH + gah + "/"+ GAVUtil.jarNameFromGAHV(gah +"__fdse__" + version1);
        String realJarPathCurr = Config.JAR_PATH + gah + "/"+ GAVUtil.jarNameFromGAHV(gah +"__fdse__" + version2);

        boolean res = GAVUtil.loadJarPair(gah +"__fdse__" + version1, gah +"__fdse__" + version2);
        if (!res) {
            System.out.println("unable to load jar");
            return null;
        }
        Global.logger.info("do diff");
        JarDiffGson jarDiffGson = new JarDiffGson();
        String decompilePath = Config.DECOMPILE_PATH + "/" +gah;
        DiffInfo diffInfo = jarDiffGson.diffJar(gah,realJarPathPrev, realJarPathCurr, decompilePath);
        DiffInfoPrinter.printDiffInfo(diffInfo);

        // DiffInfo -> added/modified/deleted/same
        String result;
        if(isAllDiffAPI){
            result = getDiffInfoAsJsonString(diffInfo);
        }else {
            JSONObject resultArray;
            resultArray = queryDiffInfoToJSONArray(diffInfo, apiArray);
            result = resultArray.toJSONString();
        }
        Global.logger.info("success");
        return result;

    }

    private String getDiffInfoAsJsonString(DiffInfo diffInfo){
        JSONObject jsonObject = diffInfo.deletedItemtoJSONObject();
        return jsonObject.toJSONString();
    }


    private JSONObject queryDiffInfoToJSONArray(DiffInfo diffInfo, JSONArray apiArray){

        //  key added/deleted/modified/same added/deleted/modifed info
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("added",new JSONArray());
        jsonObject.put("deleted",new JSONArray());
//        jsonObject.put("same",new JSONArray());
        jsonObject.put("modified",new JSONArray());
//        jsonObject.put("modified_similairty",new JSONArray());
        for(int i =0;i<apiArray.size();i++) {
            String s = apiArray.getString(i);
            //
            List<String> status = queryDiffInfo(diffInfo,s);
            String statusKey = status.get(0);
            if("same".equals(statusKey)){
                continue;
            }
            jsonObject.getJSONArray(statusKey).add(s);
            //todo
//            if("modified".equals(statusKey)){
//                String simiValue = status.get(1);
//                jsonObject.getJSONArray(statusKey).add(s);
//                jsonObject.getJSONArray("modified_similairty").add(simiValue);
//            }else{
    //            jsonObject.getJSONArray(statusKey).add(s);
//            }
        }
        return jsonObject;
    }

    /**
     *
     * @param diffInfo
     * @param s
     * @return [added/deleted/modified/same, simiValue]
     */
    private List<String> queryDiffInfo(DiffInfo diffInfo,String s){
        String[] data = JDTHelper.methodStringSplit(s);
        List<String> ret = new ArrayList<>();
        if(data == null){
            ret.add("same");
            return ret;
        }
        String className = data[0];
        String methodName = data[1];
        MethodBean methodBean = null;
        List<ClassBean> addedClassMethod =  diffInfo.addedClassesList;
        methodBean = isMatchDiffBean(addedClassMethod,className,methodName,"added");
        if(methodBean != null){
            ret.add("added");
            return ret;
        }
        List<ClassBean> deletedClassMethod = diffInfo.deletedClassList;
        methodBean = isMatchDiffBean(deletedClassMethod,className,methodName,"deleted");
        if(methodBean != null){
            ret.add("deleted");
            return ret;
        }
        List<ClassBean> addedMethod = diffInfo.modifiedClassMap.get("addedMethod");
        methodBean = isMatchDiffBean(addedMethod,className,methodName,"added");
        if(methodBean != null){
            ret.add("added");
            return ret;
        }
        List<ClassBean> modifiedMethodPrev = diffInfo.modifiedClassMap.get("modifiedMethodPrev");
        methodBean = isMatchDiffBean(modifiedMethodPrev,className,methodName,"modified");
        if(methodBean != null){
            ret.add("modified");
            ret.add(String.valueOf(methodBean.getCallGraphSimilarity()));
            return ret;
        }
        List<ClassBean> modifiedMethodCurr = diffInfo.modifiedClassMap.get("modifiedMethodCurr");
        methodBean = isMatchDiffBean(modifiedMethodCurr,className,methodName,"modified");
        if(methodBean != null){
            ret.add("modified");
            ret.add(String.valueOf(methodBean.getCallGraphSimilarity()));
            return ret;
        }
        List<ClassBean> deletedMethod = diffInfo.modifiedClassMap.get("deletedMethod");
        methodBean = isMatchDiffBean(deletedMethod,className,methodName,"deleted");
        if(methodBean != null){
            ret.add("deleted");
            return ret;
        }
        ret.add("same");
        return ret;

    }

    private MethodBean isMatchDiffBean(List<ClassBean> classBeans, String className, String methodName, String key){
        for(ClassBean cb : classBeans){
            List<MethodBean> mbs = cb.getMethodBeans();
            MethodBean ret = isMatchDiffBean(className,methodName,cb.getFileSubPath(),mbs);
            if(ret !=null){
                return ret;
            }
        }
        return null;

    }

    private MethodBean isMatchDiffBean(String className,String methodName,String classPath,List<MethodBean> methodBeans){
        String classPath2 = classPath.substring(0,classPath.length()-5);
        String classPath3 = classPath2.replace("/",".");
        if(className.equals(classPath3)){
            for(MethodBean methodBean:methodBeans){
                String shortName = SootMethodToString.removeBracket(methodBean.getMethodSignatureWithoutPackAndClassName());
                if(shortName.equals(methodName)){
                    return methodBean;
                }
            }
        }

        return null;
    }



}
