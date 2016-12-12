package com.flexappengine.syw.ProcessData;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

import com.google.appengine.api.NamespaceManager;
import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;
import com.google.appengine.api.datastore.Key;
import com.google.appengine.api.datastore.KeyFactory;

public class Utility{
	static final Logger Log = Logger.getLogger(Utility.class.getName());

	/**
	 * This method returns the configuration entity from datastore. 
	 */
	public Entity fetchDatastoreProperties(){
		String namespace = null;
		String env = null;
		InputStream is = Utility.class.getClassLoader().getResourceAsStream("systemenvironment.properties");
		Properties props = new Properties();
		try {
			props.load(is);
			env = (String) props.get("env");
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			Log.log(Level.SEVERE, e1.getMessage(), e1);
			e1.printStackTrace();
		}

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
			Log.info("Entity not found in datastore");
			Log.log(Level.SEVERE, e.getMessage(), e);
			return PubSubConfigEntity;
		}

	}
}