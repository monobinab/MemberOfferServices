package com.flexappengine.syw.ProcessData;

import static com.google.datastore.v1.client.DatastoreHelper.makeKey;
import static com.google.datastore.v1.client.DatastoreHelper.makeValue;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.TimeZone;
import javax.servlet.ServletInputStream;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import com.google.api.client.json.JsonParser;
import com.google.api.client.json.jackson2.JacksonFactory;
import com.google.api.services.bigquery.model.TableRow;
import com.google.api.services.pubsub.model.PubsubMessage;
import com.google.cloud.dataflow.sdk.Pipeline;
import com.google.cloud.dataflow.sdk.io.BigQueryIO;
import com.google.cloud.dataflow.sdk.io.datastore.DatastoreIO;
import com.google.cloud.dataflow.sdk.options.DataflowPipelineOptions;
import com.google.cloud.dataflow.sdk.options.Default;
import com.google.cloud.dataflow.sdk.options.PipelineOptionsFactory;
import com.google.cloud.dataflow.sdk.runners.DataflowPipelineRunner;
import com.google.cloud.dataflow.sdk.runners.DirectPipelineRunner;
import com.google.cloud.dataflow.sdk.transforms.Aggregator;
import com.google.cloud.dataflow.sdk.transforms.DoFn;
import com.google.cloud.dataflow.sdk.transforms.PTransform;
import com.google.cloud.dataflow.sdk.transforms.ParDo;
import com.google.cloud.dataflow.sdk.transforms.Sum;
import com.google.cloud.dataflow.sdk.transforms.DoFn.ProcessContext;
import com.google.cloud.dataflow.sdk.values.PCollection;
import com.google.datastore.v1.Value;
import com.google.appengine.repackaged.com.google.api.client.util.Strings;
import com.flexappengine.syw.ProcessData.Utility;
import com.google.datastore.v1.Entity;
import com.google.datastore.v1.Key;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("serial")
public class ProcessModelDataServlet extends HttpServlet {
	static final Logger Log = LoggerFactory.getLogger(ProcessModelDataServlet.class.getName());
	private static final String PIPELINE_PROJECT_ID = "syw-offers";
	private static final String STAGING_LOCATION = "gs://dataflowpipeline-staging";
	private static final String TEMP_LOCATION = "gs://dataflowpipeline-temp";

	@Override
	/**
	 * Method to accept the POST request, fetch relevant data nodes from the request body and call method to run dataflow pipeline.
	 */
	public void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		Log.info("PubSub message received in doPost");
		String subscriptionToken = "ModelClient";
		String campaignName = null;
		String projectId = null;
		String datasetId = null;
		String tableId = null;
		String token = null;

		ServletInputStream inputStream = req.getInputStream();
		JsonParser parser = JacksonFactory.getDefaultInstance()
				.createJsonParser(inputStream);
		parser.skipToKey("message");
		PubsubMessage message = parser.parseAndClose(PubsubMessage.class);

		Log.info("message received: " + new String(message.decodeData(), "UTF-8"));

		String messageString = new String(message.decodeData(), "UTF-8");
		JSONParser parser2 = new JSONParser();
		Object obj;
		try {
			obj = parser2.parse(messageString);
			JSONObject jsonObject = (JSONObject) obj;
			JSONObject messageJsonObject = (JSONObject) jsonObject.get("message");

			/** Validating unique subscription token before processing the message */
			if(null != messageJsonObject && !messageJsonObject.isEmpty()){
				token = (String) messageJsonObject.get("token");
				Log.info("Token received: " + token);

				/** Return SC_OK to acknowledge PubSub otherwise it will retry till the request succeeds */
				if (!subscriptionToken.equals(token)) {
					Log.warn("Invalid token");
					resp.setStatus(HttpServletResponse.SC_OK);
					resp.getWriter().write("Invalid token");
					resp.getWriter().close();
					return;
				}
				campaignName = (String)messageJsonObject.get("campaign_name");
				projectId = (String)messageJsonObject.get("project_id");
				datasetId = (String)messageJsonObject.get("dataset_id");
				tableId = (String)messageJsonObject.get("table_id");
			}
		} catch (ParseException e) {
			Log.error("Error: " + e.getMessage());
		}

		PrintWriter out = resp.getWriter();
		Log.info("campaignName received: " + campaignName + " , projectId received: " + projectId + " , datasetId received: " + datasetId + " , tableId received: " + tableId);

		if(!Strings.isNullOrEmpty(campaignName) && !Strings.isNullOrEmpty(projectId) &&
				!Strings.isNullOrEmpty(datasetId) && !Strings.isNullOrEmpty(tableId)){
			BigQueryPipeline(campaignName, projectId, datasetId, tableId);
			Log.info("Returned from BigQuery dataflow");
		}else{
			/** Return SC_OK to acknowledge PubSub otherwise it will retry till the request succeeds */
			Log.warn("Please provide all the data entities: Token, Campaign name, Project Id, Dataset Id and Table Id");
			out.println("Please provide all the data entities: Token, Campaign name, Project Id, Dataset Id and Table Id");
			resp.setStatus(HttpServletResponse.SC_OK);
			resp.getWriter().close();
			return;
		}

		Log.info("Writing response for BigQuery dataflow now for Campaign Name - " + campaignName);
		out.println("Campaign Name - " + campaignName);
		resp.setStatus(HttpServletResponse.SC_OK);
		resp.getWriter().close();
	}

	/**
	 * Method to request email sending service.
	 */
	public static String sendGet(String member, String offer, String campaign, String endpoint) throws Exception {
		Log.info("sending GET request");
		Log.info("Endpoint: " + endpoint);
		String url = endpoint + "member_id=" + member + "&&offer_value=" + offer + "&&campaign_name=" + campaign;
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection)obj.openConnection();
		Log.info("Sending 'GET' request to URL : " + url);

		con.setRequestMethod("GET");
		//Adding request header
		con.setRequestProperty("User-Agent", "Mozilla/5.0");
		int responseCode = con.getResponseCode();
		Log.info("Response Code : " + responseCode);

		BufferedReader in = new BufferedReader(
				new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		while ((inputLine = in.readLine()) != null) {
			response.append(inputLine);
		}
		in.close();

		Log.info("GET response: " + response.toString() + " ; For  member: " + member + " ,  offer: " + offer + " ,  campaign:  " + campaign);
		return response.toString();
	}

	public static class SplitLineDataTask extends DoFn<TableRow, Entity> {
		private final ArrayList<String> offersProcessed = new ArrayList<String>();
		private final Aggregator<Long, Long> successEmailSend =
				createAggregator("successEmailSend", new Sum.SumLongFn());
		private final Aggregator<Long, Long> failEmailSend =
				createAggregator("failEmailSend", new Sum.SumLongFn());
		private final Aggregator<Long, Long> noEmailSend =
				createAggregator("noEmailSend", new Sum.SumLongFn());
		private final Aggregator<Long, Long> tableRowCount =
				createAggregator("tableRowCount", new Sum.SumLongFn());
		private final Aggregator<Long, Long> duplicateEntires =
				createAggregator("duplicateEntires", new Sum.SumLongFn());
		private final ArrayList<String> memberOfferEntityCreated = new ArrayList<String>();
		private String fetchedEndpoint;
		private Boolean sendEmailFlag;
		private String namespace;

		/**
		 * Constructor to fetch configuration data from datastore.
		 */
		public SplitLineDataTask(){
			Utility util = new Utility();
			com.google.appengine.api.datastore.Entity PubSubConfigEntity;

			try {
				PubSubConfigEntity = util.fetchDatastoreProperties();

				if(null != PubSubConfigEntity){
					this.fetchedEndpoint = (String)PubSubConfigEntity.getProperty("EMAIL_SERVICE_ENDPOINT");
					this.sendEmailFlag = (Boolean)PubSubConfigEntity.getProperty("SEND_EMAIL_FLAG");
					this.namespace = util.getNamespace();
				}
			}
			catch (Exception e) {
				Log.error("Error. EMAIL_SERVICE_ENDPOINT/SEND_EMAIL_FLAG not found in datastore : " + e.getMessage());
				this.fetchedEndpoint = null;
				this.sendEmailFlag = null;
				this.namespace = util.getNamespace();
			}
			Log.info("Fetched Endpoint from datastore: " + this.fetchedEndpoint);
			Log.info("Fetched sendEmailFlag from datastore: " + this.sendEmailFlag);
			Log.info("Fetched namespace: " + this.namespace);
		}

		@Override
		/**
		 * This method fetches relevant information from BigQuery row data, forms datastore entity and calls another service to send email.
		 */
		public void processElement(ProcessContext c){
			String sendEmailResponse = "";
			TableRow row = c.element();

			/** Fetch member id, offer value and campaign name from the row */
			String memberId = (String)row.get("Member");
			String offerValue = (String)row.get("Offer");
			String campaignName = (String)row.get("Campaign");

			Log.info("campaignName: " + campaignName + " ,   memberId: " + memberId + " ,  offerValue: " + offerValue);

			/** Check for the sendEmailFlag and endpoint to send emails.*/
			if(null == this.sendEmailFlag){
				Log.warn("Email sending flag is null. Can't determine if to send emails or not.");
				return;
			}else if(null == this.fetchedEndpoint && this.sendEmailFlag == true){
				Log.warn("Email sending Endpoint is null. Can't send emails.");
				return;
			}

			ModelData modelData = new ModelData();
			modelData.setCamapignName(campaignName);
			modelData.setMemberId(memberId);
			modelData.setOfferValue(offerValue);
			String keyName = modelData.getCamapignName() + "_" + modelData.getMemberId() + "_" + modelData.getOfferValue();
			SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd '('HH:mm:ss:SSS')' zzz");
			format.setTimeZone(TimeZone.getTimeZone("CST"));
			String currentDateTime = format.format(new Date());
			Log.info("Current Datetime: " + currentDateTime);

			/** Check for entries that are duplicate and have already been processed. No entity is output if duplicate found*/
			if(!memberOfferEntityCreated.contains(keyName)) {
				memberOfferEntityCreated.add(keyName);
			}else {
				duplicateEntires.addValue(1L);
				Log.warn("Key already exists and written in another entity:: " + keyName);
				return;
			}

			/** Create datastore entity. */
			Entity.Builder entityBuilder = Entity.newBuilder();
			Key pkey = makeKey("ModelDataTest1", keyName).build();
			entityBuilder.setKey(pkey);

			Map<String, Value> pProperties = new HashMap<String, Value>();
			pProperties.put("Campaign", makeValue(modelData.getCamapignName()).build());
			pProperties.put("Member", makeValue(modelData.getMemberId()).build());
			pProperties.put("Offer", makeValue(modelData.getOfferValue()).build());
			pProperties.put("created_at", makeValue(currentDateTime).setExcludeFromIndexes(true).build());
			entityBuilder.putAllProperties(pProperties);
			entityBuilder.getKeyBuilder().getPartitionIdBuilder().setNamespaceId(namespace);

			/** Call method for sending email */
			if(null != campaignName && !campaignName.isEmpty() && null != memberId && !memberId.isEmpty() &&
					null != offerValue && !offerValue.isEmpty()) {
				tableRowCount.addValue(1L);
				Log.info("this.sendEmailFlag: " + this.sendEmailFlag);

				/** If email sending flag is false then service is not called to send any email */
				if(null != this.sendEmailFlag && !this.sendEmailFlag) {
					noEmailSend.addValue(1L);
				}else{
					Log.info("Calling python service for sending email for member: " + memberId + "  , offer: " + offerValue + " ,  campaign:  " + campaignName);
					try {
						sendEmailResponse = sendGet(memberId, offerValue, campaignName, this.fetchedEndpoint);
						offersProcessed.add(memberId+"_" + offerValue);
						Log.info("Returned from python service for sending email for member: " + memberId + " ,  offer: " + offerValue + " ,  campaign:  " + campaignName);
						Log.info("sendEmailResponse for member: " + memberId + " is : " + sendEmailResponse);

						if(sendEmailResponse.equalsIgnoreCase("Success")){
							successEmailSend.addValue(1L);
							Log.info("Email sending Success for memberId: " + memberId + " ,  offerValue: " + offerValue);
						}else{
							failEmailSend.addValue(1L);
							Log.warn("Email sending Fail for memberId: " + memberId + " ,  offerValue: " + offerValue);
						}
					} catch (Exception e) {
						Log.error("Error while sending email for member: " + memberId + "  , offer: " + offerValue + " ,  campaign:  " + campaignName + " :: " + e.getMessage());
					}
				}
			}
			Log.info("Entity key: " + entityBuilder.getKey());
			c.output(entityBuilder.build());
		}
	}

	/* PTransform to process data fetched from BigQuery. */
	public static class BQDataTask extends PTransform<PCollection<TableRow>,
	PCollection<Entity>> {
		@Override
		public PCollection<Entity> apply(PCollection<TableRow> lines) {
			/* Converts row lines of data into entity object and sends email. */
			PCollection<Entity> entityCollection = lines.apply(
					ParDo.named("SplitLineDataTask").of(new SplitLineDataTask()));

			return entityCollection;
		}
	}

	/** Custom pipeline option class. */
	public static interface MyOptions extends DataflowPipelineOptions {
		@Default.String(PIPELINE_PROJECT_ID)
		String getProject();
		void setProject(String value);

		@Default.String(STAGING_LOCATION)
		String getStagingLocation();
		void setStagingLocation(String value);

		@Default.String(TEMP_LOCATION)
		String getTempLocation();
		void setTempLocation(String value);
	}

	/**
	 * This method creates the dataflow pipeline and initiates it using DataflowPipelineRunner in cloud.
	 *
	 * @param campaignName
	 * @param projectId
	 * @param datasetId
	 * @param tableId
	 */
	public void BigQueryPipeline(String campaignName, String projectId, String datasetId, String tableId){
		Log.info("Start BigQuery dataflow");

		String inputTable = projectId + ":" + datasetId + "." + tableId;
		MyOptions bigOptions = PipelineOptionsFactory.as(MyOptions.class);
		bigOptions.setRunner(DataflowPipelineRunner.class);

		/** Checking and setting limit configuration to be set for BigQuery query */
		Utility util = new Utility();
		String queryLimit = null;
		com.google.appengine.api.datastore.Entity PubSubConfigEntity;
		try {
			PubSubConfigEntity = util.fetchDatastoreProperties();

			if(null != PubSubConfigEntity){
				queryLimit = (String)PubSubConfigEntity.getProperty("QUERY_LIMIT");
			}
		}
		catch (Exception e) {
			Log.error("QUERY_LIMIT not found in datastore. Setting it to null" + e.getMessage());
			queryLimit = null;
		}

		String query = "SELECT Campaign_Name as Campaign, LYL_ID_NO as Member, ofr_val as Offer FROM [" + inputTable + "] where Campaign_Name = \'" + campaignName + "\'";

		if(!Strings.isNullOrEmpty(queryLimit)){
			query = query + " LIMIT " + queryLimit;
		}

		Log.info("Input table: " + inputTable + ", Input getStagingLocation: " + bigOptions.getStagingLocation());
		Log.info("Input getTempLocation: " + bigOptions.getTempLocation() + " , Input getProject: " + bigOptions.getProject());
		Log.info("Query: " + query);

		try {
			Pipeline bp = Pipeline.create(bigOptions);
			Log.info("BigQuery pipeline created");

			bp.apply(BigQueryIO.Read.withoutValidation().withoutValidation().fromQuery(query))
			.apply(new BQDataTask())
			.apply(DatastoreIO.v1().write().withProjectId(bigOptions.getProject()));

			Log.info("BigQuery pipeline to run now");
			bp.run();
			Log.info("Initiated BigQuery dataflow");
		}
		catch (Exception e) {
			Log.error("Exception: " + e.getMessage());
		}
	}
}
