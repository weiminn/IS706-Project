package edu.fdu.se.repfinder.jardiff;

import com.google.gson.annotations.Expose;


public class FieldBean {

    @Expose(serialize = true)
    private String fieldName;

    @Expose(serialize = true)
    private String fieldHash;

    @Expose(serialize = true)
    private String fieldType;

    public String getFieldName() {
        return fieldName;
    }

    public void setFieldName(String fieldName) {
        this.fieldName = fieldName;
    }

    public String getFieldHash() {
        return fieldHash;
    }

    public void setFieldHash(String fieldHash) {
        this.fieldHash = fieldHash;
    }

    public String getFieldType() {
        return fieldType;
    }

    public void setFieldType(String fieldType) {
        this.fieldType = fieldType;
    }
}
