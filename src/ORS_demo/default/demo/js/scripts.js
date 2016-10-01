var Scripts = {
  Constructor: function() {
    this.init = Scripts.init;
	this.createXmlform = Scripts.createXmlform;
	this.checkMandatory = Scripts.checkMandatory;
  },

  init: function() {
	  var that = this;
	  $(".alert").hide();
	  $("#createOffer").on('click',function(event){
			//var xml = $("#dummy").html();
		  event.preventDefault();
		  if(that.checkMandatory('offerForm')){
		   $.ajax({
			  url: exposedApi.baseurl+"createOffer",
			  contentType:'text/plain',
			  type: 'POST',
			  data: that.createXmlform(),
			  success: function(responseData){
				$('input').val("");
				$('#condition').val("");
				if(responseData['data'] == null){
					alert("Authentication error.");
					return;
				}
				  var result = $.parseXML(responseData['data']);
					var statusText = $(result).find('StatusText').text();
					if($(result).find('Status').text() == 00){
						alert("Offer created "+statusText);
					}
					else{
						alert("Error: "+statusText)
					}
						
			  },
			  error: function(responseData){
				alert("Error");
			  }
			  
		})
		}
	  })

  },

  createXmlform : function(){
var updatedXML = "";
updatedXML += '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:off="http://rewards.sears.com/schemas/offer/" xmlns:sch="http://rewards.sears.com/schemas/">';
  updatedXML += '<soap:Header/>';
   updatedXML += '<soap:Body>';
     updatedXML += '<off:CreateUpdateOffer>';
        updatedXML += '<sch:MessageVersion>01</sch:MessageVersion>';
         updatedXML += '<sch:RequestorID>OFRP</sch:RequestorID>';
        updatedXML += '<sch:Source>TI</sch:Source>';
        updatedXML += '<off:OfferNumber>'+$("#OfferPointsDollarName").val()+'</off:OfferNumber>';
        updatedXML += '<off:OfferPointsDollarName>'+$("#OfferPointsDollarName").val()+'</off:OfferPointsDollarName>';
        updatedXML += '<off:OfferDescription>'+$("#OfferDescription").val()+'</off:OfferDescription>';
        updatedXML += '<off:OfferType>'+$("#OfferType").val()+'</off:OfferType>';
        updatedXML += '<off:OfferSubType>'+$("#OfferSubType").val()+'</off:OfferSubType>';
        updatedXML += '<off:OfferBUProgram>';
           updatedXML += '<off:BUProgram>';
              updatedXML += '<off:BUProgramName>BU - Apparel</off:BUProgramName>';
              updatedXML += '<off:BUProgramCost>0.00</off:BUProgramCost>';
            updatedXML += '</off:BUProgram>';
         updatedXML += '</off:OfferBUProgram>';
        updatedXML += '<off:ReceiptDescription>TELL-16289</off:ReceiptDescription>';
        updatedXML += '<off:OfferCategory>Stackable</off:OfferCategory>';
        updatedXML += '<off:OfferStartDate>'+$("#OfferStartDate").val()+'</off:OfferStartDate>';
        updatedXML += '<off:OfferStartTime/>';
        updatedXML += '<off:OfferEndDate>'+$("#OfferEndDate").val()+'</off:OfferEndDate>';
        updatedXML += '<off:OfferEndTime/>';
        updatedXML += '<off:ExpenseAllocation>No allocation – Charge all to WH</off:ExpenseAllocation>';
        updatedXML += '<off:ModifiedBy>nand</off:ModifiedBy>';
        updatedXML += '<off:ModifiedTS>2014-06-25 10:40:00</off:ModifiedTS>';
        updatedXML += '<off:OfferAttributes>';
           updatedXML += '<off:OfferAttribute>';
              updatedXML += '<off:Name>MULTI_TRAN_IND</off:Name>';
              updatedXML += '<off:Values>';
                 updatedXML += '<off:Value>N</off:Value>';
               updatedXML += '</off:Values>';
            updatedXML += '</off:OfferAttribute>';
           updatedXML += '<off:OfferAttribute>';
              updatedXML += '<off:Name>OFFER_NAME_MAP</off:Name>';
              updatedXML += '<off:Values>';
                 updatedXML += '<off:Value>Shop Your Way offer</off:Value>';
               updatedXML += '</off:Values>';
            updatedXML += '</off:OfferAttribute>';
           updatedXML += '<off:OfferAttribute>';
              updatedXML += '<off:Name>OFFER_DAILY_IND</off:Name>';
              updatedXML += '<off:Values>';
                 updatedXML += '<off:Value>N</off:Value>';
               updatedXML += '</off:Values>';
            updatedXML += '</off:OfferAttribute>';
           updatedXML += '<off:OfferAttribute>';
              updatedXML += '<off:Name>POINTS_AWARD_ON</off:Name>';
              updatedXML += '<off:Values>';
                 updatedXML += '<off:Value>Transaction Date plus</off:Value>';
               updatedXML += '</off:Values>';
            updatedXML += '</off:OfferAttribute>';
           updatedXML += '<off:OfferAttribute>';
              updatedXML += '<off:Name>POINTS_AWARD_DATE_PLUS</off:Name>';
              updatedXML += '<off:Values>';
                 updatedXML += '<off:Value>2</off:Value>';
               updatedXML += '</off:Values>';
            updatedXML += '</off:OfferAttribute>';
           updatedXML += '<off:OfferAttribute>';
              updatedXML += '<off:Name>POINTS_EXPIRE_ON</off:Name>';
              updatedXML += '<off:Values>';
                 updatedXML += '<off:Value>Transaction Date plus</off:Value>';
               updatedXML += '</off:Values>';
            updatedXML += '</off:OfferAttribute>';
           updatedXML += '<off:OfferAttribute>';
              updatedXML += '<off:Name>POINTS_EXPIRE_PLUS</off:Name>';
              updatedXML += '<off:Values>';
                 updatedXML += '<off:Value>4</off:Value>';
               updatedXML += '</off:Values>';
            updatedXML += '</off:OfferAttribute>';
           updatedXML += '<off:OfferAttribute>';
              updatedXML += '<off:Name>POINTS_EXPIRE_PLUS_UNIT</off:Name>';
              updatedXML += '<off:Values>';
                 updatedXML += '<off:Value>Quarter(s)</off:Value>';
               updatedXML += '</off:Values>';
            updatedXML += '</off:OfferAttribute>';
           updatedXML += '<off:OfferAttribute>';
              updatedXML += '<off:Name>ONLINE_MATERIAL_IND</off:Name>';
              updatedXML += '<off:Values>';
                 updatedXML += '<off:Value>N</off:Value>';
               updatedXML += '</off:Values>';
            updatedXML += '</off:OfferAttribute>';
         updatedXML += '</off:OfferAttributes>';
        updatedXML += '<off:Rules>';
           updatedXML += '<off:Rule Entity="Location">';
              updatedXML += '<off:Conditions>';
                 updatedXML += '<off:Condition>';
                    updatedXML += '<off:Name>STORE_LOCATION</off:Name>';
                    updatedXML += '<off:Operator>EQUALS</off:Operator>';
                    updatedXML += '<off:Values>';
                       updatedXML += '<off:Value>Order Location</off:Value>';
                     updatedXML += '</off:Values>';
                  updatedXML += '</off:Condition>';
                 updatedXML += '<off:Condition>';
                    updatedXML += '<off:Name>STORE_TYPES</off:Name>';
                    updatedXML += '<off:Operator>EQUALS</off:Operator>';
                    updatedXML += '<off:Values>';
                       updatedXML += '<off:Value>All Store Types</off:Value>';
                     updatedXML += '</off:Values>';
                  updatedXML += '</off:Condition>';
                 updatedXML += '<off:Condition>';
                    updatedXML += '<off:Name>STORE_FORMAT</off:Name>';
                    updatedXML += '<off:Operator>IN</off:Operator>';
                    updatedXML += '<off:Values>';
                       updatedXML += '<off:Value>RSU-A STORE (FULL LINE)</off:Value>';
                     updatedXML += '</off:Values>';
                  updatedXML += '</off:Condition>';
                 updatedXML += '<off:Condition>';
                    updatedXML += '<off:Name>LOCATION_OPTIONS</off:Name>';
                    updatedXML += '<off:Operator>CONTAINS</off:Operator>';
                    updatedXML += '<off:Values>';
                       updatedXML += '<off:Value>state</off:Value>';
                       updatedXML += '<off:Value>city</off:Value>';
                       updatedXML += '<off:Value>zipcode</off:Value>';
                     updatedXML += '</off:Values>';
                    updatedXML += '<off:ConditionAttributes>';
                       updatedXML += '<off:ConditionAttribute>';
                          updatedXML += '<off:Name>state</off:Name>';
                          updatedXML += '<off:Operator>IN</off:Operator>';
                          updatedXML += '<off:Values>';
                             updatedXML += '<off:Value>NY</off:Value>';
                             updatedXML += '<off:Value>IL</off:Value>';
                           updatedXML += '</off:Values>';
                        updatedXML += '</off:ConditionAttribute>';
                       updatedXML += '<off:ConditionAttribute>';
                          updatedXML += '<off:Name>city</off:Name>';
                          updatedXML += '<off:Operator>IN</off:Operator>';
                          updatedXML += '<off:Values>';
                             updatedXML += '<off:Value>NEW YORK</off:Value>';
                             updatedXML += '<off:Value>HOFFMAN ESTATES</off:Value>';
                           updatedXML += '</off:Values>';
                        updatedXML += '</off:ConditionAttribute>';
                       updatedXML += '<off:ConditionAttribute>';
                          updatedXML += '<off:Name>zipcode</off:Name>';
                          updatedXML += '<off:Operator>IN</off:Operator>';
                          updatedXML += '<off:Values>';
                             updatedXML += '<off:Value>60179</off:Value>';
                             updatedXML += '<off:Value>80031</off:Value>';
                           updatedXML += '</off:Values>';
                        updatedXML += '</off:ConditionAttribute>';
                     updatedXML += '</off:ConditionAttributes>';
                  updatedXML += '</off:Condition>';
                 updatedXML += '<off:Condition>';
                    updatedXML += '<off:Name>STORE_NUMBERS</off:Name>';
                    updatedXML += '<off:Operator>CONTAINS</off:Operator>';
                    updatedXML += '<off:Values>';
                       updatedXML += '<off:Value>NPOS</off:Value>';
                     updatedXML += '</off:Values>';
                    updatedXML += '<off:ConditionAttributes>';
                       updatedXML += '<off:ConditionAttribute>';
                          updatedXML += '<off:Name>NPOS</off:Name>';
                          updatedXML += '<off:Operator>IN</off:Operator>';
                          updatedXML += '<off:Values>';
                             updatedXML += '<off:Value>01001</off:Value>';
                             updatedXML += '<off:Value>01003</off:Value>';
                           updatedXML += '</off:Values>';
                        updatedXML += '</off:ConditionAttribute>';
                     updatedXML += '</off:ConditionAttributes>';
                  updatedXML += '</off:Condition>';
                 updatedXML += '<off:Condition>';
                    updatedXML += '<off:Name>STORE_NUMBERS</off:Name>';
                    updatedXML += '<off:Operator>NOT CONTAINS</off:Operator>';
                    updatedXML += '<off:Values>';
                       updatedXML += '<off:Value>NPOS</off:Value>';
                     updatedXML += '</off:Values>';
                    updatedXML += '<off:ConditionAttributes>';
                       updatedXML += '<off:ConditionAttribute>';
                          updatedXML += '<off:Name>NPOS</off:Name>';
                          updatedXML += '<off:Operator>IN</off:Operator>';
                          updatedXML += '<off:Values>';
                             updatedXML += '<off:Value>01004</off:Value>';
                           updatedXML += '</off:Values>';
                        updatedXML += '</off:ConditionAttribute>';
                     updatedXML += '</off:ConditionAttributes>';
                  updatedXML += '</off:Condition>';
               updatedXML += '</off:Conditions>';
            updatedXML += '</off:Rule>';
           updatedXML += '<off:Rule Entity="Member">';
              updatedXML += '<off:Conditions>';
                 updatedXML += '<off:Condition>';
                    updatedXML += '<off:Name>MEMBER_STATUS</off:Name>';
                    updatedXML += '<off:Operator>IN</off:Operator>';
                    updatedXML += '<off:Values>';
                       updatedXML += '<off:Value>BASE</off:Value>';
                       updatedXML += '<off:Value>BONUS</off:Value>';
                     updatedXML += '</off:Values>';
                  updatedXML += '</off:Condition>';
                 updatedXML += '<off:Condition>';
                    updatedXML += '<off:Name>MEMBER_NUMBER</off:Name>';
                    updatedXML += '<off:Operator>IN</off:Operator>';
                    updatedXML += '<off:Values>';
                       updatedXML += '<off:Value>7081011086867045</off:Value>';
                     updatedXML += '</off:Values>';
                  updatedXML += '</off:Condition>';
               updatedXML += '</off:Conditions>';
            updatedXML += '</off:Rule>';
            updatedXML += '<!--off:Rule Entity="Transaction">';
              updatedXML += '<off:Conditions>';
                 updatedXML += '<off:Condition>';
                    updatedXML += '<off:Name>QUALIFY_COUPON</off:Name>';
                    updatedXML += '<off:Operator>IN</off:Operator>';
                    updatedXML += '<off:Values>';
                       updatedXML += '<off:Value>NRS123</off:Value>';
                     updatedXML += '</off:Values>';
                  updatedXML += '</off:Condition>';
                 updatedXML += '<off:Name>MUST_PRESENT_TENDER_SYWR</off:Name>';
			     updatedXML += '<off:Operator>CONTAINS</off:Operator>';
			     updatedXML += '<off:Values>';
				   updatedXML += '<off:Value>SYWR</off:Value>';
				   updatedXML += '<off:Value>Min</off:Value>';
				   updatedXML += '<off:Value>Max</off:Value>';
				updatedXML += '</off:Values>';
			   updatedXML += '<off:ConditionAttributes>';
			   updatedXML += '<off:ConditionAttribute>';
							   updatedXML += '<off:Name>SYWR</off:Name>';
							   updatedXML += '<off:Operator>EQUALS</off:Operator>';
							   updatedXML += '<off:Values>';
									updatedXML += '<off:Value>Y</off:Value>';
								updatedXML += '</off:Values>';
				updatedXML += '</off:ConditionAttribute>';
			   updatedXML += '<off:ConditionAttribute>';
							   updatedXML += '<off:Name>Min</off:Name>';
							   updatedXML += '<off:Operator>EQUALS</off:Operator>';
							   updatedXML += '<off:Values>';
											   updatedXML += '<off:Value>10.00</off:Value>';
								updatedXML += '</off:Values>';
				updatedXML += '</off:ConditionAttribute>';
			   updatedXML += '<off:ConditionAttribute>';
							   updatedXML += '<off:Name>Max</off:Name>';
							   updatedXML += '<off:Operator>EQUALS</off:Operator>';
							   updatedXML += '<off:Values>';
											   updatedXML += '<off:Value>20.00</off:Value>';
								updatedXML += '</off:Values>';
				updatedXML += '</off:ConditionAttribute>';
				updatedXML += '</off:ConditionAttributes>';
				updatedXML += '</off:Condition>';
               updatedXML += '</off:Conditions>';
            updatedXML += '</off:Rule-->';
           updatedXML += '<off:RuleActions>';
              updatedXML += '<off:ActionID>ACTION-1</off:ActionID>';
            updatedXML += '</off:RuleActions>';
         updatedXML += '</off:Rules>';
        updatedXML += '<off:Actions>';
           updatedXML += '<off:Action ActionID="ACTION-1" ActionName="EARN">';
              updatedXML += '<off:ActionProperties>';
                 updatedXML += '<off:ActionProperty>';
                    updatedXML += '<off:Property>';
                       updatedXML += '<off:Name>OFFER_FOR</off:Name>';
                       updatedXML += '<off:Values>';
                          updatedXML += '<off:Value>Item</off:Value>';
                        updatedXML += '</off:Values>';
                     updatedXML += '</off:Property>';
                  updatedXML += '</off:ActionProperty>';
                 updatedXML += '<off:ActionProperty>';
                    updatedXML += '<off:Property>';
                       updatedXML += '<off:Name>OFFER_RANGE</off:Name>';
                       updatedXML += '<off:Values>';
                          updatedXML += '<off:Value>Flat</off:Value>';
                        updatedXML += '</off:Values>';
                     updatedXML += '</off:Property>';
                  updatedXML += '</off:ActionProperty>';
                 updatedXML += '<off:ActionProperty PropertyType="Tier">';
                    updatedXML += '<off:Property>';
                       updatedXML += '<off:Name>MIN</off:Name>';
                       updatedXML += '<off:Values>';
                          updatedXML += '<off:Value>1</off:Value>';
                        updatedXML += '</off:Values>';
                     updatedXML += '</off:Property>';
                    updatedXML += '<off:Property>';
                       updatedXML += '<off:Name>MAX</off:Name>';
                       updatedXML += '<off:Values>';
                          updatedXML += '<off:Value>6</off:Value>';
                        updatedXML += '</off:Values>';
                     updatedXML += '</off:Property>';
                    updatedXML += '<off:Property>';
                       updatedXML += '<off:Name>VALUE</off:Name>';
                       updatedXML += '<off:Values>';
                          updatedXML += '<off:Value>5000</off:Value>';
                        updatedXML += '</off:Values>';
                     updatedXML += '</off:Property>';
                    updatedXML += '<off:Property>';
                       updatedXML += '<off:Name>FOR_EVERY</off:Name>';
                       updatedXML += '<off:Values>';
                          updatedXML += '<off:Value>2</off:Value>';
                        updatedXML += '</off:Values>';
                     updatedXML += '</off:Property>';
                  updatedXML += '</off:ActionProperty>';
                 updatedXML += '<off:ActionProperty PropertyType="Cap">';
                     updatedXML += '<!--off:Property>';
                       updatedXML += '<off:Name>OFFER_TIMES_CAP</off:Name>';
                       updatedXML += '<off:Values>';
                          updatedXML += '<off:Value>2</off:Value>';
                        updatedXML += '</off:Values>';
                     updatedXML += '</off:Property-->';
                    updatedXML += '<off:Property>';
                       updatedXML += '<off:Name>MEMBER_TIMES_CAP</off:Name>';
                       updatedXML += '<off:Values>';
                          updatedXML += '<off:Value>1</off:Value>';
                        updatedXML += '</off:Values>';
                     updatedXML += '</off:Property>';
                     updatedXML += '<!--off:Property>';
                       updatedXML += '<off:Name>STORE_TIMES_CAP</off:Name>';
                       updatedXML += '<off:Values>';
                         updatedXML += '<off:Value>5</off:Value>';
                        updatedXML += '</off:Values>';
                     updatedXML += '</off:Property>';
                    updatedXML += '<off:Property>';
                       updatedXML += '<off:Name>OFFER_POINTS_CAP</off:Name>';
                       updatedXML += '<off:Values>';
                          updatedXML += '<off:Value>10000</off:Value>';
                        updatedXML += '</off:Values>';
                     updatedXML += '</off:Property-->';
                     updatedXML += '<!--off:Property>';
                       updatedXML += '<off:Name>STORE_POINTS_CAP</off:Name>';
                       updatedXML += '<off:Values>';
                          updatedXML += '<off:Value>15000</off:Value>';
                        updatedXML += '</off:Values>';
                     updatedXML += '</off:Property-->';
                     updatedXML += '<!--off:Property>';
                       updatedXML += '<off:Name>MEMBER_POINTS_CAP</off:Name>';
                       updatedXML += '<off:Values>';
                          updatedXML += '<off:Value>10000</off:Value>';
                        updatedXML += '</off:Values>';
                     updatedXML += '</off:Property-->';
                  updatedXML += '</off:ActionProperty>';
               updatedXML += '</off:ActionProperties>';
            updatedXML += '</off:Action>';
         updatedXML += '</off:Actions>';
        updatedXML += '<off:RealTimeFlag>N</off:RealTimeFlag>';
      updatedXML += '</off:CreateUpdateOffer>';
   updatedXML += '</soap:Body>';
updatedXML += '</soap:Envelope>';

		 return updatedXML;
  },
  checkMandatory: function(selector){
		var flag1 =false;
			$('#'+selector+' .mandatory').each(function(){	
				if($(this).val()=="" ||$(this).val()===undefined)
				{
					$(this).addClass("error");
					$(".alert").show();
					$(".alert").html("Highlighted fields are mandatory!");
					flag1 = true;
				}
				else
				{
				$(this).removeClass("error");
				}
			});
			if(flag1)
			{
				return false;
			}
			else
			{
				return true;
			}
	}
};

   