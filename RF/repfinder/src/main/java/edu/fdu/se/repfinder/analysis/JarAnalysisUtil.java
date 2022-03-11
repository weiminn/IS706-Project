package edu.fdu.se.repfinder.analysis;

import edu.fdu.se.repfinder.server.MethodDeclarationVisitor;
import org.eclipse.jdt.core.dom.*;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

/**
 * @author huangkaigfeng
 * @Date 2021-02-19
 */
public class JarAnalysisUtil {


    public static NewMethodBean splitMethod(String methodRaw){
        String [] data = methodRaw.split("__fdse__");
        String returnFull = data[0];
        String method = data[1];
        int indexret = returnFull.lastIndexOf(".");
        String returnName = returnFull;
        if(indexret!=-1) {
            returnName = returnFull.substring(indexret+1);
        }
        int index = method.indexOf("(");
        if(index == -1){
            // field
            index = method.lastIndexOf(".");
            String prefixField = method.substring(0,index);
            String fieldName = method.substring(index+1);
            int index2 = prefixField.lastIndexOf(".");
            String classFieldName = prefixField.substring(index2+1);
            String packFieldName = prefixField.substring(0,index2);
            NewMethodBean methodBean = new NewMethodBean();
            methodBean.setPackageName(packFieldName);
            methodBean.setClassName(classFieldName);
            methodBean.setMethodName(fieldName);
            methodBean.setReturnType(returnName);
            methodBean.setMethodSignatureWithoutPackAndClassName(fieldName);
            methodBean.setMethodSignatureWithPackAndClassName(method);
            return methodBean;
        }
        String prefix = method.substring(0,index);
        int dotIndex = prefix.lastIndexOf(".");
        String packageAndClass = prefix.substring(0,dotIndex);
        int dotIndex2 = packageAndClass.lastIndexOf(".");
        String packageName = packageAndClass.substring(0,dotIndex2);
        String className = packageAndClass.substring(dotIndex2+1);
        String methodName = method.substring(dotIndex+1,index);
        String methodParams = method.substring(index+1,method.length()-1);
        NewMethodBean methodBean = new NewMethodBean();
        methodBean.setPackageName(packageName);
        methodBean.setClassName(className);
        methodBean.setMethodName(methodName);
        methodBean.setReturnType(returnName);
        if(methodParams.equals("")){
            methodBean.setMethodSignatureWithoutPackAndClassName(method.substring(dotIndex+1));
            methodBean.setMethodSignatureWithPackAndClassName(method);
            return methodBean;

        }
        String[] params = methodParams.split(",");
        for(String pa:params){
            methodBean.addParam(pa);
        }
        methodBean.setMethodSignatureWithoutPackAndClassName(method.substring(dotIndex+1));
        methodBean.setMethodSignatureWithPackAndClassName(method);

        return methodBean;
    }


    /**
     * 设置v0版本method 的临近method
     *
     * @param newMethodBean
     * @param v0Path
     * @param cuV0
     */
    public static void setMethodSibsInfo(NewMethodBean newMethodBean, String v0Path, CompilationUnit cuV0){
        String classPath = v0Path + newMethodBean.getClassPath() + ".java";
        String packageName = "";
        if(cuV0.getPackage() != null){
            packageName = cuV0.getPackage().getName().toString();
        }
        MethodDeclarationVisitor vis = new MethodDeclarationVisitor(packageName,null,MethodDeclarationVisitor.FULL_MATCH);
        cuV0.accept(vis);
        List<MethodDeclaration> mds = vis.declarationList;
        List<String> sibs = new ArrayList<>();
        for(MethodDeclaration md : mds){
            String mdString = vis.getMethodNameWithoutPackageAndClass(md);
            sibs.add(mdString);
        }
        newMethodBean.sibMethods = sibs;
    }

    /***
     * 设置类的super class
     * 一种情况是 类存在，那么super class为v1的类的super class名
     * 一种情况是 类不存在, 那么super class 需要从v0 的super class找到
     * @param newMethodBean
     * @param cu
     * @param prefix
     * @param vXFiles
     */
    public static void setSuperClassInfo(NewMethodBean newMethodBean, CompilationUnit cu, String prefix, List<File> vXFiles){
        List imports = cu.imports();
        List types = cu.types();
        if(!(types.get(0) instanceof TypeDeclaration)) {
            return;
        }
        int shouldFindSuper = 0;//default
        TypeDeclaration typeDeclaration = (TypeDeclaration) types.get(0);
        Type sType = typeDeclaration.getSuperclassType();
        if(sType != null) {
            String s = sType.toString();
            int index = s.indexOf("<");
            if (index != -1) {
                String varArgsStr = s.substring(index+1,s.length()-1);
                s = s.substring(0, index);
                newMethodBean.setSuperClassTemplateArgs(varArgsStr);
            }
            newMethodBean.setSuperClassName(s);
            for (File f : vXFiles) {
                if (f.getName().equals(s + ".java")) {
                    String full = f.getAbsolutePath();
                    String shortPath = full.replace(prefix, "");
                    newMethodBean.setSuperClassPath(shortPath);
                    shouldFindSuper = 1; //find in local
                    break;
                }
            }
            //

            if(newMethodBean.getSuperClassPath() == null){
                //
                shouldFindSuper = 2; // find in third party
//                methodBean.isSuperClassOrInterfaceThirdParty = true;
                String packagePath = getSuperClassPathFromImports(imports,newMethodBean.getSuperClassName());
                if(packagePath != null){
                    newMethodBean.setSuperClassPath(packagePath);
                }
            }
        }
        int shouldFindInterface = 0;
        List li = typeDeclaration.superInterfaceTypes();
        boolean haveInterfaceDeclaration = false;
        if(li !=null && li.size()!=0){
            haveInterfaceDeclaration = true;
        }
        for(Object o:li){
            if(o instanceof SimpleType){
                SimpleType st = (SimpleType) o;
                String interfaceName = st.getName().toString();
                for (File f : vXFiles) {
                    if (f.getName().equals(interfaceName + ".java")) {
                        String full = f.getAbsolutePath();
                        String shortPath = full.replace(prefix, "");
                        newMethodBean.superInterfaceNameAndPath.put(interfaceName,shortPath);
                        shouldFindInterface = 1; //find in local
                        break;
                    }
                }
            }else if(o instanceof ParameterizedType){
                ParameterizedType pt = (ParameterizedType)o;
                String interfaceName = pt.getType().toString();
                for (File f : vXFiles) {
                    if (f.getName().equals(interfaceName + ".java")) {
                        String full = f.getAbsolutePath();
                        String shortPath = full.replace(prefix, "");
                        newMethodBean.superInterfaceNameAndPath.put(interfaceName,shortPath);
                        shouldFindInterface = 1; //find in local
                        break;
                    }
                }
            }

        }

        if(haveInterfaceDeclaration && newMethodBean.superInterfaceNameAndPath.size() ==0){
//            methodBean.isSuperClassOrInterfaceThirdParty = true;
            shouldFindInterface = 2; // find in third party
            for(Object o:li){
                if(o instanceof SimpleType){
                    SimpleType st = (SimpleType) o;
                    String interfaceName = st.getName().toString();
                    String interfacePath = getSuperClassPathFromImports(imports,interfaceName);
                    if(interfacePath !=null){
                        newMethodBean.superInterfaceNameAndPath.put(interfaceName,interfacePath);
                    }
                }

            }
        }

        newMethodBean.isSuperClassOrInterfaceThirdParty = setStatus(shouldFindSuper,shouldFindInterface);


    }

    /**
     * status: 1. 只有local 2. local 和remote 3. 只有remote 4. 没有
     * @param shouldFindSuper
     * @param shouldFindInterface
     * @return
     */
    private static int setStatus(int shouldFindSuper, int shouldFindInterface){
        int sta;
        if(shouldFindSuper ==0 && shouldFindInterface == 0){
            sta = 4;//无
            return sta;
        }
        if((shouldFindSuper == 1 && shouldFindInterface == 0)|| (shouldFindSuper == 0 && shouldFindInterface == 1)){
            sta = 1;//只有local
            return sta;
        }

        if((shouldFindSuper == 2  && shouldFindInterface == 1)|| (shouldFindSuper == 1  && shouldFindInterface == 2)){
            sta = 2;//有local and remote
            return sta;
        }

        if((shouldFindSuper == 2  && shouldFindInterface == 0)|| (shouldFindSuper == 0  && shouldFindInterface == 2)){
            sta = 3;// remote
            return sta;
        }

        if(shouldFindSuper == 2  && shouldFindInterface == 2){
            sta = 3;// remote
            return sta;
        }
        if(shouldFindSuper == 1  && shouldFindInterface == 1){
            sta = 1;// local
            return sta;
        }

        return 0;
    }

    private static String getSuperClassPathFromImports(List imports,String superClassName){

        for(Object object :imports) {
            ImportDeclaration importDeclaration = (ImportDeclaration) object;
            String name = importDeclaration.getName().toString();
            String[] data = name.split("\\.");
            String suffix = data[data.length - 1];
            if (superClassName.startsWith(suffix)&&superClassName.length()> suffix.length() && superClassName.charAt(suffix.length()) == '.'){
                String[]tmpData = superClassName.split("\\.");
                StringBuilder sb = new StringBuilder(name.replace(".","/"));
                sb.append(".");
                for(int i=1;i<tmpData.length;i++) {
                    sb.append(tmpData[i]);
                    sb.append(".");
                }
                sb.deleteCharAt(sb.length()-1);
                return sb.toString();
        }
            if(suffix.equals(superClassName)){
                return name.replace(".","/");
            }
        }
        return null;
    }

    public static boolean ifPathExists(String path){
        File f = new File(path);
        return f.exists();
    }
}
