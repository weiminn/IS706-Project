package edu.fdu.se.repfinder.net;

/**
 * 网络请求返回结果
 */
public class ResponseBean {
    public static final int OK = 200;

    int code;
    String response;

    public ResponseBean(int code, String response) {
        this.code = code;
        this.response = response;
    }

    public ResponseBean() {
    }

    public int getCode() {
        return code;
    }

    public void setCode(int code) {
        this.code = code;
    }

    public String getResponse() {
        return response;
    }

    public void setResponse(String response) {
        this.response = response;
    }
}
