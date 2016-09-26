var Campaign = {
	Constructor : function(){
		this.init = Campaign.init;
		this.Edit = Campaign.Edit;
		this.notNull = Campaign.notNull;
		this.campaignTable = Campaign.campaignTable;
		this.campaignData = Campaign.campaignData;
		this.tableOptions = function(columns){
			this.paging = true;
			this.serverSide = true;
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
			$("#campaignModal").modal('show');
		});
		
		var columns = [
				{ data : 'name'
				},
				{ data : 'money'
				},
				{ data : 'category'
				},
				{ data : 'conversion_ratio' 
				},
				{ data : 'period'
				},
				{ data : null,
				  render : function(data){
					return "<button class='btn btn-table' onclick='GlobalVar.Campaign.Edit("+data.id+")'> <i class='icon-edit icon-size'> </i> </button> <button class='btn btn-table'> <i class='icon-trash icon-size'> </i> </button>"
				  }
				}
			];
		
		var tableOptions = new this.tableOptions(columns);
		tableOptions.ajax.url = exposedAPIs.baseUrl + "/api/campaign/";
		tableOptions.ajax.dataSrc = "data";
		that.campaignTable = $("#campaignTable").DataTable(tableOptions);
		
	/* next- previous code */
		// next previous code
		var content = $('#content');
		content.css('list-style-type', 'none');
		content.wrap('<div id="wrapper"></div>');

		var wrapper = $('#wrapper');
		wrapper.append('<div class="clear clearfix"> </div><div class="modal-footer"><button type="button" class="btn btn-cus" id="previous"><i class="icon-chevron-sign-left"></i></button> <button type="button" class="btn btn-cus" id="next" style="margin-bottom: 5px">  <i class="icon-chevron-sign-right"></i></button> <button type="button" id="saveCampaign" class="btn btn-greyBlue" style="margin-bottom: 5px"> <i class="icon-thumbs-up"></i> Confirm </button></div>');

		$('#previous').hide();
		$('#addRule').hide();

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
				if(that.notNull($("#OfferType").val()))
					that.campaignData.offer_details.offertype = $("#OfferType").val();
				if(that.notNull($("#mindollar").val()))
					that.campaignData.offer_details.min = $("#mindollar").val();
				if(that.notNull($("#maxdollar").val()))
					that.campaignData.offer_details.max = $("#maxdollar").val();
				if(that.notNull($("#validity").val()))
					that.campaignData.offer_details.validity = $("#validity").val();
				if(that.notNull($("#memberIssurance").val()))
					that.campaignData.offer_details.memberIssurance = $("#memberIssurance").val();
				counter++;
				swapContent();
			});

			$('#previous').click(function () {
				counter--;
				swapContent();
			});
		}
		$("#saveCampaign").on("click",function(event){
			event.preventDefault();
			that.campaignData.campaign_details= {};
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
				type : "POST",
				contentType: "application/json",
				data: JSON.stringify(that.campaignData),
				success: function(data){
					$("#campaignModal").modal('hide');
					that.campaignTable.draw();
					alert(data);
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
		$.ajax({
			headers:{"authorization":exposedAPIs.authToken},
			type:"GET",
			url: exposedAPIs.baseUrl+"/api/campaign/"+id,
				success:function(data){
					$("#campaignId").val(data.data.id);
					$("#campaignName").val(data.data.name);
					$("#money").val(data.data.money);
					$("#category").val(data.data.category);
					$("#conversionratio").val(data.data.conversion_ratio);
					$("#period").val(data.data.period);
					
					$("#campaignModal").modal("show");
				},
				error: function(error){
					alert("Error"+error.statusText);
				}
		})
	}
}