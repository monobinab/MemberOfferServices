/*
 * Copyright (C) 2015 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */

package syw.member.dataflow;

import static com.google.datastore.v1.client.DatastoreHelper.makeKey;
import static com.google.datastore.v1.client.DatastoreHelper.makeValue;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

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
import com.google.cloud.dataflow.sdk.options.PipelineOptionsFactory;
import com.google.cloud.dataflow.sdk.runners.DataflowPipelineRunner;
import com.google.cloud.dataflow.sdk.transforms.DoFn;
import com.google.cloud.dataflow.sdk.transforms.ParDo;
import com.google.cloud.dataflow.sdk.transforms.DoFn.ProcessContext;
import com.google.cloud.dataflow.sdk.values.PCollection;
import com.google.datastore.v1.Entity;
import com.google.datastore.v1.Key;



@SuppressWarnings("serial")
public class MemberDataflowJob extends HttpServlet {
	static final Logger Log = LoggerFactory.getLogger(MemberDataflowJob.class.getName());
	private static final String PIPELINE_PROJECT_ID = "syw-offers";
	private static final String STAGING_LOCATION = "gs://member-dataflow-staging";
	private static final String NAMESPACE ="dev";
	private static final String DATE_FORMAT = "yyyy-MM-dd";

	public static class SplitLineDataTask extends DoFn<TableRow, Entity> {
		private static final long serialVersionUID = 1L;

		public Entity makeEntity(TableRow content) {
			Entity.Builder entityBuilder = Entity.newBuilder();
			Key.Builder keyBuilder = makeKey("MemberData", (String)content.get("member"));
			keyBuilder.getPartitionIdBuilder().setNamespaceId(NAMESPACE);
			entityBuilder.setKey(keyBuilder.build());

			String lyl_id_no = (String) content.get("member");
			lyl_id_no = (lyl_id_no == null)?"":lyl_id_no;

			String kmt_primary_store = (String) content.get("store");
			kmt_primary_store = (kmt_primary_store == null)?"":kmt_primary_store;

			String eml_opt_in = (String) content.get("eml_opt_in");
			eml_opt_in = (eml_opt_in == null)?"":eml_opt_in;

			Integer sends = Integer.valueOf((String) content.get("sends"));
			sends = (sends == null)?0:sends;

			Integer opens = Integer.valueOf((String)  content.get("opens"));
			opens = (opens == null)?0:opens;
			
			Calendar cal = Calendar.getInstance();
			Date today = cal.getTime();
		
			
			entityBuilder.getMutableProperties().put("member_id", makeValue(lyl_id_no).build());
			entityBuilder.getMutableProperties().put("eml_opt_in", makeValue(eml_opt_in).build());
			
			if (NAMESPACE.equals("dev")){
				entityBuilder.getMutableProperties().put("email", makeValue("testmember234@gmail.com").build());
			} else {
				entityBuilder.getMutableProperties().put("email", makeValue(email).build());
			}
			entityBuilder.getMutableProperties().put("first_name", makeValue("").build());
			entityBuilder.getMutableProperties().put("last_name", makeValue("").build());

			entityBuilder.getMutableProperties().put("format_level", makeValue("KMART").build());

			entityBuilder.getMutableProperties().put("store_id", makeValue(kmt_primary_store).build());

			entityBuilder.getMutableProperties().put("email_send", makeValue(sends).build());
			entityBuilder.getMutableProperties().put("email_open", makeValue(opens).build());
			entityBuilder.getMutableProperties().put("last_updated_at", makeValue(today).build());



			return entityBuilder.build();
		}

		@Override
		public void processElement(ProcessContext c) {
			TableRow row = c.element();
			Log.info((String) row.get("lyl_id_no"));
			c.output(makeEntity(row));
		}
	}

	public static void getMemberData(String txnStartDate, String txnEndDate, 
			String emlStartDate, String emlEndDate){
			Log.info("Start BigQuery dataflow");
		

		String query = "SELECT distinct d.Locn_Nbr AS store, d.lyl_id_no AS member, b.eml_ad_id AS email_ad_id, b.eml_opt_in, a.sends, a.opens, fst_nm, lst_nm"
				+ "FROM `syw-analytics-repo-prod.cbr_mart_tbls.eadp_kmart_pos_dtl` d"
				+ "inner join (select b.lyl_id_no, b.eml_ad_id,max(b.eml_opt_in) as eml_opt_in"
				+ "from `syw-analytics-repo-prod.lci_loyal_views.sywr_email_id` b"
				+ "group by 1,2) b  on d.lyl_id_no = b.lyl_id_no"
				+ "inner join (select a.eml_ad_id,"
				+ "count(distinct case when a.eml_cnt_cd = 'S' then a.cpg_id end) as sends,"
				+ "count(distinct case when a.eml_cnt_cd in ('O','C') then a.cpg_id end) as opens"
				+ "from `syw-analytics-repo-prod.lci_dw_tbls.eml_rsp_cpg_comm` a"
				+ "where" 
				+ "a._partitiontime between cast(current_date as timestamp)" 
				+ "and cast(DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR) as timestamp) and"
				+ "a.ld_dt between a.cpg_sta_dt and DATE_SUB(a.cpg_sta_dt, interval 7 day)"
				+ "group by 1) a on a.eml_ad_id = b.eml_ad_id"
				+ "inner join `syw-analytics-repo-prod.lci_loyal_nadr_views.sywr_mbr` mbr"
				+ "on mbr.lyl_id_no = d.lyl_id_no"
				+ "where"
					+ "d.lyl_id_no = b.lyl_id_no and"
					+ "d.lyl_id_no is not null and"
					+ "d.locn_nbr is not null and"
					+ "d.soar_no is not null and"
					+ "d.burn_amt is not null and"
				    + "d.sellqty is not null and"
				    + "d.kmt_sell is not null and"
				    + "d.md_amt is not null and"
				    + "d.day_dt between DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR) and cast(current_date as date) and"
				    + "d.locn_nbr in (9524, 3418)"
				    ;


		Log.info("Query: " + query);

		try {

			// Create and set your PipelineOptions.
			DataflowPipelineOptions options = PipelineOptionsFactory.as(DataflowPipelineOptions.class);

			// For Cloud execution, set the Cloud Platform project, staging location,
			// and specify DataflowPipelineRunner or BlockingDataflowPipelineRunner.
			options.setProject(PIPELINE_PROJECT_ID);
			options.setStagingLocation(STAGING_LOCATION);
			options.setRunner(DataflowPipelineRunner.class);

			Pipeline bp = Pipeline.create(options);

			//			Pipeline bp = Pipeline.create(PipelineOptionsFactory.fromArgs(args).withValidation().create());

			Log.info("BigQuery-DataStore pipeline created");
			PCollection<TableRow> BigQueryReadingCollection = bp
					//					.apply(BigQueryIO.Read.withoutValidation().fromQuery(query));
					.apply(BigQueryIO.Read.withoutValidation().usingStandardSql().fromQuery(query));
			PCollection<Entity> BigQueryTransformData = BigQueryReadingCollection
					.apply(ParDo.of(new SplitLineDataTask()));
			BigQueryTransformData.apply(DatastoreIO.v1().write().withProjectId(PIPELINE_PROJECT_ID));
			Log.info("BigQuery-DataStore pipeline to run now");
			bp.run();
			Log.info("Finished BigQuery-DataStore dataflow");
		} 
		catch (Exception e) {
			Log.info("Exception: " + e.getMessage() + e.getStackTrace().toString());
			}
		}
	
	public static void main(String[] args){
		getMemberDataFromToday();
	}
		
		
	public static void getMemberDataFromToday(){
		Calendar cal = Calendar.getInstance();
		Date today = cal.getTime();
		cal.add(Calendar.YEAR, -1); 
		Date lastYear = cal.getTime();
		cal.add(Calendar.MONTH, 6);
		Date emailStartDate = cal.getTime(); 
		String txnEndDate = new SimpleDateFormat(DATE_FORMAT).format(today);
		String txnStartDate = new SimpleDateFormat(DATE_FORMAT).format(lastYear);
		String emlStartDate = new SimpleDateFormat(DATE_FORMAT).format(emailStartDate);
		getMemberData(txnStartDate, txnEndDate, emlStartDate, txnEndDate);
		
	}

	@Override
	public void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		String txnStartDate = req.getParameter("startDate");
		String txnEndDate = req.getParameter("endDate");
		String emailStartDate = req.getParameter("emailStartDate");
		String emailEndDate = req.getParameter("emailEndDate");

		if (txnStartDate == null || txnEndDate == null || emailStartDate == null || emailEndDate == null){
			getMemberDataFromToday();		}else{
			getMemberData(txnStartDate, txnEndDate, emailStartDate, emailEndDate);
		}

	}
}
