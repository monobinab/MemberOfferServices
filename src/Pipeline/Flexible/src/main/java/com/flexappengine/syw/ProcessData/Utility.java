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

public class Utility{
	static final Logger Log = LoggerFactory.getLogger(Utility.class.getName());

	/**
	 * This method returns the configuration entity from datastore. 
	 */
	public Entity fetchDatastoreProperties(){
		String namespace = null;
		String env = getNamespace();

		Log.info("environment: " + env);

		if(null == env){
			namespace = "dev";
		}else{		
			switch(env) {
			case "prod" :
				namespace = "prod"; 
				break;
			case "qa" :
				namespace = "qa";
				break;
			default :
				namespace = "dev";
			}
		}

		Log.info("namespace: " + namespace);

		NamespaceManager.set(namespace);
		Key pubsubConfigKey = KeyFactory.createKey("ConfigData", "PubSubConfig");
		DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
		Entity PubSubConfigEntity = null;

		try {
			PubSubConfigEntity = datastore.get(pubsubConfigKey);
			return PubSubConfigEntity;
		}
		catch (Exception e)
		{
			Log.error("Entity not found in datastore. " +  e.getMessage());
			return PubSubConfigEntity;
		}

	}

	/**
	 * This method returns the namespace. 
	 */
	public String getNamespace(){
		String env = null;
		InputStream is = Utility.class.getClassLoader().getResourceAsStream("systemenvironment.properties");
		Properties props = new Properties();
		try {
			props.load(is);
			env = (String) props.get("env");
		} catch (IOException e1) {
			Log.error("Error getting namespace env: " + e1.getMessage());
		}

		return env;
	}
}