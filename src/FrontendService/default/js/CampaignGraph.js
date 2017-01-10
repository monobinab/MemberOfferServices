var CampaignGraph = {
  Constructor: function() {
    this.init = CampaignGraph.init;
    this.drawPlot = CampaignGraph.drawPlot;
  },

  init: function() {
	  var that = this;
  },
  drawPlot:function(selectedRow) {
    var emailArray = [];
    var offerArray  = [];
    $("#chart1").html("");
    $("#chart2").html("");
    $("#graphArea").append('<div id ="metrics_load_indicator" style="position: absolute;left: 0;top: 50%;width: 100%;text-align: center"><img src="default/img/please_wait.gif"/></div>')
    $("#metricsHeader").html("Campaign Metrics for "+selectedRow);
    $.ajax({
      // have to use synchronous here, else the function
      // will return before the data is fetched
      async: false,
      url: exposedAPIs.baseUrl+"getMetrics?campaign_id="+selectedRow,
      dataType:"json",
      success: function(responseData,statusText,xhr) {
        if(xhr.status !=200){
            alert("Something went wrong please try again later. "+statusText);
        }
        else
        {
          var emailMetrics = responseData.data.email_metrics;
          var offerMetrics = responseData.data.offer_metrics;
            for(var key in emailMetrics)
            {
              emailArray.push([emailMetrics[key],key.split('_').join(' ')]);
            }
            for(var key in offerMetrics)
            {
              offerArray.push([key.split('_').join(' '),offerMetrics[key]]);
            }
        }
console.log(offerArray);
      },
      error: function(error,statusText, xhr){
        if(xhr.status !=200 || statusText != "success"){
          alert("Something went wrong please try again later. "+statusText);
          console.error("Internal server error."+" status: "+error.statusText);
        }
     },
	 complete:function(){
		$("#metrics_load_indicator").remove();
		}
    });

    $.jqplot.config.enablePlugins = true;

     plot1 = $.jqplot('chart1', [emailArray], {
                              title: "Email Metrics",
                              animate: !$.jqplot.use_excanvas,
                              captureRightClick: true,
                              seriesColors:['#4285f4', '#fbbc05', '#ea4335', '#34a853'],
                              //seriesColors:['#85802b', '#00749F', '#73C774', '#C7754C'],
                              seriesDefaults:{
                                  renderer:$.jqplot.BarRenderer,
                                  shadowAngle: 135,
                                  rendererOptions: {
                                      barDirection: 'horizontal',
                                      highlightMouseDown: true,
                                      varyBarColor: true
                                  },
                                  pointLabels: {show: true, formatString: '%d'}
                              },

                              axes: {
                                xaxis:{
                                  drawMajorGridlines: false,
                                  tickOptions:{
                                       fontSize:'9pt',
                                     }
                                },
                                  yaxis: {
                                    drawMajorGridlines: false,
                                      renderer: $.jqplot.CategoryAxisRenderer,
                                      tickOptions:{
                                           fontSize:'9pt',
                                         }
                                  }
                              },
                              highlighter: {
                               					show: true,
                               					sizeAdjust: 2.5,
                                         showTooltip:true,
                                         useAxesFormatters: false,
                                         tooltipFormatString: '%s'
                               				}
                          });

             var plot2 = $.jqplot('chart2', [offerArray], {
               title : "Offer Metrics",
               animate: !$.jqplot.use_excanvas,
             seriesDefaults: {
               // make this a donut chart.
               renderer:$.jqplot.DonutRenderer,
               rendererOptions:{
                 // Donut's can be cut into slices like pies.
                 sliceMargin: 3,
                 // Pies and donuts can start at any arbitrary angle.
                 startAngle: -90,
                 showDataLabels: true,
                 // By default, data labels show the percentage of the donut/pie.
                 // You can show the data 'value' or data 'label' instead.
                 dataLabels: 'value',
                 // "totalLabel=true" uses the centre of the donut for the total amount

               }
             },
             legend: { show:true, location: 'w' },
             highlighter: {
              					show: true,
              					sizeAdjust: 2.5,
                        showTooltip:true,
                        useAxesFormatters: false,
                        tooltipFormatString: '%s'
              				}

           });

  }
};
