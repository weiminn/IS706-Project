package edu.fdu.se.repfinder.analysis;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import edu.fdu.se.repfinder.analysis.jaranalysispack.*;
import edu.fdu.se.repfinder.analysis.thirdlibanalysis.*;
import edu.fdu.se.repfinder.analysis.thirdlibanalysis.ThirdJarDataPack;
import edu.fdu.se.repfinder.global.Config;
import edu.fdu.se.repfinder.util.DirUtil;
import edu.fdu.se.repfinder.util.GAVUtil;
import edu.fdu.se.repfinder.util.JavaMethodUtil;

import java.io.File;
import java.util.*;

/**
 * @author huangkaigfeng
 * @Date 2021-02-17
 */
public class ThirdJarAnalysis {

    private String gaHash;

    private Map<String, JSONObject> result;


    public static Map<String, ThirdJarDataPack> toAnalyzeList;

    public static final int FIND_SUPER = 1;
    public static final int FIND_THIS = 2;
    public static final int FIND_ALL = 3;

    public static String libraryPath;

    private String version1;
    private String version0;



    public ThirdJarAnalysis(String gaHash, Map<String,JSONObject> result,String v0, String v1){
        this.gaHash = gaHash;
        this.result = result;
        this.version1 = v1;
        this.version0 = v0;


    }



    public void run(){
        //初始化search path
        initSearchPaths(toAnalyzeList);
        for(Map.Entry<String,ThirdJarDataPack> entry : toAnalyzeList.entrySet()){
            String method = entry.getKey();
            ThirdJarDataPack thirdJarDataPack = entry.getValue();
            JSONObject resultPack = this.result.get(method);
            boolean isContinue = false;
            if(resultPack.containsKey("find_map")){
                if (resultPack.getBoolean("find_map")){
                    if(resultPack.containsKey("is_similar")){
                       //containkey
                        if(resultPack.getBoolean("is_similar")){
                            // not continue
                            isContinue = false;
                        }else{
                            isContinue = true;
                        }
                    }else{
                        isContinue = true;
                    }
                }else{
                    isContinue = false;
                }
            }
            if(isContinue){
                continue;
            }

            int flag = thirdJarDataPack.findSuperorSelf;

            List<String> searchPaths = thirdJarDataPack.searchClassPaths;
            // 1. JDK
            int jdkSta = SearchJDKJar.searchJDKJar(searchPaths,thirdJarDataPack);
            if (jdkSta == AnalysisConstant.FIND_CLASS_FIND_METHOD || jdkSta == AnalysisConstant.FIND_CLASS_NOT_FIND_METHOD){
                continue;
            }
            // 2. Dependency
            int depSta = SearchDependencyJars.searchDependencyJars(searchPaths,thirdJarDataPack,this.gaHash, this.version1);
            if (depSta == AnalysisConstant.FIND_CLASS_FIND_METHOD || depSta == AnalysisConstant.FIND_CLASS_NOT_FIND_METHOD){
                continue;
            }
            // 3. 属于同个groupId的Module 但是没有在2中找到
            int moduleSta = SearchModuleJars.searchModuleJars(searchPaths,thirdJarDataPack,this.gaHash,this.version1);
            if (moduleSta == AnalysisConstant.FIND_CLASS_FIND_METHOD || moduleSta == AnalysisConstant.FIND_CLASS_NOT_FIND_METHOD){
                continue;
            }
            // 4. lucene 匹配
            if(Config.THIRD_JAR_STEP4) {
                int onlineSta = SearchOnlineJars.searchOnlineJars(searchPaths,thirdJarDataPack,this.gaHash,this.version0,this.version1);
                if (onlineSta == AnalysisConstant.FIND_CLASS_FIND_METHOD || onlineSta == AnalysisConstant.FIND_CLASS_NOT_FIND_METHOD){
                    continue;
                }
            }
//            if(resultPack.getBoolean("find_map")){
//                this.result.get(method).put("source_type","jar3");
//            }

        }
    }

    /**
     *  设置ThirdJarDataPack.searchPath
     * @param toAnalyzeList
     */
    public void initSearchPaths(Map<String,ThirdJarDataPack> toAnalyzeList){
        //init search paths todo
        // List<String
        for(Map.Entry<String,ThirdJarDataPack> entry:toAnalyzeList.entrySet()){
            String method = entry.getKey();
            ThirdJarDataPack thirdJarDataPack = entry.getValue();
            int flag = thirdJarDataPack.findSuperorSelf;
            NewMethodBean methodBean = thirdJarDataPack.methodBean;
            List<String> searchPaths = getSearchClassPath(flag,methodBean);
            thirdJarDataPack.searchClassPaths = searchPaths;
        }
    }

    private List<String> getSearchClassPath(int flag, NewMethodBean methodBean){
        List<String> searchClassPaths = new ArrayList<>();
        if(ThirdJarAnalysis.FIND_SUPER == flag){
            if (methodBean.getSuperClassPath() != null){
                searchClassPaths.add(methodBean.getSuperClassPath() + ".java");
            }
            else if(methodBean.superInterfaceNameAndPath.size() != 0){
                for(Map.Entry<String,String> entry : methodBean.superInterfaceNameAndPath.entrySet()){
                    String path = entry.getValue();
                    searchClassPaths.add(path + ".java");
                }
            }
        }
        if(ThirdJarAnalysis.FIND_THIS == flag){
            searchClassPaths.add(methodBean.getClassPath() + ".java");
        }
        return searchClassPaths;

    }


    /**
     * 单独测试 jar3的逻辑的时候，需要确定是找This Class，还是找this class的super class，
     * 还是找this class的super class的super class...也就是找第一个在this jar中找不到的class，并加入到search path
     * @param methods
     */
    public void initData(JSONArray methods,String v0,String v1){

        String realJarPathCurr = Config.JAR_PATH + this.gaHash + "/"+ GAVUtil.jarNameFromGAHV(this.gaHash + "__fdse__" + v1);
        String decompilePath = Config.DECOMPILE_PATH + "/" + this.gaHash;
        String decomCurrPath = JavaMethodUtil.decompileJar(realJarPathCurr, decompilePath,false);
        File decomFile = new File(decomCurrPath);
        if(!decomFile.exists()){
            return;
        }
        List<File> v1Files = DirUtil.getAllJavaFilesOfADirectory(decomCurrPath);

        ThirdJarAnalysis.toAnalyzeList = new HashMap<>();
        for(int i = 0; i < methods.size(); i ++) {
            String method = methods.getString(i);
            NewMethodBean methodBean = JarAnalysisUtil.splitMethod(method);
            String classPath = decomCurrPath + methodBean.getClassPath() + ".java";
            boolean exists = IsClassExistInPackage.isClassExistInPackage(classPath);
            if(exists) {
                // class 存在在原来的jar包，那么既然跑到jar3，那么就是需要在jar3中搜索super class
                // e.g. JEdisPoolConfig 存在在原来的jar ， set super class信息： Generic
                int isSuperExistInOriginalJar = IsSuperClassExist.isSuperClassExist(classPath,methodBean,decomCurrPath,v1Files);
//                String superClassName = "";
                if(isSuperExistInOriginalJar == 3){

//                    methodBean.getSuperClassName() 这个superclass是remote，本地没有找到
                    // 下一步找Generic
                    //todo 已经在isSuperClassExist中设置过了 super class的信息
                    //设置method bean里面super class为 Generic
//                    methodBean.setSuperClassName(superClassName);
//                    methodBean.setSuperClassPath(superClassName);

                }else{
                    //  methodBean.getSuperClassName() 这个superclass是remote，本地找到了
                    // class的super class存在在原来的jar，那么需要找super class的super class
                    // 设置method bean里面super class为 BaseObjectPoolConfig
                    //todo FIXME-----------------
//                    setSuperClassSuperClass()
//                    methodBean.setSuperClassName(superClassName);
//                    methodBean.setSuperClassPath(superClassName);
                }
                //需要设置find 的super class
                ThirdJarDataPack thirdJarDataPack = new ThirdJarDataPack(this.result.get(method),ThirdJarAnalysis.FIND_SUPER,methodBean,method);
                ThirdJarAnalysis.toAnalyzeList.put(method,thirdJarDataPack);

            }else{
                // class 在原来的jar包不存在，那么在jar3中搜索this class 和super class
                ThirdJarDataPack thirdJarDataPack = new ThirdJarDataPack(this.result.get(method),ThirdJarAnalysis.FIND_THIS,methodBean,method);
                ThirdJarAnalysis.toAnalyzeList.put(method,thirdJarDataPack);
            }


        }
    }










}
