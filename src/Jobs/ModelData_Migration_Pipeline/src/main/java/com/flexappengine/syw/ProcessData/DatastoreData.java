package com.flexappengine.syw.ProcessData;

public class DatastoreData {
    private String modelToken;
    private String emailServiceEndpoint;
    private Boolean sendEmailFlag;
    private String queryLimit;
    private String sourceProjectId;

    public String getSourceProjectId() {
	return sourceProjectId;
    }

    public void setSourceProjectId(String sourceProjectId) {
	this.sourceProjectId = sourceProjectId;
    }

    public String getModelToken() {
	return modelToken;
    }

    public void setModelToken(String modelToken) {
	this.modelToken = modelToken;
    }

    public String getEmailServiceEndpoint() {
	return emailServiceEndpoint;
    }

    public void setEmailServiceEndpoint(String emailServiceEndpoint) {
	this.emailServiceEndpoint = emailServiceEndpoint;
    }

    public Boolean getSendEmailFlag() {
	return sendEmailFlag;
    }

    public void setSendEmailFlog(Boolean sendEmailFlag) {
	this.sendEmailFlag = sendEmailFlag;
    }

    public String getQueryLimit() {
	return queryLimit;
    }

    public void setQueryLimit(String queryLimit) {
	this.queryLimit = queryLimit;
    }

}