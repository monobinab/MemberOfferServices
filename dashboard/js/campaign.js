var Campaign = {
	Constructor : function(){
		this.init = Campaign.init;
		this.tableOptions = function(columns){
			this.paging = true;
			this.ajax = {};
			this.ajax.dataSrc = "";
			this.columns = columns;
		}
		
	},
	init : function(){
		$("#creteCampaign").on("click",function(){
			$("#campaignModal").modal('show');
		});
		
		var data = [
			{
				"comp_name" : "First Compaign",
				"money": "$100",
				"category": "Approval",
				"conversion_ratio": "6",
				"period": "2 weeks",
			},
			{
				"comp_name" : "Second Compaign",
				"money":       "$100",
				"category":   "Not Approval",
				"conversion_ratio": "10",
				"period": "1 weeks",
			},
			{
				"comp_name" : "Third Compaign",
				"money": "$100",
				"category": "Approval",
				"conversion_ratio": "6",
				"period": "2 weeks",
			},
			{
				"comp_name" : "Fourth Compaign",
				"money":       "$100",
				"category":   "Not Approval",
				"conversion_ratio": "10",
				"period": "1 weeks",
			},
			{
				"comp_name" : "Fifth Compaign",
				"money": "$100",
				"category": "Approval",
				"conversion_ratio": "6",
				"period": "2 weeks",
			},
			{
				"comp_name" : "Sixth Compaign",
				"money":       "$100",
				"category":   "Not Approval",
				"conversion_ratio": "10",
				"period": "1 weeks",
			}
		];  


		$("#campaignTable").DataTable({
			data : data,
			columns: [
				{ data : 'comp_name'
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
				  render : function(){
					return "<button class='btn btn-table'> <i class='icon-edit icon-size'> </i> </button> <button class='btn btn-table'> <i class='icon-trash icon-size'> </i> </button>"
				  }
				}
			]
	    }); 
		
	/* next- previous code */
		// next previous code
		var content = $('#content');
		content.css('list-style-type', 'none');
		content.wrap('<div id="wrapper"></div>');

		var wrapper = $('#wrapper');
		wrapper.append('<div class="clear clearfix"> </div><div class="modal-footer"><button type="button" class="btn btn-cus" id="previous"><i class="icon-chevron-sign-left"></i></button> <button type="button" class="btn btn-cus" id="next" style="margin-bottom: 5px">  <i class="icon-chevron-sign-right"></i></button> <button type="button" id="addRule" class="btn btn-greyBlue" style="margin-bottom: 5px"> <i class="icon-thumbs-up"></i> Confirm </button></div>');

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
					$('#addRule').hide();
				}

				if (counter == liElementCount - 1) {
					$('#next').hide();
					$('#addRule').show();
				} else {
					$('#next').show();
				}

				liElements.hide();
				$(liElements.get(counter)).show();
			}

			if(liElements.last() == true){
				$('#addRule').show();
			}
			
			$('#next').click(function () {
				counter++;
				swapContent();
			});

			$('#previous').click(function () {
				counter--;
				swapContent();
			});
		}
	}
}