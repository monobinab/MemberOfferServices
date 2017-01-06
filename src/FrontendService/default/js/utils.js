//This js file contains all the required utils across the application.

//Util to check for all mandatory fields

function checkMandatory(selector){
  var flag1 =false;
    $('#'+selector+' .activate .mandatory').each(function(){
      if(($(this).val()=="" ||$(this).val()===undefined ||$(this).val()==null))
      {
        $(this).val('');
        $(this).addClass("error");
        $(this).siblings(".ui-multiselect").addClass("error");
        $(".alert").show();
        $(".alert").html("Highlighted fields are mandatory!");
        flag1 = true;
      }
      else
      {
      $(this).removeClass("error");
      $(this).siblings(".ui-multiselect").removeClass("error");
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
};

//Util to do validations for comparing min and max values against eah other and also boundary conditions for  the input fields
function validations(element,comparand,operation){

  /*Method to validate the current input element with comparand. operation specifies the type of comparison.*/
      var flag = true;
      $(".alert").empty();
      $(".alert").hide();
        var val = parseInt($(element).val().replace(/,/g,'').replace("\u0024", ""));
        var min = parseInt($(element).attr('min'));
        var max = parseInt($(element).attr('max'));
        var comparandValue =  parseInt($(comparand).val().replace(/,/g,'').replace("\u0024", ""));

        if(isNaN(val)){
          $(".alert").show();
          $(".alert").html("Please enter valid number in "+$(element).attr('name'));
          flag = false;
        }
         else if($(element).attr('min') && $(element).attr('max')){
          if(!(val >= min && val <=  max)){
            $(".alert").show();
            $(".alert").html("Please enter value in range of "+ min+" - "+max+" for the "+$(element).attr('name') +".");
            flag = false;
          }

          if(operation ==0)// 0 specifies that the value of element should be less than the comparand value
          {
              if(comparandValue && (val > comparandValue))
              {
                $(".alert").show();
                $(".alert").html( "Mimimum value should be lesser than the maximum value i.e "+ comparandValue+" in this case.");
                flag = false;
              }
          }
          else if(operation ==1)	//	1 specifies that the value of element should be more than the comparand value
          {
              if(comparandValue && (val < comparandValue))
              {
                $(".alert").show();
                $(".alert").html("Maximum value should be greater than the minimum value i.e "+ comparandValue+" in this case.");
                flag = false;
              }
          }

        }
        return flag;
};

//Util to check for positive currency value
function positiveCurrency(element){

    $(".alert").empty();
    $(".alert").hide();
    var val = parseFloat($(element).val().replace(/,/g,'').replace("\u0024", "")-0);

    if(val<=0){
      $(".alert").show();
      $(".alert").html("Please enter valid currency in "+$(element).attr('name'));
      $(element).val("");
    }
    else{
      $(element).val(val);
    }

};


//Date validations

 function dateValidation(element) {
   var dateFlag = true;
    $(".alert").empty();
    $(".alert").hide();
    var enteredDate = new Date($(element).val());
    enteredDate = enteredDate.getTime();
    var start = new Date();
    start = start.setHours(0,0,0,0);
    if(!isNaN(enteredDate)){
      if (enteredDate >= start) {
        dateFlag = true;
        $(element).removeClass("error1");
      }
      else {
        dateFlag = false;
        $(element).addClass("error1");
        $(".alert").show();
        $(".alert").html("Please enter the date greater than today");
      }
    }
    else{
      dateFlag = false;
      $(".alert").show();
      $(element).addClass("error1");
      $(".alert").html("Please enter date format as follows YYYY-MM-DD");
    }
    return dateFlag;
};

function lengthValidation(element)
{
  var lengthFlag =true;
  $(element).parent().find(".lenWarning").remove();
  if($(element).val().length>$(element).attr("maxlen"))
  {
    $(element).addClass("error1");
    $(element).parent().append("<span class ='lenWarning' style='font-size:11.5px;color:red;'>Max length allowed is "+$(element).attr("maxlen")+" characters.</span>")
    lengthFlag = false;
  }
  else
  {
    $(element).removeClass("error1");
    $(element).parent().find(".lenWarning").remove();
    lengthFlag = true;
  }
  return lengthFlag;
};
