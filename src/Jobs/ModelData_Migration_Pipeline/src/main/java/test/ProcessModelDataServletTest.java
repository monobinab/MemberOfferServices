package test;

import com.google.api.services.bigquery.model.TableRow;
import com.google.cloud.dataflow.sdk.Pipeline;
import com.google.cloud.dataflow.sdk.coders.StringUtf8Coder;
import com.google.cloud.dataflow.sdk.testing.DataflowAssert;
import com.google.cloud.dataflow.sdk.testing.RunnableOnService;
import com.google.cloud.dataflow.sdk.testing.TestPipeline;
import com.google.cloud.dataflow.sdk.transforms.Create;
import com.google.cloud.dataflow.sdk.transforms.DoFnTester;
import com.google.cloud.dataflow.sdk.transforms.ParDo;
import com.google.cloud.dataflow.sdk.values.PCollection;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

import org.hamcrest.CoreMatchers;
import org.junit.Assert;
import org.junit.Test;
import org.junit.experimental.categories.Category;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;
import org.mockito.Mockito;
import static org.mockito.Mockito.when;

import com.flexappengine.syw.ProcessData.ProcessModelDataServlet;
import com.flexappengine.syw.ProcessData.ProcessModelDataServlet.SplitLineDataTask;

@RunWith(JUnit4.class)
public class ProcessModelDataServletTest {

	@Test
	public void testSplitLineDataTask() {
		DoFnTester<TableRow, String[]> extractWordsFn =
				DoFnTester.of(new SplitLineDataTask());
		TableRow trow = new TableRow();
		trow.set("Member", "12345678");
		trow.set("Offer", "5");
		trow.set("Campaign", "testcampaign");

		//String [] outArray = new String[2];
		//outArray[0]= "12345678";
		//outArray[1] = "5";
		ProcessModelDataServlet test = Mockito.mock(ProcessModelDataServlet.class);
		try {
			when(test.sendGet(Mockito.anyString(), Mockito.anyString(),Mockito.anyString(), Mockito.anyString())).thenReturn("Success");
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		List<String[]> outArray = extractWordsFn.processBatch(trow);

		Assert.assertThat(trow.get("Member"),
				CoreMatchers.is(outArray.get(0)[0]));
		Assert.assertThat(trow.get("Offer"),
				CoreMatchers.is(outArray.get(0)[1]));
	}


	@Test
	public void testSplitLineDataTaskNoRow() {
		DoFnTester<TableRow, String[]> extractWordsFn =
				DoFnTester.of(new SplitLineDataTask());
		TableRow trow = new TableRow();
		//trow.set("Member", "12345678");
		//trow.set("Offer", "5");
		//trow.set("Campaign", "testcampaign");

		//String [] outArray = new String[2];
		//outArray[0]= "12345678";
		//outArray[1] = "5";

		List<String[]> outArray = extractWordsFn.processBatch(trow);

		Assert.assertThat(trow.get("Member"),
				CoreMatchers.is(outArray.get(0)[0]));
		Assert.assertThat(trow.get("Offer"),
				CoreMatchers.is(outArray.get(0)[1]));

	}
	
		@Test
		@Category(RunnableOnService.class)
		public void testPipeline() throws Exception {
			Pipeline p = TestPipeline.create();
			TableRow trow1 = new TableRow();
			trow1.set("Member", "12345678");
			trow1.set("Offer", "5");
			trow1.set("Campaign", "testcampaign");

			TableRow trow2 = new TableRow();
			trow2.set("Member", "abcdef");
			trow2.set("Offer", "7");
			trow2.set("Campaign", "testcampaign");
			
			List<TableRow> rowLists = new ArrayList<TableRow>();
			rowLists.add(trow1);
			rowLists.add(trow2);

			PCollection<TableRow> input = p.apply(Create.of(rowLists));
			PCollection<String[]> output = input.apply(ParDo.of(new SplitLineDataTask()));

			String [] outArray1 = new String[2];
			outArray1[0]= "12345678";
			outArray1[1] = "5";
			String [] outArray2 = new String[2];
			outArray2[0]= "abcdef";
			outArray2[1] = "7";
			
			List<String []> outLists = new ArrayList<String []>();
			outLists.add(outArray1);
			outLists.add(outArray2);

			DataflowAssert.that(output).containsInAnyOrder(outLists);
			p.run();
		}

}
