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

package com.flexappengine.syw.ProcessBQTable;

import static com.google.datastore.v1.client.DatastoreHelper.makeKey;
import static com.google.datastore.v1.client.DatastoreHelper.makeValue;

import java.util.UUID;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.api.services.bigquery.model.TableRow;
import com.google.cloud.dataflow.sdk.Pipeline;
import com.google.cloud.dataflow.sdk.io.BigQueryIO;
import com.google.cloud.dataflow.sdk.io.datastore.DatastoreIO;
import com.google.cloud.dataflow.sdk.options.PipelineOptionsFactory;
import com.google.cloud.dataflow.sdk.transforms.DoFn;
import com.google.cloud.dataflow.sdk.transforms.ParDo;
import com.google.cloud.dataflow.sdk.values.PCollection;
import com.google.datastore.v1.Entity;
import com.google.datastore.v1.Key;

/**
 * A starter example for writing Google Cloud Dataflow programs.
 *
 * <p>
 * The example takes two strings, converts them to their upper-case
 * representation and logs them.
 *
 * <p>
 * To run this starter example locally using DirectPipelineRunner, just execute
 * it without any additional parameters from your favorite development
 * environment.
 *
 * <p>
 * To run this starter example using managed resource in Google Cloud Platform,
 * you should specify the following command-line options:
 * --project=<YOUR_PROJECT_ID>
 * --stagingLocation=<STAGING_LOCATION_IN_CLOUD_STORAGE>
 * --runner=BlockingDataflowPipelineRunner
 */
public class StarterPipeline {
	private static final Logger Log = LoggerFactory.getLogger(StarterPipeline.class);

	public static class SplitLineDataTask extends DoFn<TableRow, Entity> {
		private static final long serialVersionUID = 1L;

		public Entity makeEntity(TableRow content) {
			Entity.Builder entityBuilder = Entity.newBuilder();
			Key.Builder keyBuilder = makeKey("SywrOfrData", UUID.randomUUID().toString());
			keyBuilder.getPartitionIdBuilder().setNamespaceId("dev");
			entityBuilder.setKey(keyBuilder.build());
			entityBuilder.getMutableProperties().put("OFR_ID", makeValue((String) content.get("OFR_ID")).build());
			return entityBuilder.build();
		}

		@Override
		public void processElement(ProcessContext c) {
			TableRow row = c.element();
			Log.info((String) row.get("OFR_ID"));
			c.output(makeEntity(row));
		}
	}

	public static void main(String[] args) {
		Log.info("Start BigQuery dataflow");
		
		/*
		String query = "SELECT * FROM [syw-offers:lci_loyal_tbls.sywr_ofr] limit 10";
		Log.info("Query: " + query);
		*/
		
		try {
			Pipeline bp = Pipeline.create(PipelineOptionsFactory.fromArgs(args).withValidation().create());
			Log.info("BigQuery-DataStore pipeline created");
			PCollection<TableRow> BigQueryReadingCollection = bp
					.apply(BigQueryIO.Read.withoutValidation().from("syw-offers:lci_loyal_tbls.sywr_ofr_cpy"));
			PCollection<Entity> BigQueryTransformData = BigQueryReadingCollection
					.apply(ParDo.of(new SplitLineDataTask()));
			BigQueryTransformData.apply(DatastoreIO.v1().write().withProjectId("syw-offers"));
			Log.info("BigQuery-DataStore pipeline to run now");
			bp.run();
			Log.info("Finished BigQuery-DataStore dataflow");
		} catch (Exception e) {
			Log.info("Exception: " + e.getMessage() + e.getStackTrace().toString());
		}
	}
}
