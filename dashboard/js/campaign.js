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
	}
}