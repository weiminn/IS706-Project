package edu.fdu.se.repfinder.jardiff;

import com.google.gson.annotations.Expose;
import edu.fdu.se.repfinder.server.MethodBean;

import java.util.ArrayList;
import java.util.List;

public class ClassBean {

    /**
     * relative path
     */
    @Expose(serialize = true)
    private String fileSubPath;


    @Expose(serialize = true)
    private String className;

    @Expose(serialize = true)
    private List<MethodBean> methodBeans;

    @Expose(serialize = true)
    private List<FieldBean> fieldBeans;

    public String getFileSubPath() {
        return fileSubPath;
    }

    public ClassBean(){
        this.methodBeans = new ArrayList<>();
        this.fieldBeans = new ArrayList<>();
    }

    public void setFileSubPath(String fileSubPath) {
        this.fileSubPath = fileSubPath;
    }

    public String getClassName() {
        return className;
    }

    public void setClassName(String className) {
        this.className = className;
    }

    public List<MethodBean> getMethodBeans() {
        return methodBeans;
    }

    public List<FieldBean> getFieldBeans() {
        return fieldBeans;
    }
}
