package com.flexappengine.syw.ProcessData;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.appengine.api.NamespaceManager;
import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;
import com.google.appengine.api.datastore.Key;
import com.google.appengine.api.datastore.KeyFactory;
import com.google.cloud.dataflow.sdk.repackaged.com.google.common.base.Strings;

public class Utility {
    static final Logger Log = LoggerFactory.getLogger(Utility.class.getName());

    /**
     * This method returns the configuration entity from datastore.
     */
    public DatastoreData fetchDatastoreProperties() {
	String namespace = getNamespace();
	Log.info("namespace: " + namespace);

	NamespaceManager.set(namespace);
	Key datastoreConfigKey = KeyFactory.createKey("ConfigData", "DataflowConfig");
	DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
	Entity DataflowConfigEntity = null;
	DatastoreData dData = null;

	try {
	    DataflowConfigEntity = datastore.get(datastoreConfigKey);
	    if (null != DataflowConfigEntity) {
		dData = new DatastoreData();
		dData.setEmailServiceEndpoint((String) DataflowConfigEntity.getProperty("EMAIL_SERVICE_ENDPOINT"));
		dData.setModelToken((String) DataflowConfigEntity.getProperty("MODEL_TOKEN"));
		dData.setQueryLimit((String) DataflowConfigEntity.getProperty("QUERY_LIMIT"));
		dData.setSendEmailFlog((Boolean) DataflowConfigEntity.getProperty("SEND_EMAIL_FLAG"));
		dData.setSendEmailFlog((Boolean) DataflowConfigEntity.getProperty("SEND_EMAIL_FLAG"));
		dData.setSourceProjectId((String) DataflowConfigEntity.getProperty("SOURCE_PROJECT_ID"));
	    }

	    return dData;
	} catch (Exception e) {
	    Log.error("Entity not found in datastore. " + e.getMessage());
	    return dData;
	}
    }

    /**
     * This method returns the namespace.
     */
    public String getNamespace() {
	String namespace = null;
	String env = null;
	InputStream is = Utility.class.getClassLoader().getResourceAsStream("systemenvironment.properties");
	Properties props = new Properties();
	try {
	    props.load(is);
	    env = (String) props.get("env");
	} catch (IOException e1) {
	    Log.error("Error getting namespace env: " + e1.getMessage());
	}

	Log.info("environment: " + env);

	if (Strings.isNullOrEmpty(env) || env.equalsIgnoreCase("${project.env}")) {
	    namespace = "dev";
	} else {
	    namespace = env;
	}

	return namespace;
    }
}