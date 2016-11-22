package com.flexappengine.syw.ProcessData;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;
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
import com.google.cloud.dataflow.sdk.options.DataflowPipelineOptions;
import com.google.cloud.dataflow.sdk.options.Default;
import com.google.cloud.dataflow.sdk.options.PipelineOptionsFactory;
import com.google.cloud.dataflow.sdk.runners.DataflowPipelineRunner;
import com.google.cloud.dataflow.sdk.runners.DirectPipelineRunner;
import com.google.cloud.dataflow.sdk.transforms.Aggregator;
import com.google.cloud.dataflow.sdk.transforms.DoFn;
import com.google.cloud.dataflow.sdk.transforms.ParDo;
import com.google.cloud.dataflow.sdk.transforms.Sum;
import com.google.cloud.dataflow.sdk.values.PCollection;
import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;
import com.google.appengine.api.datastore.Key;
import com.google.appengine.api.datastore.KeyFactory;
import com.google.appengine.repackaged.com.google.api.client.util.Strings;


@SuppressWarnings("serial")
public class ProcessModelDataServlet extends HttpServlet {
	static final Logger Log = Logger.getLogger(ProcessModelDataServlet.class.getName());
	private static final String PIPELINE_PROJECT_ID = "syw-offers";
	private static final String STAGING_LOCATION = "gs://dataflowpipeline-staging";
	private static final String TEMP_LOCATION = "gs://dataflowpipeline-temp";

	@Override
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

			// Validating unique subscription token before processing the message
			if(null != messageJsonObject && !messageJsonObject.isEmpty()){
				token = (String) messageJsonObject.get("token");
				Log.info("Token received: " + token);

				if (!subscriptionToken.equals(token)) {
					Log.info("Invalid token");
					// Return SC_OK to acknowledge PubSub otherwise it will keep retrying till the request succeeds
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
			// TODO Auto-generated catch block
			Log.log(Level.SEVERE, e.getMessage(), e);
		}

		PrintWriter out = resp.getWriter();
		Log.info("campaignName received: " + campaignName + " , projectId received: " + projectId + " , datasetId received: " + datasetId + " , tableId received: " + tableId);

		if(!Strings.isNullOrEmpty(campaignName) && !Strings.isNullOrEmpty(projectId) &&
				!Strings.isNullOrEmpty(datasetId) && !Strings.isNullOrEmpty(tableId)){
			BigQueryPipeline(campaignName, projectId, datasetId, tableId);
			Log.info("Returned from BigQuery dataflow");
		}else{
			// Return SC_OK to acknowledge PubSub otherwise it will keep retrying till the request succeeds
			Log.info("Please provide all the data entities: Token, Campaign name, Project Id, Dataset Id and Table Id");
			out.println("Please provide all the data entities: Token, Campaign name, Project Id, Dataset Id and Table Id");
			resp.setStatus(HttpServletResponse.SC_OK);
			resp.getWriter().close();
			return;
		}

		out.println("Campaign Name - " + campaignName);
		resp.setStatus(HttpServletResponse.SC_OK);
		resp.getWriter().close();
	}

	// HTTP GET request to email sending service
	public static String sendGet(String member, String offer, String campaign, String endpoint) throws Exception {
		Log.info("sending GET request");
		Log.info("Endpoint: " + endpoint);
		String url = endpoint + "member_id=" + member + "&&offer_value=" + offer + "&&campaign_name=" + campaign;
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection)obj.openConnection();
		Log.info("\nSending 'GET' request to URL : " + url);

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

		Log.info("GET response: " + response.toString());
		Log.info("GET sendGet completed for  member: " + member + " ,  offer: " + offer + " ,  campaign:  " + campaign);
		return response.toString();
	}

	public static class SplitLineDataTask extends DoFn<TableRow, String[]> {
		private final ArrayList<String> offersProcessed = new ArrayList<String>();
		private final Aggregator<Long, Long> successEmailSend =
				createAggregator("successEmailSend", new Sum.SumLongFn());
		private final Aggregator<Long, Long> failEmailSend =
				createAggregator("failEmailSend", new Sum.SumLongFn());
		private final Aggregator<Long, Long> tableRowCount =
				createAggregator("tableRowCount", new Sum.SumLongFn());
		private final ArrayList<String> fetchedEndpoint = new ArrayList<String>();

		public SplitLineDataTask(){
			// Reading service endpoint from datastore to call for sending emails
			Key pubsubConfigKey = KeyFactory.createKey("ConfigData", "PubSubConfig");
			DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
			Entity emailServiceEndpointEntity;

			try {
				emailServiceEndpointEntity = datastore.get(pubsubConfigKey);
				String emailServiceEndpoint = (String)emailServiceEndpointEntity.getProperty("EMAIL_SERVICE_ENDPOINT");
				fetchedEndpoint.add(emailServiceEndpoint);
			}
			catch (Exception e)
			{
				Log.info("emailServiceEndpoint not found in datastore");
				Log.log(Level.SEVERE, e.getMessage(), e);
				return;
			}
			Log.info("Fetched Endpoint from datastore: " + fetchedEndpoint.get(0));
		}

		@Override
		public void processElement(ProcessContext c){
			String sendEmailResponse = "";
			TableRow row = c.element();

			// Fetch member id, offer value from the row
			String memberId = (String)row.get("Member");
			String offerValue = (String)row.get("Offer");
			String campaignName = (String)row.get("Campaign");

			String [] outArray = new String[2];
			outArray[0] = memberId;
			outArray[1] = offerValue;

			Log.info("campaignName: " + campaignName + " ,   memberId: " + memberId + " ,  offerValue: " + offerValue);

			// Call for sending email
			if(null != campaignName && !campaignName.isEmpty() && null != memberId && !memberId.isEmpty() &&
					null != offerValue && !offerValue.isEmpty()){
				tableRowCount.addValue(1L);

				Log.info("Calling python service for sending email for member: " + memberId + "  , offer: " + offerValue + " ,  campaign:  " + campaignName);
				try {
					Log.info("processElement fetched Endpoint from constructor: " + fetchedEndpoint.get(0));
					sendEmailResponse = sendGet(memberId, offerValue, campaignName, fetchedEndpoint.get(0));
					offersProcessed.add(memberId+"_" + offerValue);
					Log.info("Returned from python service for sending email for member: " + memberId + " ,  offer: " + offerValue + " ,  campaign:  " + campaignName);
				} catch (Exception e) {
					// TODO Auto-generated catch block
					Log.info("Error Returned from python service for sending email for member: " + memberId + "  , offer: " + offerValue + " ,  campaign:  " + campaignName);
					Log.log(Level.SEVERE, e.getMessage(), e);
				}
			}

			Log.info("sendEmailResponse: " + sendEmailResponse);
			if(sendEmailResponse.equalsIgnoreCase("Success")){
				successEmailSend.addValue(1L);
				Log.info("Email sending Success for memberId: " + memberId + " ,  offerValue: " + offerValue);
			}else{
				failEmailSend.addValue(1L);
				Log.info("Email sending Fail for memberId: " + memberId + " ,  offerValue: " + offerValue);
			}
			c.output(outArray);
		}
	}

	/* Custom pipeline option class. */
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

	public void BigQueryPipeline(String campaignName, String projectId, String datasetId, String tableId){
		Log.info("Start BigQuery dataflow");

		String inputTable = projectId + ":" + datasetId + "." + tableId;
		MyOptions bigOptions = PipelineOptionsFactory.as(MyOptions.class);
		bigOptions.setRunner(DataflowPipelineRunner.class);

		String query = "SELECT Campaign_Name as Campaign, LYL_ID_NO as Member, ofr_val as Offer FROM [" + inputTable + "] where Campaign_Name = \'" + campaignName + "\'";

		Log.info("Input table: " + inputTable + ", Input getStagingLocation: " + bigOptions.getStagingLocation());
		Log.info("Input getTempLocation: " + bigOptions.getTempLocation() + " , Input getProject: " + bigOptions.getProject());
		Log.info("Query: " + query);

		try{
			Pipeline bp = Pipeline.create(bigOptions);
			Log.info("BigQuery pipeline created");
			PCollection<TableRow> BigQueryReadingCollection = bp.apply(BigQueryIO.Read.withoutValidation().withoutValidation().fromQuery(query));
			PCollection<String[]> BigQueryProcessingCollection = BigQueryReadingCollection.apply(ParDo.of(new SplitLineDataTask()));
			Log.info("BigQuery pipeline to run now");
			bp.run();
			Log.info("Initiated BigQuery dataflow");
		}
		catch (Exception e) {
			Log.info("Exception: " + e.getMessage());
			Log.log(Level.SEVERE, e.getMessage(), e);
		}
	}
}
