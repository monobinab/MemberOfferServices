var Campaign = {
	Constructor : function(){
		this.init = Campaign.init;
		this.Edit = Campaign.Edit;
		this.notNull = Campaign.notNull;
		this.campaignTable = Campaign.campaignTable;
		this.campaignData = Campaign.campaignData;
		this.ajaxMethod = Campaign.ajaxMethod;
		this.tableOptions = function(columns){
			this.dom = "lftip";
			this.paging = true;
			this.serverSide = true;
			this.cache = true
			this.processing = true;
			this.destroy = true;
			this.ajax = {};
			this.ajax.dataSrc = "";
			this.columns = columns;
		}
		
	},
	init : function(){
		var that = this;
		$("#creteCampaign").on("click",function(){
			that.ajaxMethod = "POST";
			$("input:text").val("");
			$("#campaignModal").modal('show');
		});
		
		var columns = [
				{ data : 'campaign_details.name'
				},
				{ data : 'campaign_details.money'
				},
				{ data : 'campaign_details.category'
				},
				{ data : 'campaign_details.conversion_ratio' 
				},
				{ data : 'campaign_details.period'
				},
				{ data : null,
				  render : function(data){
					return "<button class='btn btn-table' onclick='GlobalVar.Campaign.Edit("+data.campaign_details.campaign_id+")'> <i class='icon-edit icon-size'> </i> </button>"
				  }
				}
			];
		
		var tableOptions = new this.tableOptions(columns);
		tableOptions.ajax = function(data,callback,settings){
			data ="";
			$.ajax({
				headers: {"authorization":exposedAPIs.authToken},
				url: exposedAPIs.baseUrl +"/api/campaign/",
				success:function(res){
					callback({
						recordsTotal:res.data.length,
						data:res.data
					})
				}
				
			})
		}
		that.campaignTable = $("#campaignTable").DataTable(tableOptions);
		
	/* next- previous code */
		// next previous code
		var content = $('#content');
		content.css('list-style-type', 'none');
		content.wrap('<div id="wrapper"></div>');

		var wrapper = $('#wrapper');
		wrapper.append('<div class="clear clearfix"> </div><div class="modal-footer"><button type="button" class="btn btn-cus" id="previous"><i class="icon-chevron-sign-left"></i></button> <button type="button" class="btn btn-cus" id="next" style="margin-bottom: 5px">  <i class="icon-chevron-sign-right"></i></button> <button type="button" id="saveCampaign" class="btn btn-greyBlue" style="margin-bottom: 5px"> <i class="icon-thumbs-up"></i> Confirm </button></div>');

		$('#previous').hide();
		$('#saveCampaign').hide();

		var liElements = content.children();
		liElements.hide();
		liElements.first().show();

		var liElementCount = liElements.length;

		if (liElementCount > 0) {
			var counter = 0;

			function swapContent() {
				if (counter == 0) {
					$('#previous').hide();
				} else {
					$('#previous').show();
					$('#saveCampaign').hide();
				}

				if (counter == liElementCount - 1) {
					$('#next').hide();
					$('#saveCampaign').show();
				} else {
					$('#next').show();
				}

				liElements.hide();
				$(liElements.get(counter)).show();
			}

			if(liElements.last() == true){
				$('#saveCampaign').show();
			}
			
			$('#next').click(function () {
				that.campaignData = {};
				that.campaignData.offer_details = {}
				if(that.notNull($("#offerid").val()) && that.ajaxMethod == "PUT");
					that.campaignData.offer_details.offer_id = $("#offerid").val();
				if(that.notNull($("#OfferType").val()))
					that.campaignData.offer_details.offer_type = $("#OfferType").val();
				if(that.notNull($("#mindollar").val()))
					that.campaignData.offer_details.min_value = $("#mindollar").val();
				if(that.notNull($("#maxdollar").val()))
					that.campaignData.offer_details.max_value = $("#maxdollar").val();
				if(that.notNull($("#validity").val()))
					that.campaignData.offer_details.valid_till = $("#validity").val();
				if(that.notNull($("#memberissuance").val()))
					that.campaignData.offer_details.member_issuance = $("#memberissuance").val();
				counter++;
				swapContent();
			});

			$('#previous').click(function () {
				counter--;
				swapContent();
				$('#saveCampaign').hide();
			});
		}
		$("#saveCampaign").on("click",function(event){
			event.preventDefault();
			that.campaignData.campaign_details= {};
			if(that.notNull($("#campaignid").val()) && that.ajaxMethod == "PUT");
				that.campaignData.campaign_details.campaign_id = $("#campaignid").val();
			if(that.notNull($("#campaignName").val()))
				that.campaignData.campaign_details.name = $("#campaignName").val();
			if(that.notNull($("#money").val()))
				that.campaignData.campaign_details.money = $("#money").val();
			if(that.notNull($("#category").val()))
				that.campaignData.campaign_details.category = $("#category").val();
			if(that.notNull($("#conversionratio").val()))
				that.campaignData.campaign_details.conversion_ratio = $("#conversionratio").val();
			if(that.notNull($("#period").val()))
				that.campaignData.campaign_details.period = $("#period").val();
			$.ajax({
				headers: {"authorization":exposedAPIs.authToken},
				url : exposedAPIs.baseUrl + "/api/campaign/",
				type : that.ajaxMethod,
				contentType: "application/json",
				data: JSON.stringify(that.campaignData),
				success: function(data){
					$("#campaignModal").modal('hide');
					that.campaignTable.draw();
					alert(data.message);
				},
				error: function(error){
					$("#campaignModal").modal('hide');
					that.campaignTable.draw();
					alert("Something went wrong please try again later. "+error.statusText);
				}
			})
			
		})
	},
	
	notNull: function(value){
		if (typeof value != 'undefined' && value)
		 {
			return true;
		 }
		 else
		 {
			return false;
		 }
	},
	
	Edit : function(id){
		var that = this;
		that.ajaxMethod = "PUT";
		$.ajax({
			headers:{"authorization":exposedAPIs.authToken},
			type:"GET",
			url: exposedAPIs.baseUrl+"/api/campaign/"+id+"/",
				success:function(res){
					var data = res.data[0];
					$("#offerid").val(data.offer_details.offer_id);
					$("#OfferType").val(data.offer_details.offer_type);
					$("#mindollar").val(data.offer_details.min_value);
					$("#maxdollar").val(data.offer_details.max_value);
					var validity = data.offer_details.valid_till.split('-');
					validity = validity.reverse();
					validity = validity.join("-");
					document.getElementById("validity").value = validity;
					$("#memberissuance").val(data.offer_details.member_issuance);
					$("#campaignid").val(data.campaign_details.campaign_id);
					$("#campaignName").val(data.campaign_details.name);
					$("#money").val(data.campaign_details.money);
					$("#category").val(data.campaign_details.category);
					$("#conversionratio").val(data.campaign_details.conversion_ratio);
					$("#period").val(data.campaign_details.period);
					
					$("#campaignModal").modal("show");
				},
				error: function(error){
					alert("Error"+error.statusText);
				}
		})
	}
}