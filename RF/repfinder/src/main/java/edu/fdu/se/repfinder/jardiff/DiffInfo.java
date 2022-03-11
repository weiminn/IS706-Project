package edu.fdu.se.repfinder.jardiff;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;
import edu.fdu.se.repfinder.server.MethodBean;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class DiffInfo {

    /**
     * 增加的class
     */
    @Expose(serialize = true)
    @SerializedName("ADDED_FILES")
    public List<ClassBean> addedClassesList;

    /**
     * 删除的class
     */
    @Expose(serialize = true)
    @SerializedName("REMOVED_FILES")
    public List<ClassBean> deletedClassList;

    /**
     * key:
     * addedMethod
     * deletedMethod
     * modifiedMethodPrev
     * modifiedMethodCurr
     *
     */
    @Expose(serialize = true)
    @SerializedName("MODIFIED_FILES")
    public Map<String,List<ClassBean>> modifiedClassMap;


    public DiffInfo(){
        this.modifiedClassMap = new HashMap<>();
        this.modifiedClassMap.put("addedMethod",new ArrayList<>());
        this.modifiedClassMap.put("deletedMethod",new ArrayList<>());
        this.modifiedClassMap.put("modifiedMethodPrev",new ArrayList<>());
        this.modifiedClassMap.put("modifiedMethodCurr",new ArrayList<>());
    }

    @Expose(serialize = true)
    private String prevRootPath;

    @Expose(serialize = true)
    private String currRootPath;


    public String getPrevRootPath() {
        return prevRootPath;
    }

    public void setPrevRootPath(String prevRootPath) {
        this.prevRootPath = prevRootPath;
    }

    public String getCurrRootPath() {
        return currRootPath;
    }

    public void setCurrRootPath(String currRootPath) {
        this.currRootPath = currRootPath;
    }

//
//    @Expose(serialize = true)
//    public String prevShortName;
//
//    @Expose(serialize = true)
//    public String currShortName;

    @Expose(serialize = true)
    private String prevDecompilePath;


    @Expose(serialize = true)
    private String currDecompilePath;


    public String getPrevDecompilePath() {
        return prevDecompilePath;
    }

    public void setPrevDecompilePath(String prevDecompilePath) {
        this.prevDecompilePath = prevDecompilePath;
    }

    public String getCurrDecompilePath() {
        return currDecompilePath;
    }

    public void setCurrDecompilePath(String currDecompilePath) {
        this.currDecompilePath = currDecompilePath;
    }




    public JSONObject deletedItemtoJSONObject(){
        JSONObject result = new JSONObject();
        JSONArray deletedClasses = new JSONArray();
        result.put("deleted_classes", deletedClasses);
        List<ClassBean> classBeans = this.deletedClassList;
        for(ClassBean classBean:classBeans){
            JSONObject classJson = new JSONObject();
            String prefix = getClassFullName(classBean);
            classJson.put("class_name",prefix);
            JSONArray fieldArr = toFieldArray(classBean.getFieldBeans(),prefix);
            JSONArray methodArr = toMethodArray(classBean.getMethodBeans(),prefix);
            classJson.put("deleted_fields_in_class",fieldArr);
            classJson.put("deleted_method_in_class",methodArr);
            deletedClasses.add(classJson);
        }
        //input
        List<ClassBean> deletedMethodInExistingClass = this.modifiedClassMap.get("deletedMethod");
        JSONArray deletedEntryInClass = new JSONArray();
        result.put("undeleted_class_deleted_items",deletedEntryInClass);
        for(ClassBean classBean:deletedMethodInExistingClass){
            JSONObject classJson = new JSONObject();
            String prefix = getClassFullName(classBean);
            classJson.put("class_name", prefix);
            JSONArray fieldArr = toFieldArray(classBean.getFieldBeans(),prefix);
            JSONArray methodArr = toMethodArray(classBean.getMethodBeans(),prefix);
            classJson.put("deleted_fields_in_class",fieldArr);
            classJson.put("deleted_method_in_class",methodArr);
            deletedEntryInClass.add(classJson);
        }
        return result;
    }

    private JSONArray toFieldArray(List<FieldBean> fieldBeans, String prefix){
        JSONArray jsonArray = new JSONArray();
        for(FieldBean fieldBean:fieldBeans){
            String s = fieldBean.getFieldType() + "__fdse__" + prefix + "." +fieldBean.getFieldName();
            jsonArray.add(s);

        }
        return jsonArray;

    }

    private JSONArray toMethodArray(List<MethodBean> methodBeans, String prefix){
        JSONArray jsonArray = new JSONArray();
        for(MethodBean methodBean: methodBeans){
            String s = methodBean.getReturnType() + "__fdse__" + methodBean.getMethodSignatureWithNewClassAndPackageName(prefix);
            if(methodBean.getModifier().contains("public")) {
                jsonArray.add(s);
            }
        }
        return jsonArray;
    }


    private String getClassFullName(ClassBean classBean){
//        String name = classBean.getClassName();
        String path = classBean.getFileSubPath();
        path = path.replace("/",".");
        return path.substring(0,path.length()-5);
    }


}
