var Scripts = {
  Constructor: function() {
    this.init = Scripts.init;
	this.createXmlform = Scripts.createXmlform;
	this.checkMandatory = Scripts.checkMandatory;
  },

  init: function() {
	  var that = this;
	  $("#createOffer").on('click',function(event){
		  event.preventDefault();
		  if(that.checkMandatory('offerForm')){
		   $.ajax({
			  url: exposedApi.baseurl+"createOffer",
			  contentType:'text/plain',
			  type: 'POST',
			  dataType:'application/json',
			  data: that.createXmlform(),
			  success: function(data){
				var result = JSON.parse(data.responseText);
					result = $.parseXML(result.data);
					var statusText = $(result).find('StatusText').text();
					var status = $(result).find('Status').text();
						alert(statusText) 
			  },
			  error: function(data){
					var result = JSON.parse(data.responseText);
					result = $.parseXML(result.data);
					var statusText = $(result).find('StatusText').text();
					var status = $(result).find('Status').text();
						alert(statusText)
					
			  }
			  
		})
		}
	  })

  },

  createXmlform : function(){
	  var xml = '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:off="http://rewards.sears.com/schemas/offer/" xmlns:sch="http://rewards.sears.com/schemas/">';
	  xml += '<soap:Header></soap:Header><soap:Body><off:CreateUpdateOffer><sch:MessageVersion>01</sch:MessageVersion><sch:RequestorID>OFRP</sch:RequestorID><sch:Source>TI</sch:Source><off:OfferNumber>NUMB</off:OfferNumber>';

     xml += '<off:OfferPointsDollarName>'+$("#OfferPointsDollarName").val()+'</off:OfferPointsDollarName>';
     xml += '<off:OfferDescription>'+$("#OfferDescription").val()+'</off:OfferDescription>';
     xml += '<off:OfferType>'+$("#OfferType").val()+'</off:OfferType>';
     xml += '<off:OfferSubType>'+$("#OfferSubType").val()+'</off:OfferSubType>';
		 xml += '<off:OfferStartDate>'+$("#OfferStartDate").val()+'</off:OfferStartDate>';
     xml += '<off:OfferStartTime>00:00:00</off:OfferStartTime>';
     xml += '<off:OfferEndDate>'+$("#OfferEndDate").val()+'</off:OfferEndDate>';
     xml += '<off:OfferEndTime>23:59:00</off:OfferEndTime>';
		 xml += '<off:OfferBUProgram><off:BUProgram><off:BUProgramName>BU-Apparel</off:BUProgramName><off:BUProgramCost>0.00</off:BUProgramCost></off:BUProgram></off:OfferBUProgram>';
     xml += '<off:ReceiptDescription>TELL-16289</off:ReceiptDescription>';
     xml += '<off:OfferCategory>Stackable</off:OfferCategory>';
     xml += '<off:ExpenseAllocation>Noallocation–ChargealltoWH</off:ExpenseAllocation>';
     xml += '<off:ModifiedBy>nand</off:ModifiedBy>';
     xml += '<off:ModifiedTS>2014-06-2510:40:00</off:ModifiedTS>';
     xml += '<off:OfferAttributes>';
     xml +=    '<off:OfferAttribute><off:Name>MULTI_TRAN_IND</off:Name><off:Values><off:Value>N</off:Value></off:Values></off:OfferAttribute>';
     xml += '</off:OfferAttributes>';
     xml +=  '<off:Rules>';
      xml +=      '<off:Rule Entity="Location">';
      xml +=         '<off:Conditions>';
      xml +=            '<off:Condition>';
      xml +=             '<off:Name>STORE_LOCATION</off:Name>';
      xml +=             '<off:Operator>EQUALS</off:Operator>';
      xml +=             '<off:Values>';
      xml +=                '<off:Value>OrderLocation</off:Value>';
      xml +=          '</off:Values>';
      xml +=         '</off:Condition>';
      xml +=   '</off:Conditions>';
          xml +=  '</off:Rule>';
          xml +=  '<off:RuleActions>';
          xml +=     '<off:ActionID>ACTION-1</off:ActionID>';
          xml +=  '</off:RuleActions>';
        xml += '</off:Rules>';
        xml += '<off:Actions>';
          xml +=  '<off:Action ActionID="ACTION-1" ActionName="EARN">';
          xml +=     '<off:ActionProperties>';
            xml +=      '<off:ActionProperty PropertyType="Tier">';
              xml +=       '<off:Property>';
              xml +=          '<off:Name>MIN</off:Name>';
              xml +=          '<off:Values>';
              xml +=             '<off:Value>1</off:Value>';
                xml +=        '</off:Values>';
                xml +=     '</off:Property>';
                xml +=     '<off:Property>';
                xml +=        '<off:Name>MAX</off:Name>';
                xml +=        '<off:Values>';
                xml +=           '<off:Value>6</off:Value>';
                xml +=        '</off:Values>';
                xml +=     '</off:Property>';
                xml +=     '<off:Property>';
                xml +=        '<off:Name>VALUE</off:Name>';
                xml +=        '<off:Values>';
                xml +=           '<off:Value>5000</off:Value>';
                xml +=        '</off:Values>';
                xml +=     '</off:Property>';
                xml +=     '<off:Property>';
                xml +=        '<off:Name>FOR_EVERY</off:Name>';
                xml +=        '<off:Values>';
                xml +=           '<off:Value>2</off:Value>';
                xml +=        '</off:Values>';
                xml +=     '</off:Property>';
                xml +=  '</off:ActionProperty>';
                xml += '</off:ActionProperties>';
          xml +=  '</off:Action>';
         xml +='</off:Actions>';
         xml +='<off:RealTimeFlag>N</off:RealTimeFlag>';
    xml +=  '</off:CreateUpdateOffer>';
   xml +='</soap:Body>';
xml +='</soap:Envelope>';

		 return xml;
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
