/**
 * Copyright 2016 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package syw.mapping.dataflow;

import static com.google.datastore.v1.client.DatastoreHelper.makeKey;
import static com.google.datastore.v1.client.DatastoreHelper.makeValue;

import java.util.UUID;


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
import com.google.cloud.dataflow.sdk.values.PCollection;

import com.google.datastore.v1.Entity;
import com.google.datastore.v1.Key;

@SuppressWarnings("serial")
public class BUMappingDataflowJob {
	static final Logger Log = LoggerFactory.getLogger(BUMappingDataflowJob.class.getName());
	private static final String PIPELINE_PROJECT_ID = "syw-offers";
	private static final String STAGING_LOCATION = "gs://bu-mapping-dataflow-staging";

	public static class SplitLineDataTask extends DoFn<TableRow, Entity> {
		private static final long serialVersionUID = 1L;

		public Entity makeEntity(TableRow content) {
			
			Integer SOAR_NO = Integer.valueOf((String) content.get("SOAR_NO"));
			SOAR_NO = (SOAR_NO == null)?0:SOAR_NO;
			
			String SOAR_NM = (String) content.get("SOAR_NM");
			SOAR_NM = (SOAR_NM == null)?"":SOAR_NM;
			
			String FP_DVSN_DESC = (String) content.get("FP_DVSN_DESC");
			FP_DVSN_DESC = (FP_DVSN_DESC == null)?"":FP_DVSN_DESC;
			
			Integer BUS_NBR = Integer.valueOf((String) content.get("BUS_NBR"));
			BUS_NBR = (BUS_NBR == null)?0:BUS_NBR;
			
			Integer UNIT_NBR = Integer.valueOf((String) content.get("UNIT_NBR"));
			UNIT_NBR = (UNIT_NBR == null)?0:UNIT_NBR;
			
			Integer DVSN_NBR = Integer.valueOf((String) content.get("DVSN_NBR"));
			DVSN_NBR = (DVSN_NBR == null)?0:DVSN_NBR;
			
			Integer DEPT_NBR = Integer.valueOf((String) content.get("DEPT_NBR"));
			DEPT_NBR = (DEPT_NBR == null)?0:DEPT_NBR;
			
			Integer CATG_CLUSTER_NBR = Integer.valueOf((String) content.get("CATG_CLUSTER_NBR"));
			CATG_CLUSTER_NBR = (CATG_CLUSTER_NBR == null)?0:CATG_CLUSTER_NBR;
			
			Integer CATG_NBR = Integer.valueOf((String) content.get("CATG_NBR"));
			CATG_NBR = (CATG_NBR == null)?0:CATG_NBR;
			
			Integer SUB_CATG_NBR = Integer.valueOf((String) content.get("SUB_CATG_NBR"));
			SUB_CATG_NBR = (SUB_CATG_NBR == null)?0:SUB_CATG_NBR;
			
			String prod_heirarchy = "KMARTSHC~"+BUS_NBR+"~"+UNIT_NBR+"~"+DVSN_NBR+"~~~~~";
//			String key = "KMARTSHC-"+BUS_NBR+"-"+UNIT_NBR+"-"+DVSN_NBR;

			
			Entity.Builder entityBuilder = Entity.newBuilder();
			String uuid = UUID.randomUUID().toString();
			Key.Builder keyBuilder = makeKey("BuMappingData", uuid);
			keyBuilder.getPartitionIdBuilder().setNamespaceId("dev");
			entityBuilder.setKey(keyBuilder.build());
			
			entityBuilder.getMutableProperties().put("soar_no", makeValue(SOAR_NO).build());
			entityBuilder.getMutableProperties().put("soar_nm", makeValue(SOAR_NM).build());
			entityBuilder.getMutableProperties().put("fp_dvsn_desc", makeValue(FP_DVSN_DESC).build());

			entityBuilder.getMutableProperties().put("bus_nbr", makeValue(BUS_NBR).build());
			entityBuilder.getMutableProperties().put("unit_nbr", makeValue(UNIT_NBR).build());
			entityBuilder.getMutableProperties().put("dvsn_nbr", makeValue(DVSN_NBR).build());
			entityBuilder.getMutableProperties().put("dept_nbr", makeValue(DEPT_NBR).build());
			entityBuilder.getMutableProperties().put("catg_cluster_nbr", makeValue(CATG_CLUSTER_NBR).build());
			entityBuilder.getMutableProperties().put("catg_nbr", makeValue(CATG_NBR).build());
			entityBuilder.getMutableProperties().put("sub_catg_nbr", makeValue(SUB_CATG_NBR).build());

			entityBuilder.getMutableProperties().put("product_heirarchy", makeValue(prod_heirarchy).build());

			return entityBuilder.build();
		}

		@Override
		public void processElement(ProcessContext c) {
			TableRow row = c.element();
			Log.info((String) row.get("soar_no"));
			c.output(makeEntity(row));
		}
	}
	
	public static void getBUData(){
		Log.info("Start BigQuery dataflow");
		/*
		 * "select b.SOAR_NO, b.SOAR_NM, b.FP_DVSN_DESC, a.BUS_NBR, a.UNIT_NBR,
		 *  a.DVSN_NBR, a.DEPT_NBR, a.CATG_CLUSTER_NBR, a.SUB_CATG_NBR, a.CATG_NBR 
		 *  from `syw-analytics-repo-prod.alex_arp_tbls_prd.lu_shc_vendor_pack` a 
		 *  inner join `syw-analytics-repo-prod.cbr_mart_tbls.sywr_kmt_soar_bu` b 
		 *  on a.ksn_id = b.ksn_id 
		 *  group by b.SOAR_NO, a.UNIT_NBR, a.DVSN_NBR, a.BUS_NBR, b.SOAR_NM, 
		 *  b.FP_DVSN_DESC, a.DEPT_NBR, a.CATG_CLUSTER_NBR, 
		 *  a.SUB_CATG_NBR, a.CATG_NBR;"
		 */

		String query = "select b.SOAR_NO, b.SOAR_NM, b.FP_DVSN_DESC, a.BUS_NBR, a.UNIT_NBR, "
				+ "a.DVSN_NBR, a.DEPT_NBR, a.CATG_CLUSTER_NBR, a.CATG_NBR,  "
				+ "a.SUB_CATG_NBR  from "
				+ "`syw-analytics-repo-prod.alex_arp_tbls_prd.lu_shc_vendor_pack` a "
				+ "inner join `syw-analytics-repo-prod.cbr_mart_tbls.sywr_kmt_soar_bu` b "
				+ "on a.ksn_id = b.ksn_id group by b.SOAR_NO, a.UNIT_NBR, a.DVSN_NBR, "
				+ "a.BUS_NBR, b.SOAR_NM, b.FP_DVSN_DESC, a.DEPT_NBR, a.CATG_CLUSTER_NBR, "
				+ "a.SUB_CATG_NBR, a.CATG_NBR;";


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
		} catch (Exception e) {
			Log.info("Exception: " + e.getMessage() + e.getStackTrace().toString());
		}
	}
	
	public static void main(String[] args){
		getBUData();
	}
}
