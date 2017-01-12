var Campaign = {
	Constructor : function(){
		this.init = Campaign.init;
		this.campaignTable = Campaign.campaignTable;
		this.campaignData = Campaign.campaignData;
	//	this.checkMandatory = Campaign.checkMandatory;
		this.validate = Campaign.validate;
		this.positiveCurrency = Campaign.positiveCurrency;
		this.checkDate = Campaign.checkDate;
		this.lengthCheck = Campaign.lengthCheck;
		this.validationFlag = true;
		this.checkDateFlag = true;
		this.tableOptions = function(columns){
			this.processing = true;
			this.paging = true ;
			this.ordering = true;
			this.searching = true;
			this.ajax = {};
			this.ajax.dataSrc = "";
			this.columns = columns;
		}

	},
	init : function(){
		var that = this;
		$("#creteCampaign").on("click",function(){
			$("input[type=text], input[type=number], input[type=date], input.number").val("");
			$("#campaignModal").modal('show');
			var start = new Date();
			var day = ("0" + start.getDate()).slice(-2);
			var month = ("0" + (start.getMonth() + 1)).slice(-2);
			var today = start.getFullYear()+"-"+(month)+"-"+(day) ;
			$("#startDate").val(today);
			$(".alert").empty();
			$(".alert").hide();
			$(".load").css('display','none');
			$("#campaignName").removeClass("error1");
	    $("#campaignName").parent().find(".lenWarning").remove();
		});
		$("#graphArea").hide();
		$('input.number').keyup(function(event) {
		  // skip for arrow keys
		if(event.which >= 37 && event.which <= 40) return;

		  // format number
		  $(this).val(function(index, value) {
			return value
			.replace(/\D/g, "").replace(/\B(?=(\d{3})+(?!\d))/g, ",").replace(/(\$?)([\d,]+)/g, "$$$2")
			;
		  });
		});
		var columns = [
				{ "data" : 'campaign_details.name',
				  "orderable" : true
				},
				{ "data" : 'campaign_details.money',
				  "orderable" : true,
				  "render" : function(data){
					var options = {currency:"USD",style:"currency",currencyDisplay:"symbol"};
					return data.toLocaleString('en-US',options);
				  }
				},
				{ "data" : 'campaign_details.category',
				  "orderable" : true
				},
				{ "data" : 'campaign_details.start_date',
				 "orderable" : true,
				 "render": function(data){
					if(data !=undefined || data !=null){
						return moment(data).format('DD MMM YYYY')
					}
					else{ return "";}
				 }
				},
				{ "data" : null,
				  "orderable" : true,
				  "render" : function(data){
					return "<span class='period-text'>"+ data.campaign_details.period +" </span> <i class='icon-caret-right icon-right'> </i>";
				  }
				},
				{ "data" : 'campaign_details.created_at',
				 "orderable" : true,
				 "visible":false
				}
			];
	/* Campaign Table initialization */
	var tableOptions = new this.tableOptions(columns);
		tableOptions.order = [[5,"desc"]];
		tableOptions.rowId = "campaign_details.campaign_id";
		tableOptions.ajax = function(data,callback,settings){
			data ="";
			$.ajax({
				url:  exposedAPIs.baseUrl+"campaigns",
				success:function(res,xhr){
					if(xhr != "success"){
						callback({
						data:''
						})
						that.campaignTable.ajax.reload().draw();
					}
					else{
						callback({
							data:res.data
						})
					}
					$(".iconCustomization").hide();
				}

			})
		}
		that.campaignTable = $("#campaignTable").DataTable(tableOptions);

		 $('#campaignTable tbody').on( 'click', 'tr', function () {
		 	if ( $(this).hasClass('selected') && $(this).hasClass('iconCustomization') ) {
		 		$(this).removeClass('selected');
		 	}
		 	else {
		 		$('tr.selected').removeClass('selected');
		 		$(this).addClass('selected');
		 	}
		 	$('.metrics-text').hide();
		 	$("#graphArea").show();
			GlobalVar.CampaignGraph.drawPlot( $(this)[0].id);

		 });
		that.campaignTable.on('xhr.dt',function(e, settings, json, xhr){
			console.log("Table data loaded. Row count is "+json.data.length);
		});
	/* next- previous code */
		// next previous code
		var content = $('#content');
		content.css('list-style-type', 'none');
		content.wrap('<div id="wrapper"></div>');

		var wrapper = $('#wrapper');
		wrapper.append('<div class="clear clearfix"> </div><div class="modal-footer"><img class="load" src="default/img/please_wait.gif"   /> <button type="button" class="btn btn-cus" id="previous"><i class="icon-chevron-sign-left"></i></button> <button type="button" class="btn btn-cus" id="next" style="margin-bottom: 5px">  <i class="icon-chevron-sign-right"></i></button> <button type="button" id="saveCampaign" class="btn btn-greyBlue" style="margin-bottom: 5px">Save Campaign</button></div>');

		$('#previous').hide();
		$('#saveCampaign').hide();

		var liElements = content.children();
		liElements.hide();
		liElements.first().show();
		$(".alert").empty();
		$(".alert").hide();
		liElements.first().toggleClass('activate');

		var liElementCount = liElements.length;


		if (liElementCount > 0) {
			var counter = 0;

			function swapContent() {
				if (counter == 0) {
					$('#previous').hide();
					$(".modal-title").text("Campaign Details ");
				} else {
					$('#previous').show();
					$('#saveCampaign').hide();
				}

				if (counter == liElementCount - 1) {
					$('#next').hide();
					$('#saveCampaign').show();
					$(".modal-title").text("Offer Details ");
				} else {
					$('#next').show();
				}

				liElements.hide();
				liElements.removeClass('activate');
				$(liElements.get(counter)).toggleClass('activate');
				$(".alert").empty();
				$(".alert").hide();
				$(liElements.get(counter)).show();
			}

			$('#next').click(function () {
				if(checkMandatory('campaignModal') && that.validationFlag && that.checkDateFlag){
					if(counter < liElementCount){
						counter++;
					}
					else{
						counter = 0;
					}
					swapContent();
				}
			});

			$('#previous').click(function () {
			if(that.validationFlag)
			{
				counter--;
				swapContent();
				$('#saveCampaign').hide();
			}
			});
		}
		/* Modal hiden/close event handling */
		$("#campaignModal").on("hidden.bs.modal", function () {
			if(counter > 0){
				$("#previous").trigger("click");
				$(".modal-title").text("Campaign Details ");
			}
			$(".mandatory").removeClass("error");
		});

		$("#saveCampaign").on("click",function(event){
			event.preventDefault();
			that.campaignData = {};
			that.campaignData.campaign_details = {}
			that.campaignData.offer_details= {}
			if(checkMandatory('campaignModal') && that.validationFlag){
				that.campaignData.campaign_details.name = $("#campaignName").val();
				that.campaignData.campaign_details.format_level = $("#format_level").val();
				if($("#store_list").val() != undefined && $("#store_list").val() != ""){
					that.campaignData.campaign_details.store_location = $("#store_list").val().join();
				}
				else{
				that.campaignData.campaign_details.store_location = "";
				}
				if($("#category").val() != undefined && $("#category").val() != ""){
					that.campaignData.campaign_details.category= $("#category").val().join();
				}
				else{
				that.campaignData.campaign_details.category = "";
				}
				that.campaignData.campaign_details.money = $("#money").val().replace(/,/g,'').replace("\u0024", "")-0;
				//that.campaignData.campaign_details.category = $("#category").val();
				that.campaignData.campaign_details.conversion_ratio = 5;
				that.campaignData.campaign_details.start_date = $("#startDate").val();
				that.campaignData.campaign_details.period = $("#period").val();
				that.campaignData.offer_details.offer_type = $("#OfferType").val();
				that.campaignData.offer_details.min_value = parseFloat($("#mindollar").val().replace(/,/g,'').replace("\u0024", ""));
				that.campaignData.offer_details.max_value = parseFloat($("#maxdollar").val().replace(/,/g,'').replace("\u0024", ""));
				that.campaignData.offer_details.valid_till = $("#validity").val();
				that.campaignData.offer_details.member_issuance = $("#memberissuance").val();
				$(".load").css('display','inline-block');
				$("#saveCampaign").prop('disabled',"disabled");
				$("#previous").prop('disabled',"disabled");
				$.ajax({
					url : exposedAPIs.baseUrl+"saveCampaign?offer_data="+JSON.stringify(that.campaignData),
					success: function(responsedata,statusText,xhr){
						if(xhr.status !=200){
								alert("Something went wrong please try again later. "+statusText);
						}
						else{
							$("#campaignModal").modal('hide');
							$("#successDialog").modal('show');
							that.campaignTable.ajax.reload().draw();
							console.info("Campaign saved with this details, below in table");
							console.table([that.campaignData.campaign_details]);
							console.table([that.campaignData.offer_details]);
							setInterval(function(){ $("#successDialog").modal('hide') }, 3000);
						}
						$(".load").css('display','none');
						$("#saveCampaign").prop('disabled',false);
						$("#previous").prop('disabled',false);
					},
					error: function(error,statusText, xhr){
					   if(xhr.status ==200 && statusText == "parseError"){
						  $("#campaignModal").modal('hide');
							 $("#successDialog").modal('show');
						  that.campaignTable.ajax.reload().draw();
						  setInterval(function(){ $("#successDialog").modal('hide') }, 3000);
					   }
					   else{
					   alert("Something went wrong please try again later. "+statusText);
					   console.error("Internal server error."+" status: "+error.statusText);
					   }
					   $(".load").css('display','none');
					   $("#saveCampaign").prop('disabled',false);
					   $("#previous").prop('disabled',false);
					   $("#campaignModal").modal('hide');
					}
				});
			}
		});

	/* load the dropdown from endpoits*/
	$.ajax({
		//url : exposedAPIs.baseUrl+"getListItems",
		url : exposedAPIs.baseUrl+"getListItems",
		dataType : 'json',
		success: function(responsedata,statusText,xhr){

			$.each(responsedata.data.conversion_ratio,function(index,val){
				var option ="<option>"+val+"</option>";
				$('#conversionratio').append(option);
			})
			$.each(responsedata.data.offer_type,function(index,val){
				var option ="<option>"+val+"</option>";
				$('#OfferType').append(option);
			})
			$.each(responsedata.data.format_level,function(index,val){
				var option ="<option>"+val+"</option>";
				$('#format_level').append(option);
			})
			var storelist = {};
			var businessUnits = {};
			storelist = responsedata.data.store_locations;
			businessUnits = responsedata.data.categories;

			$('#mindollar,#maxdollar').attr("min",parseInt(responsedata.data.minimum_surprise_points));
			$('#mindollar').attr("max",parseInt(responsedata.data.maximum_surprise_points)-1);
			$('#maxdollar').attr("max",parseInt(responsedata.data.maximum_surprise_points));
			$('#mindollar').attr("placeholder","$"+responsedata.data.minimum_surprise_points);
			$('#maxdollar').attr("placeholder","$"+responsedata.data.maximum_surprise_points);

			var format_level_id = $("#format_level").val();
			$.each(storelist[format_level_id.toLowerCase()],function(index,val){
				var option ="<option>"+val+"</option>";
				$('#store_list').append(option);
			});
			$.each(businessUnits[format_level_id.toLowerCase()],function(index,val){
				var option ="<option>"+val+"</option>";
				$('#category').append(option);
			})
			var created_at = 0 , checkall_at = 0,created_2 = 0,checkedall_2 = 0;
			$("#store_list").multiselect({
				create: function(event,ui){
					created_at = event.timeStamp;
					$("#storeLoad").hide();
				},
				beforeopen : function(event, ui){
					$("#storeLoad").show();
				},
				open : function(event, ui){
					$("#storeLoad").hide();
				},
				checkall : function(event, ui){
					checkall_at = event.timeStamp - created_at;
					console.info("time :" + checkall_at);
				}
			}).multiselectfilter();
			/**/
			$("#category").multiselect({
				create: function(event,ui){
					created_2 = event.timeStamp;
					$("#categoryLoad").hide();
				},
				beforeopen : function(event, ui){
					$("#categoryLoad").show();
				},
				open : function(event, ui){
					$("#categoryLoad").hide();
				},
				checkall : function(event, ui){
					checkall_2 = event.timeStamp - created_2;
					console.info("time :" + checkall_2);
				}
			}).multiselectfilter();
			/**/
			$("#format_level").on("change",function(){
				$("#store_list").empty();
				$("#category").empty();
				$("#storeLoad").show();
				$("#categoryLoad").show();
				var format_level_id = $("#format_level").val();
				$.each(storelist[format_level_id.toLowerCase()],function(index,val){
					var option ="<option>"+val+"</option>";
					$('#store_list').append(option);
				});
				$.each(businessUnits[format_level_id.toLowerCase()],function(index,val){
					var option ="<option>"+val+"</option>";
					$('#category').append(option);
				});
				$("#store_list").multiselect("refresh").multiselectfilter();
				$("#category").multiselect("refresh").multiselectfilter();
				setTimeout(function(){
						$("#storeLoad").hide();
						$("#categoryLoad").hide();
				},3000)
			});


		}
	})

	},

	validate : function(element,comparand,operation){
	/*Method to validate the current input element with comparand. operation specifies the type of comparison.*/
			var that = this;
			that.validationFlag = validations(element,comparand,operation);
	},

	checkDate : function (element) {
			var that = this;
			that.checkDateFlag = dateValidation(element);
	},
	lengthCheck:function (element) {
		var that = this;
		that.validationFlag = lengthValidation(element);
	}
}
