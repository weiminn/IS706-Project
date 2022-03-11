package edu.fdu.se.repfinder.jardiff;

import com.alibaba.fastjson.JSONObject;
import edu.fdu.se.repfinder.global.Global;
import edu.fdu.se.repfinder.server.MethodBean;

import java.util.List;
import java.util.Map;

public class DiffInfoPrinter {

    private static int methodNumber(ClassBean classBean){
        List<MethodBean> methodBeans = classBean.getMethodBeans();
        return methodBeans.size();
    }

    private static int listMethodNumber(List<ClassBean> classBeans){
        int sum = 0;
        for(ClassBean classBean:classBeans){
            sum += methodNumber(classBean);
        }
        return sum;
    }

    public static void printDiffInfo(DiffInfo diffInfo){
        Global.setLogger(DiffInfoPrinter.class);
        int num1 = listMethodNumber(diffInfo.addedClassesList);
        int num2 = listMethodNumber(diffInfo.deletedClassList);

        int num3 = listMethodNumber(diffInfo.modifiedClassMap.get("addedMethod"));
        int num4 = listMethodNumber(diffInfo.modifiedClassMap.get("modifiedMethodPrev"));
        int num5 = listMethodNumber(diffInfo.modifiedClassMap.get("modifiedMethodCurr"));
        int num6 = listMethodNumber(diffInfo.modifiedClassMap.get("deletedMethod"));

        int added = num1 +num3;
        int deleted = num2 + num6;
        Global.logger.info("JarDiff: Added method number: " + added);
        Global.logger.info("JarDiff: Deleted method number: " + deleted);
        Global.logger.info("JarDiff: Modified method number: " + num4 +"," +num5);


    }

    public static void printAPIUsageInfo(JSONObject jsonObject){
        Global.logger.info("CodeBase: v1 API Invoked in lib number: " + jsonObject.getInteger("v1InvokeNumber"));
        Global.logger.info("CodeBase: v2 API Invoked in lib number: " + jsonObject.getInteger("v2InvokeNumber"));

    }


    public static void printIntersectionInfo(Map<String,List<String>> intersections){
        int s = intersections.get("added_method").size();
        int s2 = intersections.get("deleted_method").size();
        int s3 = intersections.get("changed_method_prev").size();
        int s4 = intersections.get("changed_method_curr").size();
        int s5 = s+s2+s3+s4;
        Global.logger.info("Intersection api number: " + s5);

        Global.logger.info("Intersection added method number: " + s);
        Global.logger.info("Intersection deleted method number: " + s2);
        Global.logger.info("Intersection changed_method_prev method number: " + s3);
        Global.logger.info("Intersection changed_method_curr method number: " + s4);

    }


    public static void printSnippetInfo(Map<String,Integer> snipptUsageNum){
        int s = snipptUsageNum.get("added_method");
        int s2 = snipptUsageNum.get("deleted_method");
        int s3 = snipptUsageNum.get("changed_method_prev");
        int s4 = snipptUsageNum.get("changed_method_curr");

        Global.logger.info("Snippet found added_method number: " + s);
        Global.logger.info("Snippet found deleted_method number: " + s2);
        Global.logger.info("Snippet found changed_method_prev number: " + s3);
        Global.logger.info("Snippet found changed_method_curr number: " + s4);

    }

}
