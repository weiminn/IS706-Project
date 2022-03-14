package edu.fdu.se.repfinder.jardiff;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import edu.fdu.se.repfinder.global.Config;
import edu.fdu.se.repfinder.preprocess.DiffMetaInfo;
import edu.fdu.se.repfinder.server.MethodBean;
import edu.fdu.se.repfinder.util.DirUtil;
import edu.fdu.se.repfinder.util.FileRWUtil;
import edu.fdu.se.repfinder.util.FileUtil;
import edu.fdu.se.repfinder.util.JavaMethodUtil;

import java.io.*;
import java.util.*;

@SuppressWarnings("Duplicates")
public class JarDiffGson {

    private String libPrev;
    private String libCurr;


    public DiffInfo diffJar(String md5LibName, String libPrev, String libCurr, String decompilePath){

        File fPrev = new File(libPrev);
        File fCurr = new File(libCurr);
        this.libCurr = libCurr;
        this.libPrev = libPrev;
        Gson gson = new GsonBuilder().excludeFieldsWithoutExposeAnnotation().setPrettyPrinting().create();
        String name = fPrev.getName().substring(0, fPrev.getName().length() - 4)+"__fdse__"+fCurr.getName().substring(0, fCurr.getName().length() - 4);
        String outputFileName = Config.JAR_DIFF_INFO_PATH +"/" + md5LibName+"/"+name+".json";
        File outputFile = new File(outputFileName);
        if(outputFile.exists()){
            //cache
            String content = FileUtil.read(outputFileName);
            DiffInfo diffInfo = gson.fromJson(content,DiffInfo.class);
            return diffInfo;
        }

        DiffInfo diffInfo = new JarDiffGson().doDiff(libPrev,libCurr,decompilePath);
        String jsonString = gson.toJson(diffInfo);
        FileRWUtil.writeInAll(outputFileName,jsonString);
        return diffInfo;
    }


    private Map<String,Set<String>> coarseDiffOfDir(String decomPrevPath, String decomCurrPath){
        List<File> decomPrevFiles = DirUtil.getAllJavaFilesOfADirectory(decomPrevPath);
        List<File> decomCurrFiles = DirUtil.getAllJavaFilesOfADirectory(decomCurrPath);
        Set<String> prevPaths = subPathOfFiles(decomPrevFiles, decomPrevPath.length());
        Set<String> currPaths = subPathOfFiles(decomCurrFiles, decomCurrPath.length());
        Set<String> intersection = new HashSet<>();
        intersection.addAll(prevPaths);
        intersection.retainAll(currPaths);
        prevPaths.removeAll(intersection);
        currPaths.removeAll(intersection);
        Map<String,Set<String>> result = new HashMap<>();
        result.put("add", currPaths);
        result.put("delete",prevPaths);
        result.put("modify",intersection);
        return result;

    }

    private void parseAddOrDeleteResult(DiffInfo diffInfo,Set<String> subPaths, int addOrDelete){
        String prefixPath;
        if(addOrDelete == 1){
            // add
            prefixPath = diffInfo.getCurrRootPath();
        }else if(addOrDelete == 2){
            // delete
            prefixPath = diffInfo.getPrevRootPath();
        }else{
            return;
        }
        List<ClassBean> classBeans = new ArrayList<>();
        if(addOrDelete == 1){
            diffInfo.addedClassesList = classBeans;
        }else if(addOrDelete == 2){
            diffInfo.deletedClassList = classBeans;
        }
        try {
            for (String s : subPaths) {
                ClassBean bean = DiffMetaInfo.singleFileMethodNameClassBean(new FileInputStream(new File(prefixPath + s)));

                if (bean != null) {
                    bean.setFileSubPath(s);
                    classBeans.add(bean);
                }
            }
        }catch (Exception e){
            e.printStackTrace();
        }


    }

    /**
     *  一个modify的文件pair 会有多个ClassBean的key
     *  key1 ClassBean -> modifiedClassMap[addedMethod]
     *  key2 Classbean -> modifiedClassMap[deletedMethod]
     *  key3 Classbean -> modifiedClassMap[modifiedMethodPrev]
     *  key4 Classbean -> modifiedClassMap[modifiedMethodCurr]
     *
     *  Classbean的key都属于同一个ClassBean
     *
     * @param diffInfo
     * @param subPaths
     */
    private void parseModifiedResult(DiffInfo diffInfo,Set<String> subPaths){
        String decomPrevPath = diffInfo.getPrevRootPath();
        String decomCurrPath = diffInfo.getCurrRootPath();
        for (String s : subPaths) {
            try {
                File prevFile = new File(decomPrevPath + s);
                File currFile = new File(decomCurrPath + s);
                if (prevFile.length() == currFile.length()) {
                    continue;
                }
                InputStream prevIS = new FileInputStream(prevFile);
                InputStream currIS = new FileInputStream(currFile);
                // 拿到Deleted Modified Added Same 方法列表
                JSONObject joo = DiffMetaInfo.filePairDiffMethodNameList(prevIS,currIS);
                // Added 和Deleted 提前可以封装
                addedMethodDeletedMethodToMethodBean(s,diffInfo,joo);
                modifiedMethodSameMethodToMethodBean(s,diffInfo,joo);

            } catch (FileNotFoundException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private void addedMethodDeletedMethodToMethodBean(String fileSubPath,DiffInfo diffInfo, JSONObject joo){
        String className = joo.getString("class_name");
        ClassBean addedMethods = toAddedOrDeletedMethodBean(diffInfo, joo.getJSONArray("added_methods"));
        ClassBean deletedMethods = toAddedOrDeletedMethodBean(diffInfo, joo.getJSONArray("deleted_methods"));
        if(addedMethods != null) {
            addedMethods.setFileSubPath(fileSubPath);
            addedMethods.setClassName(className);
            diffInfo.modifiedClassMap.get("addedMethod").add(addedMethods);
        }
        if(deletedMethods != null){
            deletedMethods.setFileSubPath(fileSubPath);
            deletedMethods.setClassName(className);
            diffInfo.modifiedClassMap.get("deletedMethod").add(deletedMethods);
        }
    }
    private void modifiedMethodSameMethodToMethodBean(String fileSubPath,DiffInfo diffInfo, JSONObject joo){
        String className = joo.getString("class_name");
        List<ClassBean> modifiedMethods = toChangedMethodBean(diffInfo,joo.getJSONArray("changed_methods"));
        if(modifiedMethods != null && modifiedMethods.size() == 2) {
            modifiedMethods.get(0).setFileSubPath(fileSubPath);
            modifiedMethods.get(1).setFileSubPath(fileSubPath);
            modifiedMethods.get(0).setClassName(className);
            modifiedMethods.get(1).setClassName(className);
            diffInfo.modifiedClassMap.get("modifiedMethodPrev").add(modifiedMethods.get(0));
            diffInfo.modifiedClassMap.get("modifiedMethodCurr").add(modifiedMethods.get(1));
        }
        // same methods
//        JSONArray sameArray = joo.getJSONArray("same_methods");
        // call graph similarity and methods array
        // todo call graph diff
//        List<Double> simiList = CallGraphDiffMain.callGraphMethodSimilarity(this.libPrev, this.libCurr,sameArray);
//
//        List<ClassBean> callGraphDiffMethods = toCallGraphChangedMethodBean(diffInfo,joo.getJSONArray("same_methods"),simiList);
//        // same methods -> DiffInfo
//
//        if(callGraphDiffMethods != null && callGraphDiffMethods.size() == 2) {
//            callGraphDiffMethods.get(0).setFileSubPath(fileSubPath);
//            callGraphDiffMethods.get(1).setFileSubPath(fileSubPath);
//            callGraphDiffMethods.get(0).setClassName(className);
//            callGraphDiffMethods.get(1).setClassName(className);
//            diffInfo.modifiedClassMap.get("modifiedMethodPrev").add(callGraphDiffMethods.get(0));
//            diffInfo.modifiedClassMap.get("modifiedMethodCurr").add(callGraphDiffMethods.get(1));
//        }


    }


    private ClassBean toAddedOrDeletedMethodBean(DiffInfo diffInfo, JSONArray jsonArray){
        if(jsonArray == null || jsonArray.size() == 0){
            return null;
        }
        ClassBean bean = new ClassBean();
        for(int i=0;i<jsonArray.size();i++){
            JSONObject joo = jsonArray.getJSONObject(i);
            if(joo.containsKey("field")){
                List<FieldBean> fieldBean = DiffMetaInfo.toFieldBean(joo);
                bean.getFieldBeans().addAll(fieldBean);
            }else if(joo.containsKey("method_name")){
                MethodBean methodBean = DiffMetaInfo.toMethodBean(joo);
                bean.getMethodBeans().add(methodBean);
            }
        }
        return bean;
    }

    private List<ClassBean> toChangedMethodBean(DiffInfo diffInfo, JSONArray jsonArray){
        if(jsonArray == null || jsonArray.size() == 0){
            return null;
        }
        ClassBean prevBean = new ClassBean();
        ClassBean currBean = new ClassBean();
        List<ClassBean> result = new ArrayList<>();
        for(int i=0;i<jsonArray.size();i++){
            JSONObject joo = jsonArray.getJSONObject(i);
            if(joo.containsKey("method_name")){
                MethodBean methodBean = DiffMetaInfo.toMethodBean(joo);
                prevBean.getMethodBeans().add(methodBean);
                currBean.getMethodBeans().add(methodBean);
            }
        }
        result.add(prevBean);
        result.add(currBean);
        return result;
    }

    private List<ClassBean> toCallGraphChangedMethodBean(DiffInfo diffInfo, JSONArray jsonArray,List<Double> similarityList){
        if(jsonArray == null || jsonArray.size() == 0){
            return null;
        }
        ClassBean prevBean = new ClassBean();
        ClassBean currBean = new ClassBean();
        List<ClassBean> result = new ArrayList<>();
        for(int i=0;i<jsonArray.size();i++){
            JSONObject joo = jsonArray.getJSONObject(i);
            double simi = similarityList.get(i);
            if(joo.containsKey("method_name")){
                MethodBean methodBean = DiffMetaInfo.toMethodBean(joo);
                methodBean.setCallGraphSimilarity(simi);
                prevBean.getMethodBeans().add(methodBean);
                currBean.getMethodBeans().add(methodBean);
            }
        }
        // 同一个method bean 放到了两个地方
        result.add(prevBean);
        result.add(currBean);
        return result;
    }




    /**
     *
     * @param libPrevPath
     * @param libCurrPath
     * @return JSONObject result
     *
     */
    public DiffInfo doDiff(String libPrevPath, String libCurrPath, String outputDir){
        String decomPrevPath = JavaMethodUtil.decompileJar(libPrevPath, outputDir,false);
        String decomCurrPath = JavaMethodUtil.decompileJar(libCurrPath, outputDir,false);
        DiffInfo diffInfo = new DiffInfo();
        diffInfo.setPrevRootPath(decomPrevPath);
        diffInfo.setCurrRootPath(decomCurrPath);
        Map<String,Set<String>> coarseDiffResult = coarseDiffOfDir(decomPrevPath,decomCurrPath);
        parseAddOrDeleteResult(diffInfo,coarseDiffResult.get("add"),1);
        parseAddOrDeleteResult(diffInfo,coarseDiffResult.get("delete"),2);
        parseModifiedResult(diffInfo,coarseDiffResult.get("modify"));

        return diffInfo;

    }

    public static Set<String> subPathOfFiles(List<File> mList, int len) {
        Set<String> s = new HashSet<>();
        for (File f : mList) {
            s.add(f.getAbsolutePath().substring(len));
        }
        return s;
    }
}
