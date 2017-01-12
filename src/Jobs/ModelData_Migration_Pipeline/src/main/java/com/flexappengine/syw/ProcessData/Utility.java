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

		String sourceProject = null;
		InputStream is = Utility.class.getClassLoader().getResourceAsStream("systemenvironment.properties");
		Properties props = new Properties();
		try {
		    props.load(is);
		    sourceProject = (String) props.get("sourceProject");

		    if (sourceProject.equalsIgnoreCase("${project.sourceProject}")) {
			sourceProject = null;
		    }
		} catch (IOException e1) {
		    Log.error("Error getting sourceProject: " + e1.getMessage());
		}
		dData.setSourceProjectId(sourceProject);
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

	switch (env == null ? "" : env) {
	case "prod":
	    namespace = "prod";
	    break;
	case "qa":
	    namespace = "qa";
	    break;
	default:
	    namespace = "dev";
	}

	return namespace;
    }
}