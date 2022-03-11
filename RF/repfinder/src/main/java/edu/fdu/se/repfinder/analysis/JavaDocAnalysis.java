package edu.fdu.se.repfinder.analysis;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;

import edu.fdu.se.repfinder.analysis.javadocanalysispack.DeprecatedAPIInfo;
import edu.fdu.se.repfinder.analysis.javadocanalysispack.JavaDocAnalysisPack;
import edu.fdu.se.repfinder.analysis.thirdlibanalysis.JarEntryExistanceUtil;
import edu.fdu.se.repfinder.global.Config;
import edu.fdu.se.repfinder.global.Global;
import edu.fdu.se.repfinder.server.JarAPIDeprecationHandler;
import edu.fdu.se.repfinder.util.GAVUtil;
import edu.fdu.se.repfinder.util.LibUtil;
import edu.fdu.se.repfinder.util.SootMethodToString;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import soot.SootMethod;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 * @author huangkaigfeng
 * @Date 2021-02-14
 */
public class JavaDocAnalysis {

    private Map<String,JSONObject> result;

    private int existingToMapSize;

    public JavaDocAnalysis(Map<String,JSONObject> result){
        this.result = result;
        this.existingToMapSize = 0;
        for(Map.Entry<String,JSONObject> entry:result.entrySet()){
            if(!entry.getValue().getBoolean("find_map")){
                this.existingToMapSize ++;
            }
        }
    }

    public Map<String,JSONObject> run(String groupId, String artifactId, String v0, String v1, JSONArray methods, JSONArray versions){

        Collections.reverse(versions);
        for(int i = 0; i < versions.size(); i ++) {
            if(this.existingToMapSize == 0){
                break;
            }
            String version = versions.getString(i);
            String gavh = LibUtil.getMD5LibName(groupId, artifactId);
            boolean res = GAVUtil.loadJavaDoc(gavh + "__fdse__" + version);
            if (!res) {
                System.out.println("unable to load javadoc");
                continue;
            }
            String realJarPath = Config.JAR_PATH + gavh + "/" + GAVUtil.javaDocNameFromGAHV(gavh + "__fdse__" + version);
            Global.setLogger(JarAPIDeprecationHandler.class);
            Global.logger.info(groupId + " " + artifactId + " " + version);
            Map<String,List<DeprecatedAPIInfo>> deprecatedInfoAll = JavaDocAnalysisPack.getDeprecatedAPIs(realJarPath);
            if(deprecatedInfoAll == null || deprecatedInfoAll.size() == 0 ){
                continue;
            }
            if((!deprecatedInfoAll.containsKey("Methods")) && (!deprecatedInfoAll.containsKey("Packages"))&&(!deprecatedInfoAll.containsKey("Classes"))){
                continue;
            }
            for(int j = 0; j < methods.size(); j++){
                String method = methods.getString(j);
                if(this.result.get(method).getBoolean("find_map")){
                    continue;
                }
                NewMethodBean newMethodBean = JarAnalysisUtil.splitMethod(method);
                //搜索部分
                DeprecatedAPIInfo deprecatedAPIInfo = JavaDocAnalysisPack.findIfMethodIsDeprecated(newMethodBean,realJarPath,deprecatedInfoAll);
                if(deprecatedAPIInfo==null){
                    deprecatedAPIInfo = JavaDocAnalysisPack.findIfClassIsDeprecated(newMethodBean,realJarPath,deprecatedInfoAll);
                }
                if(deprecatedAPIInfo == null){
                    continue;
                }
                //map部分
                String s = deprecatedAPIInfo.element.html();
                this.result.get(method).put("desc",s);
                findMapping(deprecatedAPIInfo,newMethodBean,version,method,realJarPath);
            }
        }

        return null;

    }


    /**
     *
     * @param deprecatedAPIInfo
     * @param newMethodBean
     * @param version
     * @param method JSONObject的key值，e.g: org...__fdse__org...methodName(CLASSNAME,...)
     * @param javaDocJarPath
     */
    private void findMapping(DeprecatedAPIInfo deprecatedAPIInfo, NewMethodBean newMethodBean, String version, String method, String javaDocJarPath){
        //仅仅是声明deprecated
        JSONObject jsonObject = this.result.get(method);
        jsonObject.put("deprecated_list",true);
        jsonObject.put("deprecated_list_version",version);
        // 暂时设置为true
//        jsonObject.put("find_map",true);
        this.result.put(method,jsonObject);
        List<String> mappedMethod = null;
        String mapType = null;
        if("Classes".equals(deprecatedAPIInfo.key)){
            mappedMethod = classLinkAndText(deprecatedAPIInfo,newMethodBean,method,javaDocJarPath);
            mapType = "map class";

        }else if("Methods".equals(deprecatedAPIInfo.key)){
            mappedMethod = methodLinkAndText(deprecatedAPIInfo,newMethodBean,method,javaDocJarPath);
            mapType = "map methods";

        }
        if(mappedMethod != null && mappedMethod.size() != 0){
            mappedMethod.remove(method);
            this.result.get(method).put("mapped_method", mappedMethod);
            this.result.get(method).put("find_map", true);
            this.result.get(method).put("map_type", mapType);
            this.result.get(method).put("source_type","javadoc");
        }
        return;
    }

    /**
     * 处理JAVADOC的类变更
     * @param deprecatedAPIInfo
     * @param methodBean
     * @param method
     * @param javaDocJarPath
     * @return
     */
    private List<String> classLinkAndText(DeprecatedAPIInfo deprecatedAPIInfo, NewMethodBean methodBean, String method, String javaDocJarPath){
        Element trElement = deprecatedAPIInfo.element;
        Element tdElement = trElement.child(0);
        Elements aElements = tdElement.getElementsByTag("a");
        List<String> hrefList = new ArrayList<>();
        int hrefSize = 0;
        String firstHref = null;
        for(Element href : aElements){
            String href1 = href.attr("href");
            if(firstHref == null && !"".equals(href1)){
                firstHref = href1;
                continue;
            }
            if(href1 != null && !"".equals(href1)){
                hrefSize ++;
                hrefList.add(href1);
            }
        }
        if (hrefSize >= 1){
            String methodName = methodBean.getMethodSignatureWithoutPackAndClassName();
            return classLink(hrefList,methodName);
        }else{
            return classText(deprecatedAPIInfo,methodBean,method,javaDocJarPath);
        }
    }

    private List<String> methodLinkAndText(DeprecatedAPIInfo deprecatedAPIInfo, NewMethodBean methodBean, String method, String javaDocJarPath){
        Element trElement = deprecatedAPIInfo.element;
        Element tdElement = trElement.child(0);

        Elements aElements = tdElement.getElementsByTag("a");
        List<String> hrefList = new ArrayList<>();

        int hrefSize = 0;
        String firstHref = null;
        for(Element href : aElements){
            String href1 = href.attr("href");
            if (firstHref == null && !"".equals(href1)){
                firstHref = href1;
                continue;
            }
            if (href1 != null && !"".equals(href1) && href1.contains("#")){
                hrefSize ++;
                hrefList.add(href1);
            }
        }
        if (hrefSize >= 1){
            return methodLink(hrefList);
        }else{
            return methodText(deprecatedAPIInfo,methodBean,method,javaDocJarPath);
        }

    }

    private List<String> methodLink(List<String> hrefList){
        List<String> mappingMethod = new ArrayList<>();
        for (String href : hrefList){
            int index = href.indexOf(".html");
            String newHref = href.substring(0,index);
            //TODO 只解决了规则的带#的method link的链接
            String []tempArray = href.split("#");
            String methodName = tempArray[1];
            JSONObject jo = getMappingMethod(methodName);
            methodName = jo.getString("method_name");
            String parameterResult = jo.getString("parameter");
            newHref = newHref + "."+ methodName + "(" + parameterResult + ")";
            //TODO 只解决完整括号的逻辑
            newHref = newHref.replace("/",".");
            mappingMethod.add(newHref);
        }
        return mappingMethod;
    }

    private JSONObject getMappingMethod(String methodName){
        //参数是由括号包围
        int left = methodName.indexOf('(');
        int right = methodName.indexOf(')');
        String parameter = "";
        String parameterResult = "";
        if (left != -1 && right != -1 ){
            parameter = methodName.substring(left + 1, right).replace(" ","").replace("--","");
        }
        //还有：-参数-()
        else if (methodName.contains("-")){
            left = methodName.indexOf("-");
            right = methodName.length()-1;
            parameter = methodName.substring(left + 1, right).replace(" ","").replace("(","").replace(")","");
        }

        parameterResult = handleParameter(parameter);
        methodName = methodName.substring(0,left);
        JSONObject jo = new JSONObject();
        jo.put("method_name",methodName);
        jo.put("parameter",parameterResult);
        return jo;
    }

    private String handleParameter(String parameter){

        StringBuilder parameterResult = new StringBuilder();
        if(parameter.contains("-")){
            parameter = parameter.replace("-",",");
        }
        if(parameter.contains(",")){
            //多个参数的情况
            String []parameters = parameter.split(",");
            int paraLength = parameters.length;
            int count = 0;
            for (String para : parameters){
                if(para.contains(".")) {
                    para = para.split("\\.")[para.split("\\.").length - 1];
                }
                count ++;
                if(count != paraLength){
                    parameterResult.append(para).append(",");
                }
                else{
                    parameterResult.append(para);
                }
            }
        }
        else {
            //只有一个参数的情况
            parameterResult = new StringBuilder(parameter.split("\\.")[parameter.split("\\.").length - 1]);
        }
        return parameter.length() == 0 ? parameter : parameterResult.toString();
    }

    private JSONObject matchFindText(DeprecatedAPIInfo apiInfo, int isFind){
        Elements tagIs = apiInfo.element.getElementsByTag("i");
        Pattern pat1 = Pattern.compile("Use <code>.*?</code>");
        Pattern pat2 = Pattern.compile("Use .*? ");
        String findText = null;
        for(Element element:tagIs){
            String htmlText = element.html();
            Matcher mat1 = pat1.matcher(htmlText);
            while(mat1.find()) {
                findText = mat1.group();
                isFind = 1;
                break;
            }
            if(isFind == 1){
                break;
            }
            // Use xxx 提取xxx
            Matcher mat2 = pat2.matcher(htmlText);
            while(mat2.find()) {
                findText = mat2.group();
                isFind = 2;
                break;
            }
            if(isFind == 2){
                break;
            }

        }
        JSONObject jo = new JSONObject();
        jo.put("is_find",isFind);
        jo.put("find_text",findText);
        return jo;
    }

    private List<String> methodText(DeprecatedAPIInfo apiInfo, NewMethodBean methodBean,String method,String javaDocJarPath){

        List<String> mappingMethodResult = new ArrayList<>();

        JSONObject jsonObject = this.result.get(method);
        String text = jsonObject.getString("desc");
        int isFind = 0;
        JSONObject jo = matchFindText(apiInfo,isFind);
        isFind = jo.getInteger("is_find");
        String findText = jo.getString("find_text");
        if(isFind != 0){
            findText = findText.replace("&nbsp","").replace(";","");
            //提到了方法，判断情况直接替换
            if(findText.contains("#")){
                if(isFind == 1) {
                    findText = findText.replace("Use <code>", "").replace("</code>", "");
                }
                else {
                    //TODO
//                    findText = findText.replace("Use ", "").replace(">", "").replace("&nbsp;", "").replace(" ", "");
                }
                mappingMethodResult = methodTextMappingMethod(findText,methodBean);
            }
            //row 380没有#是方法
            else if(findText.contains("(")){
                if(isFind ==1){
                    findText = findText.replace("Use <code>", "").replace("</code>", "");
                }
                else{
                    String methodName = findText.split(" ")[1];
                    if(!methodName.contains(".")){
                        // 方法
                        mappingMethodResult = methodTextMappingMethod(findText,methodBean);
                    }
                    else{
                        // ?.method()
                    }
                }
            }
            //没有提到方法名、参数等变更，仅仅是更换类等
            else {
                List<String> searchClassName = new ArrayList<>();
                if (isFind == 1) {
                    findText = findText.replace("Use <code>", "").replace("</code>", "");
                }
                else {
                    String className = findText.split(" ")[1];
                    if (findText.contains("'")){
                        className = className.substring(0,className.indexOf("'"));
                        searchClassName.add(className);
                    }
                }
                mappingMethodResult = classTextMappingMethod(javaDocJarPath,searchClassName,methodBean);
            }
        }
        return mappingMethodResult;
    }

    /**
     * Deprecated List中的Text 处理含有方法信息的变更
     * 1.use xxx.xxx()
     * 2.use xxx()
     * @param findText
     * @param methodBean
     * @return
     */
    private List<String> methodTextMappingMethod(String findText, NewMethodBean methodBean){
        List<String> mappingMethodResult = new ArrayList<>();
        String mappingMethod = "";

        if(!findText.contains(")")){
            findText = findText + ")";
        }

        // #Method()
        if(findText.startsWith("#")){
            findText = findText.replace("#","");
            //方法不仅包括方法名，还有包、类名等
            if(findText.contains(".")){

            }
            findText = SootMethodToString.transParameterLongNameToShortName(findText);
            mappingMethod = methodBean.getMethodSignatureWithPackAndClassName().replace(methodBean.getMethodSignatureWithoutPackAndClassName(),findText);
            mappingMethodResult.add(mappingMethod);
            return mappingMethodResult;
        }
        else if(!findText.contains(".")){
            // Class#Method()
            if(findText.contains("#")) {
                String oldClassName = methodBean.getClassName();
                String oldMethodName = methodBean.getMethodSignatureWithoutPackAndClassName();
                String newClassName = findText.split("#")[0];
                String newMethodName = findText.split("#")[1];

                newMethodName = SootMethodToString.transParameterLongNameToShortName(newMethodName);
                mappingMethod = methodBean.getMethodSignatureWithPackAndClassName().replace(oldClassName + "." + oldMethodName, newClassName + "." + newMethodName);
            }
            //Method()
            else{
                findText = SootMethodToString.transParameterLongNameToShortName(findText);
                mappingMethod = methodBean.getMethodSignatureWithPackAndClassName().replace(methodBean.getMethodSignatureWithoutPackAndClassName(),findText);
            }

            if(!"".equals(mappingMethod)){
                mappingMethodResult.add(mappingMethod);
            }

        }


        return mappingMethodResult;
    }

    /**
     * Deprecated List中的Text 处理只写明 use xxx类的变更
     * @param javaDocJarPath
     * @param searchClassName
     * @param methodBean
     * @return
     */
    private List<String> classTextMappingMethod(String javaDocJarPath, List<String> searchClassName, NewMethodBean methodBean){
        List<String> mappingMethodResult = new ArrayList<>();
        // add class name from findText -> searchClassName
        List<String> matchedPath = JarEntryExistanceUtil.isJavaDocEntryExist(javaDocJarPath,searchClassName);
        if(matchedPath != null && matchedPath.size() != 0) {
            InputStream is = JarEntryExistanceUtil.getHtmlTextFromEntry(javaDocJarPath, matchedPath.get(0));
            String html = new BufferedReader(new InputStreamReader(is)).lines().collect(Collectors.joining("\n"));
            Document doc = Jsoup.parse(html);

            //suspectedFullClassName : org...Class
            String suspectedFullClassName = doc.getElementsByTag("h2").get(0).text();
            suspectedFullClassName = suspectedFullClassName.replace(" ","").replace("Class",".");

            //original Method Information
            //e.g: getDirectory
            String methodOnlyName = methodBean.getMethodName();
            Elements suspectedMethodElements = doc.select(String.format("a[name^=%s]",methodOnlyName+"("));
            String methodName = methodBean.getMethodSignatureWithoutPackAndClassName();
            if(!suspectedMethodElements.isEmpty()){
                String mappingResult = "";
                if(suspectedMethodElements.size() > 1){
                    String newMethodName = suspectedMethodElements.attr("name");
                    newMethodName = SootMethodToString.transParameterLongNameToShortName(newMethodName);
                    if(methodName.equals(newMethodName)){
                        mappingResult = suspectedFullClassName + "." + methodName;
                    }
                }
                else{
                    mappingResult = suspectedFullClassName + "." + suspectedMethodElements.attr("name");
                }
                if(!"".equals(mappingResult)){
                    mappingMethodResult.add(mappingResult);
                }
            }
        }
        return mappingMethodResult;
    }

    /**
     *
     * @param hrefList
     * @param methodName
     * @return
     */
    private List<String> classLink(List<String> hrefList, String methodName){
        List<String> mappingMethod = new ArrayList<>();
        for (String href : hrefList){
            if (href.contains("#")){
                int left = href.indexOf("-");
                int methodNameIndex = href.indexOf("#");
                if (left == -1){
                    left = href.indexOf("(");
                }
                methodName = href.substring(methodNameIndex+1,left);
                int right = href.length()-1;
                String para = href.substring(left+1,right);
                para.replace("-",",");
                para = handleParameter(para);
                if(para.length() != 0){
                    methodName = methodName + "(" + para + ")";
                }
            }
            int index = href.indexOf(".html");
            String newHref = href.substring(0,index);
            newHref = newHref.replace('/','.') + "." + methodName;

            mappingMethod.add(newHref);
        }
        return mappingMethod.size() > 0? mappingMethod : null;
    }

    private List<String> classText(DeprecatedAPIInfo apiInfo, NewMethodBean methodBean, String method, String javaDocJarPath){
        JSONObject jsonObject = this.result.get(method);
        String text = jsonObject.getString("desc");
        List<String> mappingMethodResult = new ArrayList<>();
        int isFind = 0;
        JSONObject jo = matchFindText(apiInfo,isFind);
        isFind = jo.getInteger("is_find");
        String findText = jo.getString("find_text");
        if(isFind != 0){
            if(isFind == 2){
                String className = "";
                className = findText.split(" ")[1];
                List<String> searchClassName = new ArrayList<>();
                searchClassName.add(className);
                mappingMethodResult = classTextMappingMethod(javaDocJarPath,searchClassName,methodBean);
            }
            return mappingMethodResult;
        }

        return null;
    }
}
