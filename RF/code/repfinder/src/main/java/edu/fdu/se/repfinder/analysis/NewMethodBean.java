package edu.fdu.se.repfinder.analysis;

import edu.fdu.se.repfinder.server.MethodBean;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @author huangkaigfeng
 * @Date 2021-02-16
 */
public class NewMethodBean extends MethodBean {


    private String packageName;

    private String className;

    private String superClassName;
    private List<String> superClassTemplateArgs;

    private String superClassPath;

    public int isSuperClassOrInterfaceThirdParty;

    public Map<String,String> superInterfaceNameAndPath;

    public List<String> sibMethods;


    public NewMethodBean(){
        superInterfaceNameAndPath = new HashMap<>();
        isSuperClassOrInterfaceThirdParty = -1;
    }

    public void setPackageName(String packageName) {
        this.packageName = packageName;
    }

    public void setClassName(String className) {
        this.className = className;
    }

    public String getPackageName(){

        return packageName;
    }

    public String getPackagePath(){
        return packageName.replace(".","/");
    }


    public String getClassName(){

        return className;
    }


    public String getClassPath(){
        return getPackagePath()+ "/"+ className;
    }

    public String getSuperClassName(){
        return this.superClassName;
    }

    public void setSuperClassName(String superClassName){
        this.superClassName = superClassName;
    }

    public void setSuperClassTemplateArgs(String varArgs){

        if(varArgs == null || varArgs.equals("")) {
            return;
        }
        int index = varArgs.indexOf(",");
        List<String> temp = new ArrayList<>();
        if(index!=-1){
            String[] data = varArgs.split(",");
            for(String a:data){
                temp.add(a);
            }
        }else{
            temp.add(varArgs);
        }
        this.superClassTemplateArgs = temp;
    }

    public List<String> getSuperClassTemplateArgs() {
        return superClassTemplateArgs;
    }

    public String getSuperClassPath(){
        return this.superClassPath;
    }
    public void setSuperClassPath(String path){
        this.superClassPath =  path;
    }

    public List<String> getSibMethods(){
        return null;
    }


//    public String getMethodSignatureWithoutPackageAndClassPrefix(){
//        return this.getMethod
//        String s = this.getMethodSignatureShort().replace(this.getPackageName()+ ".","");
//        String s2 = s.replace(this.getClassName() + ".","");
//        return s2;
//    }


    

}
