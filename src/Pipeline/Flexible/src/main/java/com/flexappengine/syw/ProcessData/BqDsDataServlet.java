package com.flexappengine.syw.ProcessData;

import static com.google.datastore.v1.client.DatastoreHelper.makeKey;
import static com.google.datastore.v1.client.DatastoreHelper.makeValue;

import java.io.IOException;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.api.services.bigquery.model.TableRow;
import com.google.cloud.dataflow.sdk.Pipeline;
import com.google.cloud.dataflow.sdk.io.BigQueryIO;
import com.google.cloud.dataflow.sdk.io.datastore.DatastoreIO;
import com.google.cloud.dataflow.sdk.options.DataflowPipelineOptions;
import com.google.cloud.dataflow.sdk.options.Default;
import com.google.cloud.dataflow.sdk.options.PipelineOptionsFactory;
import com.google.cloud.dataflow.sdk.runners.DataflowPipelineRunner;
import com.google.cloud.dataflow.sdk.transforms.DoFn;
import com.google.cloud.dataflow.sdk.transforms.ParDo;
import com.google.cloud.dataflow.sdk.values.PCollection;
import com.google.datastore.v1.Entity;
import com.google.datastore.v1.Key;

@SuppressWarnings("serial")
public class BqDsDataServlet extends HttpServlet {
	static final Logger Log = LoggerFactory.getLogger(BqDsDataServlet.class.getName());
	private static final String PIPELINE_PROJECT_ID = "syw-offers";
	private static final String STAGING_LOCATION = "gs://bq-ds-dataflow-staging";
	private static final String TEMP_LOCATION = "gs://bq-ds-dataflow-temp";		

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


	public static class SplitLineDataTask extends DoFn<TableRow, Entity> {
		private static final long serialVersionUID = 1L;

		public Entity makeEntity(TableRow content) {
			Entity.Builder entityBuilder = Entity.newBuilder();
			Key.Builder keyBuilder = makeKey("MemberEmailOptInStatusData", (String)content.get("lyl_id_no"));
			keyBuilder.getPartitionIdBuilder().setNamespaceId("dev");
			entityBuilder.setKey(keyBuilder.build());

			String lyl_id_no = (String) content.get("lyl_id_no");
			lyl_id_no = (lyl_id_no == null)?"":lyl_id_no;

			String eml_opt_in = (String) content.get("eml_opt_in");
			eml_opt_in = (eml_opt_in == null)?"":eml_opt_in;

			String sends = (String) content.get("sends");
			sends = (sends == null)?"":sends;

			String opens = (String) content.get("opens");
			opens = (opens == null)?"":opens;

			entityBuilder.getMutableProperties().put("lyl_id_no", makeValue(lyl_id_no).build());
			entityBuilder.getMutableProperties().put("eml_opt_in", makeValue(eml_opt_in).build());
			entityBuilder.getMutableProperties().put("sends", makeValue(sends).build());
			entityBuilder.getMutableProperties().put("opens", makeValue(opens).build());
			return entityBuilder.build();
		}

		@Override
		public void processElement(ProcessContext c) {
			TableRow row = c.element();
			Log.info((String) row.get("lyl_id_no"));
			c.output(makeEntity(row));
		}
	}

	public static void getMemberEmailData(){
		Log.info("Start BigQuery dataflow");

		String query = "select b.b.lyl_id_no, b.eml_opt_in, a.sends, a.opens from (select a.eml_ad_id, "
				+ "count(distinct case when a.eml_cnt_cd = 'S' then a.cpg_id end) as sends, count(distinct case when a.eml_cnt_cd in ('O','C') then "
				+ "a.cpg_id end) as opens  from `syw-analytics-repo-prod.lci_dw_tbls.eml_rsp_cpg_comm` a "
				+ "where a._partitiontime between cast('2016-12-20' as timestamp) and cast('2016-12-21' as timestamp)"
				+ " and a.ld_dt between a.cpg_sta_dt and date_add(a.cpg_sta_dt, interval 7 day) group by 1) a "
				+ "inner join (select b.lyl_id_no, b.eml_ad_id, max(b.eml_opt_in) as eml_opt_in "
				+ "from `syw-analytics-repo-prod.lci_loyal_views.sywr_email_id` b "
				+ "group by 1,2) b on a.eml_ad_id = b.eml_ad_id limit 10;";
		Log.info("Query: " + query);

		try {
			MyOptions options = PipelineOptionsFactory.as(MyOptions.class);
			options.setRunner(DataflowPipelineRunner.class);

			Pipeline bp = Pipeline.create(options);
			Log.info("BigQuery-DataStore pipeline created");
			PCollection<TableRow> BigQueryReadingCollection = bp
					.apply(BigQueryIO.Read.withoutValidation().usingStandardSql().fromQuery(query));
			PCollection<Entity> BigQueryTransformData = BigQueryReadingCollection
					.apply(ParDo.of(new SplitLineDataTask()));
			BigQueryTransformData.apply(DatastoreIO.v1().write().withProjectId(PIPELINE_PROJECT_ID));
			Log.info("BigQuery-DataStore pipeline to run now");
			bp.run();
			Log.info("Finished BigQuery-DataStore dataflow");
		} catch (Exception e) {
			Log.info("Exception: " + e.getMessage() + e.getStackTrace().toString());
		}
	}

	@Override
	public void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		getMemberEmailData();
	}

}
